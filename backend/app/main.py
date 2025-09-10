"""
python -m app.main
API route 功能

有一任務，從 MQTT 訂閱資料 → 放入記憶體佇列 → 批次進入到資料庫
"""
import asyncio
import uuid
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logger import get_logger
from app.core.db import engine
from app.core.mqtt_service import mqtt_service
# import model 才會被 Base.metadata 掃到，create table 
from app.features.auth.model import Users
from app.features.auth import router as auth_router
from app.features.partition import router as partition_router
from app.features.di.router import router as di_router
from app.features.ai import router as ai_router
from app.features.ai_datatype_list import router as ai_datatype_router
from app.features.shapes_name import router as shapes_name_router
from app.features.elements import router as elements_router
from app.features.elements_shapes import router as elements_shapes_router
from app.features.ai_objects_text import router as ai_objects_text_router
from app.features.views import router as views_router
from app.features.view_shapes import router as view_shapes_router
from app.features.view_shapes_1 import router as view_shapes_1_router
from app.features.view_shapes_2 import router as view_shapes_2_router
from app.features.view_shapes_3 import router as view_shapes_3_router
from app.features.sdi import router as sdi_router
from app.features.functions_operator import router as fo_router
from app.features.functions_formula import router as ff_router
from app.features.functions_list import router as fl_router
from app.features.functions_point import router as fp_router
from app.features.views_menu_main import router as menu_main_router
from app.features.views_menu_side import router as menu_side_router
from app.features.views_menu_buttons import router as menu_btns_router
from app.features.mqtt_hmi_mx.router import router as mqtt_mx_router
from app.features.mqtt_hmi_st.router import router as mqtt_st_router
from app.features.view_objs_partion_list.router import router as view_partition_list_router
from app.features.multi_point import router as multi_point_router



logger = get_logger("power-system-hmi-backend")
cfg = settings()

# ───────────────────────────────────────────────────────────
# 靜態檔案掛載（可能：目錄不存在/權限問題）
# ───────────────────────────────────────────────────────────

try:
    app = FastAPI(title="power-system-hmi", version="1.0.0",debug=True) # 建立後端伺服器
    # 掛載靜態檔案 圖片
    app.mount(
        cfg.image_url_prefix,  # URL 前綴
        StaticFiles(directory=cfg.image_dir),  
        name="images"
    )
    # 再掛一個 Vue 靜態資源（例如 /frontend）
    app.mount(cfg.vue_url_prefix, StaticFiles(directory=cfg.vue_dir, html=True), name="frontend")

    logger.info(f"Mounted static files at prefix={cfg.image_url_prefix}, dir={cfg.image_dir}")
    logger.info(f"Mounted static files at prefix={cfg.vue_url_prefix}, dir={cfg.vue_dir}")
except Exception:
    # 若無法掛載，不中斷整個服務（依需求也可 raise）
    logger.exception("掛載 StaticFiles 失敗")


# CORS（通常不會拋例外，但保險包起來）
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],#["http://127.0.0.1:1880","http://127.0.0.1:1234"],  # Vue 的開發伺服器
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception:
    logger.exception("設定 CORS Middleware 失敗")


# ───────────────────────────────────────────────────────────
# 請求 Middleware：記錄 request/response 與未攔截例外
# ───────────────────────────────────────────────────────────
@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = req_id
    start = time.perf_counter()
    try:
        logger.info(f"[REQ] id={req_id} {request.method} {request.url.path} q={request.url.query or ''}")
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"[RES] id={req_id} {request.method} {request.url.path} -> {response.status_code} {elapsed_ms}ms")
        response.headers["X-Request-ID"] = req_id
        return response
    except Exception:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(f"[ERR] id={req_id} {request.method} {request.url.path} 未攔截例外，耗時 {elapsed_ms}ms")
        return JSONResponse(
            status_code=500,
            content={"detail": "伺服器內部錯誤", "request_id": req_id},
            headers={"X-Request-ID": req_id},
        )
    

# ───────────────────────────────────────────────────────────
# 路由註冊（這裡一般不會拋例外；若擔心也可包 try/except）
# ───────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(partition_router, prefix=cfg.api_prefix)
app.include_router(di_router, prefix=cfg.api_prefix)
app.include_router(ai_router, prefix=cfg.api_prefix)
app.include_router(ai_datatype_router, prefix=cfg.api_prefix)
app.include_router(shapes_name_router, prefix=cfg.api_prefix)
app.include_router(elements_router, prefix=cfg.api_prefix)
app.include_router(elements_shapes_router, prefix=cfg.api_prefix)
app.include_router(ai_objects_text_router, prefix=cfg.api_prefix)
app.include_router(views_router, prefix=cfg.api_prefix)
app.include_router(view_shapes_router, prefix=cfg.api_prefix)
app.include_router(view_shapes_1_router, prefix=cfg.api_prefix)
app.include_router(view_shapes_2_router, prefix=cfg.api_prefix)
app.include_router(view_shapes_3_router, prefix=cfg.api_prefix)
app.include_router(sdi_router, prefix=cfg.api_prefix)
app.include_router(fo_router, prefix=cfg.api_prefix)
app.include_router(ff_router, prefix=cfg.api_prefix)
app.include_router(fl_router, prefix=cfg.api_prefix)
app.include_router(fp_router, prefix=cfg.api_prefix)
app.include_router(menu_main_router, prefix=cfg.api_prefix)
app.include_router(menu_side_router, prefix=cfg.api_prefix)
app.include_router(menu_btns_router, prefix=cfg.api_prefix)
app.include_router(mqtt_mx_router, prefix=cfg.api_prefix)
app.include_router(mqtt_st_router, prefix=cfg.api_prefix)
app.include_router(view_partition_list_router, prefix=cfg.api_prefix)
app.include_router(multi_point_router)




# ───────────────────────────────────────────────────────────
# 啟動事件
# ───────────────────────────────────────────────────────────

# @app.on_event("startup")
# async def on_startup():
#     # mssql全部，都建好 table
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    # 只針對 users table 建表
    try:
        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Users.__table__.create(
                    bind=sync_conn, checkfirst=True
                )
            )
        logger.info("Users 資料表建立/檢查完成")
    except Exception:
        logger.exception("啟動時建立 Users 資料表失敗")
        raise # 終止啟動

    # 啟動 MQTT 背景服務
    try:
        task = asyncio.create_task(mqtt_service.run())
        # 可選：task callback 監控 task 內未處理例外
        def _cb(t: asyncio.Task):
            try:
                exc = t.exception()
                if exc:
                    logger.exception("MQTT 背景任務異常終止", exc_info=exc)
            except asyncio.CancelledError:
                # 正常關閉
                pass
            except Exception:
                logger.exception("MQTT 背景任務 callback 讀取例外失敗")
        task.add_done_callback(_cb)
        logger.info("MQTT 背景服務啟動")        
    except Exception:
        logger.exception("啟動 MQTT 背景服務失敗")        
        raise # 終止啟動

# ───────────────────────────────────────────────────────────
# 關閉事件
# ───────────────────────────────────────────────────────────

@app.on_event("shutdown")
async def on_shutdown():
    """關閉連線"""
    # 結束資料庫
    try:
        await engine.dispose()
        logger.info("資料庫連線已關閉")
    except Exception:
        logger.exception("關閉資料庫連線失敗")

    # 結束 MQTT
    try:
        await mqtt_service.stop()
        logger.info("MQTT 背景服務已停止")
    except Exception:
        logger.exception("停止 MQTT 背景服務失敗")

    logger.info("Backend 已停止")



# ───────────────────────────────────────────────────────────
# 全域 Exception Handler
# ───────────────────────────────────────────────────────────

# 錯誤 400
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    req_id = getattr(request.state, "request_id", None)
    logger.info(f"[ValidationError] id={req_id} path={request.url.path} errors={exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "request_id": req_id},
        headers={"X-Request-ID": req_id or ""},
    )

# 錯誤 500
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", None)
    logger.exception(f"[Unhandled] id={req_id} path={request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "伺服器內部錯誤", "request_id": req_id},
        headers={"X-Request-ID": req_id or ""},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
