# backend/app/core/logger.py
"""
紀錄 log，自動 rotate
統一全域 logger，Console + File log，Rotating，每個 module 都能 import 用

——— 用法 ———
from core.logger import get_logger
logger = get_logger(__name__) 
try:    
    print(1/0)
except Exception:
    logger.exception("Error occurred")
"""
import logging
# import inspect
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = Path(BASE_DIR/"datas"/"logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


# Log 顯示格式
_fmt = "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"


class LineFormatter(logging.Formatter):
    """
    遇到 exception 自動補上完整 traceback
    純出錯沒except，直接顯示上層錯誤
    Ex: 2024-04-15 13:00:23 | INFO     | api.py:25 | 成功建立連線
    """
    def format(self, record: logging.LogRecord) -> str:
        if record.exc_info:
            tb = traceback.extract_tb(record.exc_info[2])
            if tb:
                last = tb[-1]
                record.filename = Path(*Path(last.filename).parts[-2:])
                record.lineno = last.lineno
        return super().format(record)

def _handler(factory):
    h = factory()
    h.setFormatter(LineFormatter(_fmt))
    return h


# 主 logger 建立函數（可多次調用）
def get_logger(name: Optional[str] = None):
    logger = logging.getLogger(name)
    logger.propagate = False  # 防止重複往上傳
    if not logger.handlers:  # 避免重複加 handler
        logger.setLevel("INFO") #INFO
        logger.addHandler(_handler(logging.StreamHandler))  # console
        logger.addHandler(_handler(lambda: RotatingFileHandler( # file rotate
            LOG_DIR / f"{name}.log", maxBytes=10_000_000, backupCount=3, encoding="utf-8"
        )))
    return logger

