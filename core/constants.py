"""Application constants and enums."""

from enum import Enum


class ContentType(str, Enum):
    """Content types for analysis."""

    REQUIREMENT = "requirement"
    TEST_CASE = "test_case"
    USER_STORY = "user_story"
    GENERAL = "general"


class AnalysisLevel(str, Enum):
    """Analysis levels."""

    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


class AnalysisStatus(str, Enum):
    """Analysis status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PII_TYPE(str, Enum):
    """PII types for sanitization."""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    URL = "url"
    API_KEY = "api_key"
    PASSWORD = "password"
    JWT_TOKEN = "jwt_token"
    NAME = "name"
    ADDRESS = "address"


# API Configuration
API_V1_PREFIX = "/api/v1"
DEFAULT_TIMEOUT = 300
MAX_RETRIES = 3
BACKOFF_MAX_TIME = 60

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_BURST = 10

# LLM Configuration
DEFAULT_LLM_MODEL = "gemini-pro"
DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 8192

# Logging
LOG_FORMAT = "json"
LOG_LEVEL_DEFAULT = "INFO"

# Security
API_KEY_HEADER = "X-API-Key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS
CORS_ALLOW_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
