from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent.parent

BACKEND_DIR = Path(__file__).parent.parent.parent


class Db_Config(BaseModel):
    """Настройки базы данных"""
    url: str


class Paginate_Config(BaseModel):
    page_size: int = 6

class CORS_Config(BaseModel):
    """Настройки CORS"""
    allow_credentials: bool = True
    allow_origins: list[str] = ['*']
    allow_methods: list[str] = ['*']
    allow_headers: list[str] = ['*']

class Access_Token(BaseModel):
    """Настройки токена"""
    lifetime_seconds: int = 3600
    verification_token_secret: str
    reset_password_token_secret: str

class App_Config(BaseModel):
    """Настройки приложения"""
    debug: bool = False
    host: str = '0.0.0.0'
    port: int = 8000
    reload: bool = False

class Settings(BaseSettings):
    """Базовые настройки"""
    app: App_Config = App_Config()
    cors: CORS_Config = CORS_Config()
    db: Db_Config
    access_token: Access_Token
    pagination: Paginate_Config = Paginate_Config()

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / '.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        env_nested_delimiter='__',
        extra='ignore',
    )

settings = Settings()# type: ignore
