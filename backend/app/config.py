from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    indic_en_model: str = "ai4bharat/indictrans2-indic-en-dist-200M"
    en_indic_model: str = "ai4bharat/indictrans2-en-indic-dist-200M"
    model_device: str = "auto"
    model_max_length: int = 256
    model_num_beams: int = 5
    asr_provider: str = "mock"
    asr_model_id: str = "small"
    asr_device: str = "cpu"
    asr_compute_type: str = "int8"
    gemini_api_key: str | None = None
    tts_provider: str = "none"
    database_url: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
