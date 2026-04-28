from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./engrow.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    reset_token_expire_minutes: int = 60

    frontend_origin: str = "http://localhost:3000"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@engrow.app"

    backup_dir: str = "./backups"
    backup_interval_hours: int = 6

    superadmin_email: str = "admin@engrow.app"
    superadmin_password: str = "change-me-now"
    admin_secret_key: str = "admin-secret-change-me"


settings = Settings()
