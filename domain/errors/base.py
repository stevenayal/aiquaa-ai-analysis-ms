"""Base domain exceptions."""

from typing import Any, Optional


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        details: Optional[Any] = None,
    ):
        """Initialize domain error.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class ValidationError(DomainError):
    """Validation error."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class NotFoundError(DomainError):
    """Resource not found error."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code="NOT_FOUND", details=details)


class ConfigurationError(DomainError):
    """Configuration error."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)


class ExternalServiceError(DomainError):
    """External service error."""

    def __init__(self, message: str, service: str, details: Optional[Any] = None):
        self.service = service
        super().__init__(
            message,
            code="EXTERNAL_SERVICE_ERROR",
            details={**(details or {}), "service": service},
        )


class RateLimitError(DomainError):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Any] = None):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", details=details)


class AuthenticationError(DomainError):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(DomainError):
    """Authorization error."""

    def __init__(self, message: str = "Authorization failed", details: Optional[Any] = None):
        super().__init__(message, code="AUTHORIZATION_ERROR", details=details)
