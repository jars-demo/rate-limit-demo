"""What every limiter returns, and the one method they all share."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Decision:
    allowed: bool
    remaining: int
    # Seconds until this key could pass again. 0 when the request was allowed.
    retry_after: float


class Limiter(Protocol):
    name: str
    limit: int

    def allow(self, key: str, now: float) -> Decision: ...


class Unlimited:
    """No limit at all: where chapter 01 starts."""

    name = "none"

    def __init__(self, limit: int = 0, window: float = 1.0) -> None:
        self.limit = limit

    def allow(self, key: str, now: float) -> Decision:
        return Decision(True, self.limit, 0.0)
