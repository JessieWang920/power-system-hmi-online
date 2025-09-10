"""
供 main.py 匯入

不加這行時，main.py 要這樣寫：
    from app.api.v1.partition.router import router as partition_router
如果在 partition/__init__.py 裡加了：
    from .router import router
就能簡化為：
    from app.api.v1.partition import router as partition_router
"""

from .router import router   
