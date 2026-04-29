from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_STATE_DIR = ROOT_DIR / "artifacts" / "local"
DEFAULT_DB_PATH = DEFAULT_STATE_DIR / "autotrain.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    autotrain_env: str = Field(default="local", alias="AUTOTRAIN_ENV")
    app_name: str = "autotrain-api"
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    database_url: str = Field(
        default=f"sqlite:///{DEFAULT_DB_PATH}",
        alias="DATABASE_URL",
    )
    mistral_api_key: str | None = Field(default=None, alias="MISTRAL_API_KEY")


settings = Settings()
