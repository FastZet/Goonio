from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    """
    Pydantic model for application settings.
    It automatically reads settings from a .env file or environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Addon Settings ---
    ADDON_ID: str = "org.goonio.adult"
    ADDON_NAME: str = "Goonio"
    ADDON_VERSION: str = "0.1.0"
    ADDON_DESCRIPTION: str = "Stremio's finest adult catalog and stream provider."
    ADDON_LOGO: str = "https://i.imgur.com/83942T5.png" # Example logo, can be changed
    ADDON_BACKGROUND: str = "https://i.imgur.com/WwnXB3k.jpeg" # Example background

    # --- Server Settings ---
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

# Create a single instance of the settings to be used throughout the application
settings = AppSettings()
