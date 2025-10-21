from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    API_PREFIX: str = ""
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    OIDC_CONFIG_URL: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_DEFAULT_REGION: str | None = None
    AWS_BEDROCK_KNOWLEDGE_BASE_ID: str | None = None
    AWS_BEDROCK_MODEL_ARN: str | None = None


settings = Settings()
