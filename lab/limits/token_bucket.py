from .core import Decision


class TokenBucket:
    """Each key has a bucket of `burst` tokens that refills at `limit` tokens per `window`.

    A request takes one token. Bursts up to `burst` are allowed on purpose; over time the
    average rate can never beat the refill rate.
    """

    name = "token-bucket"

    def __init__(self, limit: int, window: float = 1.0, burst: int | None = None) -> None:
        self.limit = limit
        self.rate = limit / window  # tokens per second
        self.capacity = burst if burst is not None else limit
        self._buckets: dict[str, tuple[float, float]] = {}  # key -> (tokens, last seen)

    def allow(self, key: str, now: float) -> Decision:
        tokens, last = self._buckets.get(key, (float(self.capacity), now))
        tokens = min(self.capacity, tokens + (now - last) * self.rate)
        if tokens < 1:
            self._buckets[key] = (tokens, now)
            return Decision(False, 0, (1 - tokens) / self.rate)
        tokens -= 1
        self._buckets[key] = (tokens, now)
        return Decision(True, int(tokens), 0.0)
