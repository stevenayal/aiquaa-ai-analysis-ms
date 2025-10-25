"""Langfuse client for LLM observability."""

from typing import Optional, Any, Dict
import structlog
from langfuse import Langfuse

from core.config import get_settings

logger = structlog.get_logger(__name__)


class LangfuseClient:
    """Langfuse client for LLM observability and tracing."""

    def __init__(self):
        """Initialize Langfuse client."""
        settings = get_settings()

        self.enabled = settings.langfuse_configured
        self.client: Optional[Langfuse] = None

        if self.enabled:
            try:
                self.client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host
                )
                logger.info("Langfuse client initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Langfuse client", error=str(e))
                self.enabled = False
                self.client = None
        else:
            logger.warning("Langfuse not configured - observability disabled")

    async def health_check(self) -> bool:
        """Check Langfuse connection health.

        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self.enabled or not self.client:
                logger.info("Langfuse not configured - skipping health check")
                return True

            # Test basic connection
            self.client.flush()
            logger.info("Langfuse health check successful")
            return True
        except Exception as e:
            logger.error("Langfuse health check failed", error=str(e))
            return False

    def trace(self, name: str, user_id: Optional[str] = None, **kwargs) -> Any:
        """Create a new trace.

        Args:
            name: Trace name
            user_id: Optional user ID
            **kwargs: Additional trace parameters

        Returns:
            Trace object or None if disabled
        """
        if not self.enabled or not self.client:
            return None

        try:
            return self.client.trace(name=name, user_id=user_id, **kwargs)
        except Exception as e:
            logger.error("Failed to create trace", error=str(e), trace_name=name)
            return None

    def flush(self) -> None:
        """Flush pending Langfuse data."""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error("Failed to flush Langfuse data", error=str(e))
