# backend/app/core/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from .config import settings
from collections.abc import AsyncGenerator
from .logger import get_logger

Base = declarative_base()
logger = get_logger("power-system-hmi-backend")


def _url() -> str:
    try:
        s = settings()
        # ODBC Driver 名稱中的空格要用 + 轉義
        driver = s.mssql_driver.replace(" ", "+")
        return (
            f"mssql+aioodbc://{s.mssql_user}:{s.mssql_password}"
            f"@{s.mssql_host}:{s.mssql_port}/{s.mssql_db}"
            f"?driver={driver}&TrustServerCertificate=yes&MARS_Connection=Yes"
        )
    except Exception:
        logger.exception("產生 MSSQL 連線字串失敗")
        raise  # 中止，這會導致 create_engine() crash


# 建立 engine / session 時，若失敗會立刻報錯
try:
    engine = create_async_engine(_url(), pool_pre_ping=True, echo=False) # echo 可開啟除錯
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    logger.info("成功建立 async MSSQL engine 與 session factory")
except Exception:
    logger.exception("初始化資料庫 engine/session 失敗")
    raise



# FastAPI 依賴
async def get_db()  -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 使用的依賴注入：取得 DB session，結束後自動關閉連線
    """
    try:
        async with SessionLocal() as session:
            logger.debug("DB session 開啟")
            yield session
            logger.debug("DB session yield 完成")
    except Exception:
        logger.exception("使用 get_db() 時發生錯誤")
        raise