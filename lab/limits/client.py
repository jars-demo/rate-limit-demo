"""Calling a rate-limited API politely: back off, add jitter, respect Retry-After."""

import random
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

RETRY_STATUSES = (429, 503)


@dataclass(frozen=True)
class Response:
    status: int
    retry_after: float | None  # seconds, from the Retry-After header


def get(url: str, key: str, timeout: float = 5) -> Response:
    request = urllib.request.Request(url, headers={"X-Api-Key": key})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return Response(response.status, None)
    except urllib.error.HTTPError as error:
        header = error.headers.get("Retry-After")
        return Response(error.code, float(header) if header else None)


def backoff(attempt: int, base: float = 0.1, cap: float = 2.0, rng=random.random) -> float:
    """Full jitter: a random wait between 0 and base * 2^attempt, never more than cap."""
    return rng() * min(cap, base * 2**attempt)


def call_with_retry(
    send: Callable[[], Response],
    attempts: int = 5,
    base: float = 0.1,
    cap: float = 2.0,
    sleep: Callable[[float], None] = time.sleep,
    rng=random.random,
) -> Response:
    for attempt in range(attempts):
        response = send()
        if response.status not in RETRY_STATUSES or attempt == attempts - 1:
            return response
        if response.retry_after is not None:
            # The server said when. Add a little jitter so every client does not return at once.
            sleep(response.retry_after + rng() * base)
        else:
            sleep(backoff(attempt, base, cap, rng))
    raise AssertionError("unreachable")
