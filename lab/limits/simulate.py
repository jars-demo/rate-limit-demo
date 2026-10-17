"""Replay a traffic pattern against a limiter with a fake clock. No server, no waiting."""

from dataclasses import dataclass

from .core import Limiter

# Request times in seconds. Each pattern shows one thing a limiter has to get right.
PATTERNS: dict[str, list[float]] = {
    # 20 requests in 0.2 seconds, right across the edge between two windows.
    "edge": [round(0.90 + i * 0.01, 2) for i in range(20)],
    # 20 requests per second for 3 seconds: twice the limit, all day.
    "steady": [round(i * 0.05, 2) for i in range(60)],
    # 30 requests at once, then one per second.
    "burst": [0.0] * 30 + [float(second) for second in range(1, 6)],
}


@dataclass(frozen=True)
class Result:
    allowed: list[float]
    rejected: int

    def worst_window(self, window: float = 1.0) -> int:
        """The most allowed requests inside any `window` seconds: what your backend really sees."""
        times, worst, start = sorted(self.allowed), 0, 0
        for end, t in enumerate(times):
            # Rounded, so 1.15 - 1.0 counts as 0.15 and not 0.1499999.
            while times[start] <= round(t - window, 9):
                start += 1
            worst = max(worst, end - start + 1)
        return worst


def simulate(limiter: Limiter, times: list[float], key: str = "demo") -> Result:
    allowed, rejected = [], 0
    for t in times:
        if limiter.allow(key, t).allowed:
            allowed.append(t)
        else:
            rejected += 1
    return Result(allowed, rejected)
