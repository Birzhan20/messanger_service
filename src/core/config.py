from pydantic_settings import BaseSettings
from pydantic import ConfigDict, AnyHttpUrl

class Settings(BaseSettings):
    GROK_API_URL: str = ""
    GROK_API_KEY: str | None = None
    SUPPORT_PROMPT_PATH: str = "./prompts.docx"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    DATABASE_URL: str = "sqlite:///tests.db"

    POCKETBASE_URL: str
    POCKETBASE_ADMIN_EMAIL: str
    POCKETBASE_ADMIN_PASSWORD: str
    POCKETBASE_COLLECTION: str
    POCKETBASE_FIELD_NAME: str

    model_config = ConfigDict(
        env_file=".env",
        extra="allow",
    )

settings = Settings()