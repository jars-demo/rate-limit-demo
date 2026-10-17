"""A tiny HTTP API with a rate limiter in front of it. Standard library only."""

import json
import math
import threading
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .core import Limiter


class LimitedServer(ThreadingHTTPServer):
    def __init__(self, port: int, limiter: Limiter, clock: Callable[[], float]) -> None:
        super().__init__(("127.0.0.1", port), Handler)
        self.limiter = limiter
        self.clock = clock
        # Requests arrive on many threads; the limiter's counters must change one at a time.
        self.lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server: LimitedServer

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, {"ok": True})  # never limited: load balancers poll this
            return
        if self.path != "/api/hello":
            self._send(404, {"error": "not_found"})
            return

        # Who is asking: the API key when there is one, otherwise the client's address.
        key = self.headers.get("X-Api-Key") or self.client_address[0]
        with self.server.lock:
            decision = self.server.limiter.allow(key, self.server.clock())

        headers = {
            "RateLimit-Limit": str(self.server.limiter.limit),
            "RateLimit-Remaining": str(decision.remaining),
        }
        if decision.allowed:
            self._send(200, {"message": "hello", "key": key}, headers)
        else:
            # Whole seconds, rounded up, so a client that waits this long will get through.
            headers["Retry-After"] = str(math.ceil(decision.retry_after))
            self._send(429, {"error": "rate_limited", "retry_after": decision.retry_after}, headers)

    def _send(self, status: int, body: dict, headers: dict[str, str] | None = None) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        pass  # a hammer run sends hundreds of requests; keep the terminal readable


def make_server(
    limiter: Limiter, port: int = 8000, clock: Callable[[], float] = time.monotonic
) -> LimitedServer:
    return LimitedServer(port, limiter, clock)
