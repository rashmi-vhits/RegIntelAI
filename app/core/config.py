from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "RegIntel AI Backend"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./regintel.db"
    upload_dir: str = "./storage/uploads"
    anonymized_dir: str = "./storage/anonymized"
    export_dir: str = "./storage/exports"
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_temperature: float = 0.1
    ollama_timeout: float = 8.0
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
print("#.")
settings = get_settings()