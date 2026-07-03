from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "rental_shop.db"

    # AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "https://therentalshop.vercel.app",
        "https://the-rental-shop.onrender.com",
        "*",  # Temporary - allow all origins for debugging
    ]

    # Security - Generate a strong random key if not provided in .env
    secret_key: str | None = None
    rate_limit_window: int = 60
    rate_limit_max_requests: int = 100
    csrf_enabled: bool = False  # Disabled for demo
    jwt_enabled: bool = False  # Disabled for demo

    def __init__(self, **data):
        super().__init__(**data)
        # If secret_key is not set, generate one at runtime
        if not self.secret_key or self.secret_key in (
            "",
            "your-secret-key-change-in-production",
            "dev-key-never-use-in-production-change-in-env",
        ):
            if os.environ.get("ENVIRONMENT") == "production":
                raise ValueError(
                    "SECRET_KEY must be set in .env for production environment. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            # Generate a random key for each session in development
            self.secret_key = secrets.token_urlsafe(32)


settings = Settings()
