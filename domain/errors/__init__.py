"""Domain errors and exceptions."""

from .base import (
    DomainError,
    ValidationError,
    NotFoundError,
    ConfigurationError,
    ExternalServiceError,
    RateLimitError,
    AuthenticationError,
    AuthorizationError,
)

__all__ = [
    "DomainError",
    "ValidationError",
    "NotFoundError",
    "ConfigurationError",
    "ExternalServiceError",
    "RateLimitError",
    "AuthenticationError",
    "AuthorizationError",
]
