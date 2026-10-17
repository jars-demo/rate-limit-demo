import threading
import urllib.error
import urllib.request

import pytest

from limits import FixedWindow, Unlimited
from limits.client import Response, backoff, call_with_retry, get
from limits.hammer import hammer
from limits.server import make_server


@pytest.fixture
def serve():
    servers = []

    def start(limiter):
        # A frozen clock: every request lands in the same instant, so counts are exact.
        server = make_server(limiter, port=0, clock=lambda: 100.5)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        return f"http://127.0.0.1:{server.server_port}"

    yield start
    for server in servers:
        server.shutdown()
        server.server_close()


def test_the_server_answers_429_with_retry_after_and_ratelimit_headers(serve):
    url = serve(FixedWindow(limit=1)) + "/api/hello"
    assert get(url, "k").status == 200

    request = urllib.request.Request(url, headers={"X-Api-Key": "k"})
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(request, timeout=5)

    assert error.value.code == 429
    assert error.value.headers["Retry-After"] == "1"
    assert error.value.headers["RateLimit-Limit"] == "1"
    assert error.value.headers["RateLimit-Remaining"] == "0"


def test_the_server_limits_each_api_key_separately(serve):
    url = serve(FixedWindow(limit=1)) + "/api/hello"

    assert [get(url, key).status for key in ("a", "a", "b")] == [200, 429, 200]


def test_health_is_never_limited(serve):
    base = serve(FixedWindow(limit=1))

    assert [get(base + "/health", "k").status for _ in range(3)] == [200, 200, 200]


def test_hammer_counts_every_answer(serve):
    url = serve(FixedWindow(limit=5)) + "/api/hello"

    assert hammer(url, requests=12, concurrency=4) == {200: 5, 429: 7}


def test_without_a_limiter_every_request_gets_through(serve):
    url = serve(Unlimited()) + "/api/hello"

    assert hammer(url, requests=12, concurrency=4) == {200: 12}


def test_call_with_retry_waits_for_retry_after_then_succeeds():
    answers = iter([Response(429, 2.0), Response(200, None)])
    waits = []

    response = call_with_retry(lambda: next(answers), sleep=waits.append, rng=lambda: 0.5)

    assert response.status == 200
    assert waits == [2.05]


def test_call_with_retry_backs_off_when_there_is_no_retry_after():
    waits = []

    response = call_with_retry(
        lambda: Response(503, None), attempts=4, sleep=waits.append, rng=lambda: 1.0
    )

    assert response.status == 503
    assert waits == pytest.approx([0.1, 0.2, 0.4])


def test_call_with_retry_does_not_retry_other_errors():
    calls = []

    def send():
        calls.append(1)
        return Response(500, None)

    assert call_with_retry(send, sleep=lambda _: None).status == 500
    assert len(calls) == 1


def test_backoff_never_waits_longer_than_the_cap():
    assert backoff(attempt=10, base=0.1, cap=2.0, rng=lambda: 1.0) == 2.0
