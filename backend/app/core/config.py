# backend/app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path
from pydantic import model_validator
import sys
# BASE_DIR = Path(__file__).resolve().parents[2]
BASE_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parents[2]

class Settings(BaseSettings):

    # ───── App ─────
    api_prefix: str = "/SCADA"

    # ───── MSSQL ─────
    mssql_driver: str
    mssql_host: str
    mssql_port: int = 1433
    mssql_user: str
    mssql_password: str
    mssql_db: str

    # ───── MQTT ─────
    mqtt_host: str
    mqtt_port: int = 1883
    mqtt_topic: str                 # ex: "Topic/#"
    batch_interval: int = 1         # flush 秒數

    # ───── JWT ─────    
    jwt_secret_key: str = "Jessie"
    jwt_algorithm: str = "HS256"
    token_expire_min: int = 60 * 24
    
    # ───── 其他 ─────
    allowed_ips: str = "127.0.0.1"
    image_dir: Path
    image_url_prefix:str

    vue_dir:Path
    vue_url_prefix:str

    partition_list_path: Path
    

    model_config = SettingsConfigDict(
        env_file=str( BASE_DIR / "config" / ".env"),
        env_file_encoding = "utf-8"
     )
    


    @model_validator(mode="after")
    def _print_env_flag(self):
         # 非絕對路徑，加上 BASE_DIR
        if not self.image_dir.is_absolute():
            self.image_dir = BASE_DIR.parent / self.image_dir

        if not self.partition_list_path.is_absolute():
            self.partition_list_path = BASE_DIR.parent / self.partition_list_path
        
        if not self.vue_dir.is_absolute():
            self.vue_dir = BASE_DIR.parent / self.vue_dir
        
        return self


@lru_cache
def settings() -> Settings:
    """
    整個程式都用同一份設定物件。
    回傳要符合 Settings 的格式
    """
    return Settings()

if __name__ == "__main__":
    print(settings().batch_interval)
    print(settings().mqtt_host)