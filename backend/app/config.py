from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    elevenlabs_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./spam_baiter.db"
    audio_files_dir: str = str(Path(__file__).resolve().parent.parent / "audio_files")
    soundboard_dir: str = str(
        Path(__file__).resolve().parent.parent.parent / "scammer_soundboard"
    )
    phone_bridge: Literal["mock", "bluetooth"] = "mock"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
