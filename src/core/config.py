from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROK_API_URL: str
    GROK_API_KEY: str | None = None
    SUPPORT_PROMPT_PATH: str = "./support_prompt.docs"

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
