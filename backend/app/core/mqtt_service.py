import asyncio
import json
from typing import Dict, List
from aiomqtt import Client, MqttError   # ← 基於 paho 的 async 套件

from .config import settings
from .logger import get_logger
from .db import SessionLocal
from app.features.mqtt_hmi_st.model import MqttHmiSt
from app.features.mqtt_hmi_mx.model import MqttHmiMx
from app.features.mqtt_svr.crud import MqttCrud

logger = get_logger("power-system-hmi-backend")
cfg = settings()

class MqttService:
    """
    1. 連線 MQTT、訂閱 Topic
    2. 收到訊息放進 asyncio.Queue
    3. 背景 Task 每 N 秒 flush -> 批次寫入 MSSQL
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Dict] = asyncio.Queue(maxsize=100_000)
        self._flush_interval = cfg.batch_interval
        self._consumer_task: asyncio.Task | None = None
        self._client: Client | None = None
        self._running = asyncio.Event()
        self._put_timeout = 5  # queue 滿時最多等 5 秒，避免無限卡住

    # ---------- Public API ----------
    async def run(self) -> None:
        """在 FastAPI startup 時呼叫；維持整個服務生命週期"""
        self._running.set()

        # 啟動 consumer 背景任務
        try:
            self._consumer_task = asyncio.create_task(self._consumer_loop(), name="mqtt_consumer")
        except Exception:
            logger.exception("建立 consumer 背景任務失敗")
            raise
        
        # 連線 MQTT 與訂閱
        try:
            async with Client(cfg.mqtt_host, cfg.mqtt_port) as client:
                self._client = client
                try:
                    await client.subscribe(cfg.mqtt_topic, qos=1)
                    logger.info(f"MQTT 已連線 {cfg.mqtt_host}:{cfg.mqtt_port} / 訂閱 {cfg.mqtt_topic}")
                except Exception:
                    logger.exception(f"訂閱 Topic 失敗: {cfg.mqtt_topic}")
                    raise
                
                # 讀取訊息主迴圈                
                async for message in client.messages:
                    try:
                        # await self._queue.put(message.payload) # queue 雙向背壓；滿了就會在這卡住，避免失控佔記憶體
                        # queue 雙向背壓：滿了就會在這裡暫停（最多 _put_timeout 秒）
                        await asyncio.wait_for(self._queue.put(message.payload), timeout=self._put_timeout)
                    except asyncio.TimeoutError:
                        logger.warning("佇列已滿，放入訊息超時，訊息被丟棄")
                    except Exception:
                        logger.exception("放入佇列失敗，訊息被丟棄")
        except MqttError as e:
            logger.exception(f"MQTT 連線/收訊錯誤: {e}")
        except asyncio.CancelledError:
            # 服務停止時的正常流程
            logger.info("MQTT run() 收到取消訊號，準備關閉")
            raise
        except Exception:
            logger.exception("MQTT 主迴圈發生未預期的錯誤")
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """在 FastAPI shutdown 時呼叫"""
        self._running.clear()

        # 關閉 MQTT client（若還在）
        try:
            if self._client is not None:
                # aiomqtt.Client 是 async context manager，離開 with 會自動處理
                self._client = None
        except Exception:
            logger.exception("關閉 MQTT client 失敗")

        # 停 consumer
        try:
            if self._consumer_task and not self._consumer_task.done():
                self._consumer_task.cancel()
                try:
                    await self._consumer_task
                except asyncio.CancelledError:
                    pass
                except Exception:
                    logger.exception("等待 consumer 任務結束時發生錯誤")
        finally:
            self._consumer_task = None
            logger.info("MQTT 服務已停止")

    # ---------- Background Consumer ----------
    async def _consumer_loop(self) -> None:
        """
        1. 每 batch_interval 秒或 queue 為空時就 flush
        2. MX / ST 分開累積 → 同張表批次寫入
        """
        logger.info("MQTT Consumer 迴圈啟動")
        try:
            while self._running.is_set():
                try:
                    # 等 batch_interval 秒，或有第一筆訊息時立即醒來
                    await asyncio.sleep(self._flush_interval)

                    msgs: List[bytes] = []
                    while not self._queue.empty():
                        try:
                            msgs.append(self._queue.get_nowait())
                        except asyncio.QueueEmpty:
                            break

                    if not msgs:
                        continue

                    mx_rows, st_rows = self._parse_messages(msgs)
                    total = len(mx_rows) + len(st_rows)
                    # logger.info(f"Flush 批次：{total} 筆 (MX={len(mx_rows)}, ST={len(st_rows)})")

                    # --- 寫入 DB ---
                    try:
                        async with SessionLocal() as db:
                            if mx_rows:
                                await MqttCrud.bulk_replace(db, MqttHmiMx, mx_rows)
                            if st_rows:
                                await MqttCrud.bulk_replace(db, MqttHmiSt, st_rows)
                    except Exception:
                        logger.exception("批次寫入資料庫失敗")
                        # 不中斷 consumer；本批次遺失，繼續下一輪

                except asyncio.CancelledError:
                    logger.info("Consumer 收到取消訊號，準備退出")
                    raise
                except Exception:
                    logger.exception("Consumer loop error")
        
        finally:
            # 退出前如還有殘留資料，可視需求做最後 flush（這裡選擇記錄訊息）
            pending = self._queue.qsize()
            if pending:
                logger.warning(f"Consumer 結束時仍有 {pending} 筆訊息尚未處理")

    # ---------- Helper ----------
    @staticmethod
    def _parse_messages(msgs: List[bytes]):
        mx_rows: List[dict] = []
        st_rows: List[dict] = []

        for raw in msgs:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("收到非 JSON 訊息，已跳過")
                continue
            except Exception:
                logger.exception("解析訊息 JSON 時發生未知錯誤，已跳過")
                continue

            # Node-RED 那邊同時可能是一筆或多筆
            if not isinstance(payload, list):
                payload = [payload]

            for p in payload:
                try:
                    typ = p.get("Type")
                    content = p.get("Content", {})
                    row = dict(
                        tag_name=content.get("TagName", "").strip(),
                        value=content.get("Value"),
                        time=content.get("Time"),
                        quality=content.get("Quality"),
                    )

                    if typ == "MX":
                        mx_rows.append(row)
                    elif typ == "ST":
                        st_rows.append(row)
                    elif typ == "MXA":
                        continue  # 忽略 MXA 訊息
                    else:
                        logger.warning(f"未知 Type，已跳過：{typ}")
                except Exception:
                    logger.exception(f"解析單筆 payload 失敗，payload={p}")
                    continue

        return mx_rows, st_rows


# 建立單例給 main.py 用
mqtt_service = MqttService()
