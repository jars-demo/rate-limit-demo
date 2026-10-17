"""Rate limiters from scratch, standard library only."""

from .core import Decision, Limiter, Unlimited
from .fixed_window import FixedWindow
from .sliding_log import SlidingLog
from .token_bucket import TokenBucket

LIMITERS = {
    "none": Unlimited,
    "fixed-window": FixedWindow,
    "sliding-log": SlidingLog,
    "token-bucket": TokenBucket,
}


def make(name: str, limit: int, window: float = 1.0) -> Limiter:
    if name not in LIMITERS:
        raise ValueError(f"unknown limiter {name!r}, pick one of: {', '.join(LIMITERS)}")
    return LIMITERS[name](limit, window)


__all__ = ["LIMITERS", "Decision", "FixedWindow", "Limiter", "SlidingLog", "TokenBucket", "make"]
