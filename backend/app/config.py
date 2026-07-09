from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库类型 (sqlite 或 mysql)
    DB_TYPE: str = "sqlite"
    
    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "ai_qa_db"

    # JWT
    JWT_SECRET: str = "ai-qa-python-secret-key-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # 大模型API（通义千问 DashScope OpenAI兼容接口）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen-turbo"

    # Embedding模型
    EMBEDDING_MODEL: str = "text-embedding-v2"

    # 文件上传
    UPLOAD_DIR: str = "/data/uploads"

    # ChromaDB
    CHROMA_DIR: str = "/data/chroma"

    class Config:
        env_file = ".env"


settings = Settings()
