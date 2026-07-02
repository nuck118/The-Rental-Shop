from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "rental_shop.db"

    # AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    rate_limit_window: int = 60
    rate_limit_max_requests: int = 100
    csrf_enabled: bool = True
    jwt_enabled: bool = True


settings = Settings()
