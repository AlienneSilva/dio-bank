from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Aplicação
    PROJECT_NAME: str = "DIO Bank API"
    DEBUG: bool = False

    # Banco de Dados
    DATABASE_URL: str = "sqlite+aiosqlite:///bank.db"

    # Segurança e JWT
    SECRET_KEY: str = "super_chave_secreta_padrao_para_desenvolvimento_local"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
