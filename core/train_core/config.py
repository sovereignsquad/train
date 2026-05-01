import os
import platform
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR_NAME = "train"
SOURCE_ROOT_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = Path(os.environ.get("TRAIN_ROOT_DIR", str(SOURCE_ROOT_DIR))).resolve()


def get_default_state_dir() -> Path:
    system = platform.system()
    home = Path.home()

    if system == "Darwin":
        return home / "Library" / "Application Support" / APP_DIR_NAME
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / APP_DIR_NAME
        return home / "AppData" / "Roaming" / APP_DIR_NAME

    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    if xdg_state_home:
        return Path(xdg_state_home) / APP_DIR_NAME
    return home / ".local" / "state" / APP_DIR_NAME


DEFAULT_STATE_DIR = Path(
    os.environ.get("TRAIN_STATE_DIR", str(get_default_state_dir()))
).resolve()
DEFAULT_DB_PATH = DEFAULT_STATE_DIR / "train.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    train_env: str = Field(default="local", alias="TRAIN_ENV")
    app_name: str = "train-api"
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    database_url: str = Field(
        default=f"sqlite:///{DEFAULT_DB_PATH}",
        alias="DATABASE_URL",
    )
    mistral_api_key: str | None = Field(default=None, alias="MISTRAL_API_KEY")
    mistral_api_base_url: str = Field(default="https://api.mistral.ai", alias="MISTRAL_API_BASE_URL")
    mistral_vibe_executable: str = Field(default="vibe", alias="MISTRAL_VIBE_EXECUTABLE")
    mistral_vibe_agent_name: str = Field(default="train", alias="MISTRAL_VIBE_AGENT_NAME")
    mistral_vibe_home: str = Field(
        default=str(DEFAULT_STATE_DIR / "vibe-home"),
        alias="MISTRAL_VIBE_HOME",
    )
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    operator_lease_grace_seconds: int = Field(default=30, alias="OPERATOR_LEASE_GRACE_SECONDS")


settings = Settings()
