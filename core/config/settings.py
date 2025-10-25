"""Application settings with Pydantic v2."""

from functools import lru_cache
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="AIQUAA AI Analysis MS", alias="APP_NAME")
    app_version: str = Field(default="v1", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    # Google Gemini AI
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-pro", alias="GEMINI_MODEL")

    # Langfuse (Observability)
    langfuse_public_key: Optional[str] = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", alias="LANGFUSE_HOST")
    langfuse_enabled: bool = Field(default=True, alias="LANGFUSE_ENABLED")

    # Jira Integration
    jira_base_url: Optional[str] = Field(default=None, alias="JIRA_BASE_URL")
    jira_email: Optional[str] = Field(default=None, alias="JIRA_EMAIL")
    jira_token: Optional[str] = Field(default=None, alias="JIRA_TOKEN")
    jira_timeout: int = Field(default=30, alias="JIRA_TIMEOUT")

    # Feature Flags
    use_spanish_params: bool = Field(default=False, alias="USE_SPANISH_PARAMS")
    enable_pii_sanitization: bool = Field(default=True, alias="ENABLE_PII_SANITIZATION")
    enable_rate_limiting: bool = Field(default=True, alias="ENABLE_RATE_LIMITING")

    # Security
    api_key_header: str = Field(default="X-API-Key", alias="API_KEY_HEADER")
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    allowed_api_keys: list[str] = Field(default_factory=list, alias="ALLOWED_API_KEYS")

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # Redis (for caching/rate limiting)
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")

    # OpenTelemetry
    otel_exporter_otlp_endpoint: Optional[str] = Field(default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    otel_service_name: str = Field(default="aiquaa-ai-analysis-ms", alias="OTEL_SERVICE_NAME")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("allowed_api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        """Parse API keys from string or list."""
        if isinstance(v, str):
            return [key.strip() for key in v.split(",") if key.strip()]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"

    @property
    def langfuse_configured(self) -> bool:
        """Check if Langfuse is configured."""
        return bool(
            self.langfuse_enabled
            and self.langfuse_public_key
            and self.langfuse_secret_key
        )

    @property
    def jira_configured(self) -> bool:
        """Check if Jira is configured."""
        return bool(
            self.jira_base_url
            and self.jira_email
            and self.jira_token
        )

    @property
    def gemini_configured(self) -> bool:
        """Check if Gemini AI is configured."""
        return bool(self.google_api_key)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
