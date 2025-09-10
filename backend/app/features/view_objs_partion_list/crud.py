import json
from aiofiles import open as aioopen
from pathlib import Path
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)
_cfg = settings()

class ViewObjCRUD:
    """
    目前僅寫入 JSON 檔；若日後改存 MSSQL，
    只需把 write() 換成 SQL 即可，router 不用動
    """
    @classmethod
    async def write(cls,tags: list[str]) -> list[str]:
        # 確保父目錄存在
        json_path: Path = _cfg.partition_list_path
        json_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aioopen(json_path, mode="w", encoding="utf-8") as f:
                await f.write(json.dumps(tags, ensure_ascii=False, indent=2))
            logger.info(f"寫入 PartitionList：{len(tags)} rows → {json_path}")
            return tags  
        except Exception:
            logger.exception("寫入 PartitionList 失敗")
            raise
