from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for SPARKS.
    """

    app_name: str = "SPARKS"
    environment: str = "development"
    debug: bool = True

    log_level: str = "INFO"

    model_provider: str = "ollama"

    database_url: str = (
        "postgresql+psycopg://sparks:sparks@localhost:5432/sparks"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return the shared application settings instance.
    """
    return Settings()