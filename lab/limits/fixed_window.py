from .core import Decision


class FixedWindow:
    """At most `limit` requests per key in each window. Windows start at 0, 1, 2... seconds."""

    name = "fixed-window"

    def __init__(self, limit: int, window: float = 1.0) -> None:
        self.limit = limit
        self.window = window
        self._counts: dict[str, tuple[int, int]] = {}  # key -> (window number, count)

    def allow(self, key: str, now: float) -> Decision:
        current = int(now // self.window)
        number, count = self._counts.get(key, (current, 0))
        if number != current:
            count = 0  # a new window: the count starts again
        if count >= self.limit:
            return Decision(False, 0, (current + 1) * self.window - now)
        self._counts[key] = (current, count + 1)
        return Decision(True, self.limit - count - 1, 0.0)
