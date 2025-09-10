# gateway/src/services/mqtt_service.py
"""
使用 aiomqtt 的非同步 MQTT 服務
- 自帶重連 (with client as ...)
- 支援 QoS 1/2 (預設 QoS 1)
- subscriber only

"""
import asyncio,json,orjson
from logging import Logger
from aiomqtt import Client, MqttError
from multiprocessing import  Queue
from aioprocessing import AioQueue

from shared.utils.config import Settings
from gateway.src.core.mapping import IECMapping
from gateway.src.core.payload_parser import PayloadParser


class MQTTService:
    def __init__(self, cfg : Settings, opcua_queue: AioQueue ,mapping: IECMapping, logger:Logger,client_id: str):
        self.cfg = cfg        
        self._opcua_queue = opcua_queue # output
        self.mapping = mapping 
        self.log = logger
        self.client_id = client_id

        self.initial_event = asyncio.Event()
        self.parser = PayloadParser(self.mapping) 
        # 內部用，呼叫端只 enqueue，不阻塞，用於 publish
        self._queue: asyncio.Queue[tuple[str, bytes]] = asyncio.Queue(maxsize=100_000)

        # aiomqtt 連線實例 & 重連間隔
        self._client: Client | None = None
        self._reconnect_interval = 3  # 秒

        self._process_sema = asyncio.Semaphore(4)

    async def start(self) -> None:
        """
        失連後自動重連，重連成功才 set initial_event。
        """
        attempts = 0
        while True:
            try:
                async with Client(
                    hostname=self.cfg.broker,
                    port=self.cfg.mqtt_port,
                    identifier=self.client_id,
                    keepalive=20,
                    clean_session=True,
                    max_inflight_messages = 20_000,                    
                )as c:
                    self._client = c
                    
                    # 訂閱主題
                    await c.subscribe((self.cfg.mqtt_topic, 1))  # QoS 1
                    # 首次成功連線
                    if not self.initial_event.is_set():
                        self.initial_event.set()
                        self.log.info(
                            f"MQTT connected & subscribed {self.cfg.mqtt_topic}"
                        )

                    # asyncio.create_task(self._sender_loop()) # pub 用

                    async def on_message(payload_bytes):
                        # 限流
                        async with self._process_sema:
                            try:
                                msg = orjson.loads(payload_bytes)
                            except json.JSONDecodeError:
                                self.log.error("Failed to decode MQTT payload as JSON")
                                return

                            if msg.get("IECPath") in ("path_test_7000","path_test_1000","path_test_6000","path_test_5000"):
                                print(f"MQTT message sent: {msg}")     
                            # DO 排除       
                            if msg.get("SBO") or  msg.get("Status"):
                                # self.log.info(f"SBO message received: {msg}")
                                return

                            payload = self.parser._parse_dev(msg)
                            if payload:
                                dv = self.mapping.to_opcua_datavalue(
                                    payload.tag, payload.value, payload.ts,
                                    payload.qual, datatype=payload.data_type
                                )
                                try:
                                    self._opcua_queue.put_nowait((payload.tag, dv))  # 丟給 subprocess
                                except Queue.full:
                                    self.log.warning("OPC UA subprocess queue full – dropped message")

                    # 非阻塞地把每條 message.payload 丟到 byte_queue
                    async for msg in c.messages:
                        asyncio.create_task(on_message(msg.payload))


            except MqttError as e:
                attempts += 1
                delay = min(60, self._reconnect_interval * (2 ** attempts)) # 減少頻繁重連的影響
                self.log.warning(
                    f"MQTT disconnected: {e!r} – reconnect in {self._reconnect_interval}s"
                )
                self.initial_event.clear()
                # await asyncio.sleep(self._reconnect_interval)
                try:
                    await asyncio.sleep(delay)
                except asyncio.CancelledError:
                    break
                
            finally:
                await self.stop()
                # if self._client:
                #     try:
                #         await self._client.disconnect()
                #     except Exception:
                #         pass
                # self._client = None



    async def stop(self):       
        """關閉 MQTT 連線"""
        if self._client:
            try:
                await self._client.disconnect()
            except Exception:
                pass
        self._client = None

    async def publish(
            self,
            topic: str,
            payload: dict | str,
            qos: int = 1,
        ) -> None:
        """
        供其他服務呼叫的非同步 publish，無批次處理
        """
        if self._client is None:
            self.log.warning("Publish skipped – MQTT not connected")
            return

        body = payload
        if isinstance(payload, (dict, list)):
            body = json.dumps(payload)

        try:
            await self._client.publish(topic, body, qos=qos, retain=False)
        except MqttError as e:
            self.log.error(f"Publish failed: {e!r}")

    # def enqueue(self, topic: str, payload: dict | str):
    #     """提供其他協程將資料放入_queue，來做後續的 批次 publish，完全非阻塞"""
    #     body: bytes
    #     if isinstance(payload, (dict, list)):
    #         body = orjson.dumps(payload)
    #     elif isinstance(payload, str):
    #         body = payload.encode()
    #     else:
    #         raise TypeError("payload must be dataclass / dict / str")

    #     try:
    #         self._queue.put_nowait((topic, body))
    #     except asyncio.QueueFull:
    #         # 如果OPCUA 壞掉 也會full
    #         self.log.warning("IEC MQTT out-queue full – drop message") 

    # async def _sender_loop(self):
    #     """背景送訊息來，批次publish """
    #     BATCH = 200               # 每批最多 200 筆
    #     QOS   = 1                 # QoS 0 ➜ 最低延遲；要保證就改 1
    #     TIMEOUT = 0.005            # 5 ms 沒湊滿也直接 flush

    #     client = self._client  # 區域變數抓一次，快一點
    #     while True:
    #         topic, body = await self._queue.get()
    #         batch = [(topic, body)]

    #         while len(batch) < BATCH:
    #             try:
    #                 # 20 ms 內沒新資料就提早送
    #                 batch.append(
    #                     await asyncio.wait_for(self._queue.get(), timeout=TIMEOUT)
    #                 )
    #             except asyncio.TimeoutError:
    #                 break

    #         # 併發 publish；等待 socket flush 但一次就把 BATCH 筆送出去
    #         await asyncio.gather(*[
    #             client.publish(t, b, qos=QOS, retain=False)
    #             for t, b in batch
    #         ])




