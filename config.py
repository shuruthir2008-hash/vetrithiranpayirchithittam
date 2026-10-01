from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    llm_provider: str = "gemini"
    image_provider: str = "diffusers"

    gemini_api_key: str = ""
    gemini_outline_model: str = "gemini-2.5-flash"
    gemini_story_model: str = "gemini-2.5-pro"

    hf_token: str = ""
    sd_model_id: str = "runwayml/stable-diffusion-v1-5"
    torch_device: str = "auto"
    sd_steps: int = Field(default=25, ge=1, le=100)
    sd_guidance_scale: float = Field(default=7.5, ge=1.0, le=30.0)
    image_width: int = Field(default=512, ge=256, le=1024)
    image_height: int = Field(default=512, ge=256, le=1024)

    panel_count: int = Field(default=5, ge=1, le=10)
    max_story_prompt_length: int = Field(default=2000, ge=100, le=10000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "templates"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
