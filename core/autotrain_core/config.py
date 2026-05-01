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
    mistral_api_base_url: str = Field(default="https://api.mistral.ai", alias="MISTRAL_API_BASE_URL")
    mistral_vibe_executable: str = Field(default="vibe", alias="MISTRAL_VIBE_EXECUTABLE")
    mistral_vibe_agent_name: str = Field(default="autotrain", alias="MISTRAL_VIBE_AGENT_NAME")
    mistral_vibe_home: str = Field(
        default=str(DEFAULT_STATE_DIR / "vibe-home"),
        alias="MISTRAL_VIBE_HOME",
    )
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    operator_lease_grace_seconds: int = Field(default=30, alias="OPERATOR_LEASE_GRACE_SECONDS")


settings = Settings()
