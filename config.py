"""
應用程式配置模組

使用 pydantic-settings 進行環境變數驗證和配置管理。
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """應用程式設定"""
    
    # 伺服器設定
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS 設定
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # 上傳限制
    MAX_UPLOAD_SIZE_MB: float = 10.0
    
    # 圖片處理預設值
    DEFAULT_TARGET_SIZE_MB: float = 2.0
    DEFAULT_MIN_SIZE_MB: float = 0.0
    DEFAULT_TARGET_RATIO: float = 16 / 9
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全域設定實例
settings = Settings()
