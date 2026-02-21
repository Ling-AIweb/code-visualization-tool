"""
应用配置
从 .env 文件或环境变量读取配置项。
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用全局配置"""

    # LLM API 配置（支持 OpenAI 兼容接口）
    API_KEY: str = ""
    API_BASE: str = "https://api.openai.com/v1"
    MODEL_NAME: str = "gpt-4"

    # 向量数据库配置
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS 配置（逗号分隔的来源列表）
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # 文件上传配置
    MAX_UPLOAD_SIZE_MB: int = 500

    @property
    def cors_origins_list(self) -> List[str]:
        """将逗号分隔的 CORS_ORIGINS 字符串转为列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        """将 MB 转换为字节"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
