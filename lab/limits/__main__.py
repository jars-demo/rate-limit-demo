"""python -m limits simulate | serve | hammer"""

import argparse
import contextlib
import sys
import time

from . import LIMITERS, make
from .hammer import hammer
from .server import make_server
from .simulate import PATTERNS, simulate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m limits")
    commands = parser.add_subparsers(dest="command", required=True)

    sim = commands.add_parser("simulate", help="replay a traffic pattern with a fake clock")
    sim.add_argument("--pattern", choices=PATTERNS, default="edge")
    sim.add_argument("--limit", type=int, default=10, help="requests per second")

    srv = commands.add_parser("serve", help="run the API with a limiter in front")
    srv.add_argument("--limiter", choices=LIMITERS, default="none")
    srv.add_argument("--limit", type=int, default=5, help="requests per window")
    srv.add_argument("--window", type=float, default=1.0, help="seconds")
    srv.add_argument("--port", type=int, default=8000)

    ham = commands.add_parser("hammer", help="send many requests at once")
    ham.add_argument("--url", default="http://127.0.0.1:8000/api/hello")
    ham.add_argument("--requests", type=int, default=40)
    ham.add_argument("--concurrency", type=int, default=8)
    ham.add_argument("--key", default="demo")
    ham.add_argument("--retry", action="store_true", help="back off and retry on 429")

    args = parser.parse_args(argv)

    if args.command == "simulate":
        times = PATTERNS[args.pattern]
        print(f"pattern {args.pattern}: {len(times)} requests, limit {args.limit} per second\n")
        print(f"{'limiter':<14}{'allowed':>8}{'rejected':>10}{'worst 1s':>10}")
        for name in LIMITERS:
            result = simulate(make(name, args.limit), times)
            worst = result.worst_window()
            print(f"{name:<14}{len(result.allowed):>8}{result.rejected:>10}{worst:>10}")
        return 0

    if args.command == "serve":
        server = make_server(make(args.limiter, args.limit, args.window), args.port)
        print(f"{args.limiter}, {args.limit} per {args.window:g}s")
        print(f"http://127.0.0.1:{server.server_port}/api/hello  (Ctrl+C to stop)")
        with contextlib.suppress(KeyboardInterrupt):
            server.serve_forever()
        return 0

    started = time.perf_counter()
    try:
        counts = hammer(args.url, args.requests, args.concurrency, args.key, args.retry)
    except OSError as error:
        print(f"could not reach {args.url}: {error}. Is `python -m limits serve` running?")
        return 1
    seconds = time.perf_counter() - started
    for status, count in sorted(counts.items()):
        print(f"{status}  x{count}")
    print(f"{args.requests} requests in {seconds:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
