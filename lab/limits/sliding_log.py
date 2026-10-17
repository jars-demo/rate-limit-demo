from collections import defaultdict, deque

from .core import Decision


class SlidingLog:
    """At most `limit` requests per key in ANY window of `window` seconds.

    Exact, at the cost of remembering one timestamp per allowed request.
    """

    name = "sliding-log"

    def __init__(self, limit: int, window: float = 1.0) -> None:
        self.limit = limit
        self.window = window
        self._log: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float) -> Decision:
        log = self._log[key]
        while log and log[0] <= now - self.window:
            log.popleft()  # older than one window: no longer counts
        if len(log) >= self.limit:
            return Decision(False, 0, log[0] + self.window - now)
        log.append(now)
        return Decision(True, self.limit - len(log), 0.0)
