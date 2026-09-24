from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = (
        "development"  # Altere para "production" quando for para deploy
    )

    # SQLite para desenvolvimento local
    DEV_DATABASE_URL: str = "sqlite+aiosqlite:///./dio_bank.db"

    # PostgreSQL para produção (lido do .env de produção)
    PROD_DATABASE_URL: str = ""

    SECRET_KEY: str = "sua_chave_secreta_jwt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def database_url(self) -> str:
        if self.ENVIRONMENT == "production" and self.PROD_DATABASE_URL:
            return self.PROD_DATABASE_URL
        return self.DEV_DATABASE_URL

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
