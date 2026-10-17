"""Send many requests at once and count the answers."""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from .client import call_with_retry, get


def hammer(
    url: str, requests: int = 40, concurrency: int = 8, key: str = "demo", retry: bool = False
) -> Counter[int]:
    def one(_: int) -> int:
        if retry:
            return call_with_retry(lambda: get(url, key)).status
        return get(url, key).status

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        return Counter(pool.map(one, range(requests)))
