from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    direm_env: str = Field(default="local", alias="DIREM_ENV")
    direm_version: str = Field(default="0.1.0", alias="DIREM_VERSION")
    direm_commit_sha: str = Field(default="unknown", alias="DIREM_COMMIT_SHA")
    direm_build_date: str = Field(default="unknown", alias="DIREM_BUILD_DATE")

    telegram_bot_token: SecretStr = Field(default=SecretStr("replace_me"), alias="TELEGRAM_BOT_TOKEN")

    postgres_db: str = Field(default="direm", alias="POSTGRES_DB")
    postgres_user: str = Field(default="direm", alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(default=SecretStr("direm"), alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="db", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    database_url: str = Field(
        default="postgresql+asyncpg://direm:direm@db:5432/direm",
        alias="DATABASE_URL",
    )

    worker_poll_seconds: int = Field(default=10, alias="WORKER_POLL_SECONDS")
    worker_batch_size: int = Field(default=20, alias="WORKER_BATCH_SIZE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("telegram_bot_token")
    @classmethod
    def token_must_be_set(cls, value: SecretStr) -> SecretStr:
        token = value.get_secret_value()
        if not token or token == "replace_me":
            return value
        return value

    def require_bot_token(self) -> str:
        token = self.telegram_bot_token.get_secret_value()
        if not token or token == "replace_me":
            raise RuntimeError("TELEGRAM_BOT_TOKEN must be set before starting the bot.")
        return token


@lru_cache
def get_settings() -> Settings:
    return Settings()
