from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Muller's Firearms API"
    APP_ENV: str = "development"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://weapon_store:weapon_store@localhost:5432/weapon_store"
    SQL_ECHO: bool = False

    SECRET_KEY: str = "local-development-key-change-before-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    GIGACHAT_AUTH_KEY: str | None = None
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"
    GIGACHAT_MODEL: str = "GigaChat-2"
    GIGACHAT_AUTH_URL: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    GIGACHAT_API_URL: str = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    GIGACHAT_VERIFY_SSL: bool = True

    SEED_DEMO_DATA: bool = False
    DEMO_ADMIN_EMAIL: str = "admin@mullers.local"
    DEMO_ADMIN_PASSWORD: str = "ChangeMe123!"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_secrets(self):
        unsafe_secrets = {
            "local-development-key-change-before-production",
            "replace-with-a-long-random-value",
        }
        if self.APP_ENV.lower() == "production":
            if self.SECRET_KEY in unsafe_secrets:
                raise ValueError("SECRET_KEY must be changed in production")
            if self.SEED_DEMO_DATA and self.DEMO_ADMIN_PASSWORD == "ChangeMe123!":
                raise ValueError("DEMO_ADMIN_PASSWORD must be changed in production")
        return self


settings = Settings()
