"""Shared abstract base for every agent: a uniform run() contract plus a
retry helper, so retry/backoff logic isn't duplicated in each agent."""
import time
from abc import ABC, abstractmethod
from typing import Callable, TypeVar

from app.utils.logger import get_logger

T = TypeVar("T")


class BaseAgent(ABC):
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def run(self, *args, **kwargs):
        """Every agent implements its own run() signature; this just
        establishes the convention that agents expose a single run()
        entry point rather than several loosely-related public methods."""
        raise NotImplementedError

    def with_retry(self, func: Callable[[], T], max_attempts: int, backoff_seconds: float = 2.0,
                    retry_on: tuple = (Exception,)) -> T:
        last_exc: Exception = None
        for attempt in range(1, max_attempts + 1):
            try:
                return func()
            except retry_on as exc:  # noqa: BLE001 - caller narrows via retry_on
                last_exc = exc
                self.logger.warning(
                    "%s attempt %d/%d failed: %s", self.__class__.__name__, attempt, max_attempts, exc
                )
                if attempt < max_attempts:
                    time.sleep(backoff_seconds * attempt)
        raise last_exc