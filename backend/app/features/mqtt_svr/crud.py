from typing import Sequence
from sqlalchemy import insert 
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import get_logger
from datetime import datetime, timezone
from typing import Sequence, Mapping
from sqlalchemy import text, bindparam, insert

logger = get_logger(__name__)

class MqttCrud:

    @staticmethod
    async def bulk_replace(
        db: AsyncSession,
        table,                    # e.g. models.TagCache
        rows: Sequence[Mapping],  # [{'tag_name': 'A', 'tag_value': '1'}, ...]
    ) -> None:
        """
        # FIXME: 在修正 資料庫 叢集 與使用 UPSERT
        批次插入資料；若有相同 tag 改變 value/quality 才寫入。
        這邊直接用 SQLAlchemy Core + executemany 提升效能。
        """

        if not rows:
            return

        # 1) Python 端先把同名 tag 去重，保留「最後來的」
        dedup = {r["tag_name"]: r for r in rows}.values()

        # 2) 把 tag 名字拉出來做 where in (:names)
        tag_names = [r["tag_name"] for r in dedup]

        delete_sql = text(f"""
            DELETE FROM {table.__tablename__}
            WHERE tag_name IN :names
        """).bindparams(bindparam("names", expanding=True))

        # 3) 同一個 transaction 先刪後插
        async with db.begin():
            await db.execute(delete_sql, {"names": tag_names})
            # 填入 updated_at，若你表裡有這欄位
            now = datetime.now(timezone.utc)
            for r in dedup:
                r.setdefault("updated_at", now)

            await db.execute(insert(table), list(dedup))

        # logger.info("TagCache REPLACE %s rows", len(dedup))