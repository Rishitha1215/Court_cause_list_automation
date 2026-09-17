"""
Custom exception hierarchy.

Agents raise these instead of bare exceptions so the Orchestrator can
catch specific, expected failure modes (and log/retry accordingly) while
letting truly unexpected errors propagate and surface loudly.
"""


class AppError(Exception):
    """Base class for all application-specific exceptions."""


# --- Agent-layer failures (expected, recoverable) ---

class AgentError(AppError):
    """Base class for errors raised by any agent."""


class NavigationError(AgentError):
    """Raised when the Navigator agent cannot reach or parse the court site."""


class CaptchaSolveError(AgentError):
    """Raised when the CAPTCHA solver exhausts its retries."""


class ExtractionError(AgentError):
    """Raised when the Extractor agent cannot parse the cause list page."""


class NotificationDeliveryError(AgentError):
    """Raised when the Notifier agent fails to send an email."""


# --- Service/API-layer failures ---

class AuthenticationError(AppError):
    """Raised on invalid credentials or expired/invalid tokens."""


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""


class DuplicateEntityError(AppError):
    """Raised when attempting to create an entity that already exists."""