from pydantic_settings import BaseSettings
from pydantic import ConfigDict, AnyUrl

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

    S3_ENDPOINT: AnyUrl
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str
    S3_REGION: str = "us-east-1"

    @property
    def S3_URL(self) -> str:
        return f"{str(self.S3_ENDPOINT).rstrip('/')}/{self.S3_BUCKET}"

    model_config = ConfigDict(
        env_file=".env",
        extra="allow",
    )

settings = Settings()