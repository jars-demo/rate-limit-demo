# Rate limits from scratch

[![Lab](https://github.com/jars-demo/rate-limit-demo/actions/workflows/lab.yml/badge.svg)](https://github.com/jars-demo/rate-limit-demo/actions/workflows/lab.yml)
[![Frontend](https://github.com/jars-demo/rate-limit-demo/actions/workflows/frontend.yml/badge.svg)](https://github.com/jars-demo/rate-limit-demo/actions/workflows/frontend.yml)

A hands-on backend workshop. Build three rate limiters in plain Python, put them in front of a real HTTP server, break them on purpose, and write the client that backs off politely.

**Workshop site:** [ratelimit.jishanahmed.in](https://ratelimit.jishanahmed.in)

## Quick start

You need [uv](https://docs.astral.sh/uv/) and git. uv installs Python for you. The lab uses the Python standard library only.

```bash
git clone https://github.com/jars-demo/rate-limit-demo.git
cd rate-limit-demo/lab
uv sync
uv run python -m limits simulate
```

```text
pattern edge: 20 requests, limit 10 per second

limiter        allowed  rejected  worst 1s
none                20         0        20
fixed-window        20         0        20
sliding-log         10        10        10
token-bucket        11         9        11
```

The fixed window let 20 requests through in a fifth of a second, twice its limit. Chapter 02 explains why.

## Commands

| Command                                                  | What it does                                              |
| -------------------------------------------------------- | --------------------------------------------------------- |
| `uv run python -m limits simulate [--pattern edge]`      | replay `edge`, `steady` or `burst` traffic, fake clock    |
| `uv run python -m limits serve [--limiter token-bucket]` | run the API on `127.0.0.1:8000` with a limiter in front   |
| `uv run python -m limits hammer [--retry]`               | send 40 requests at once and count the answers            |
| `uv run pytest`                                          | the tests: limiters with a fake clock, a real HTTP server |

## The workshop

| #   | Chapter                                               | You learn                                       |
| --- | ----------------------------------------------------- | ----------------------------------------------- |
| 01  | [Why rate limits](workshop/01-why-rate-limits.md)     | what a limiter decides, an API with no limit    |
| 02  | [Fixed window](workshop/02-fixed-window.md)           | the simplest limiter and its edge burst         |
| 03  | [Sliding log](workshop/03-sliding-log.md)             | exact limits and their memory cost              |
| 04  | [Token bucket](workshop/04-token-bucket.md)           | bursts on purpose, a steady average             |
| 05  | [Say no properly: HTTP 429](workshop/05-http-429.md)  | status, Retry-After, RateLimit headers, the key |
| 06  | [Retry politely](workshop/06-retry-politely.md)       | backoff, jitter and the thundering herd         |
| 07  | [Test it, then ship it](workshop/07-test-and-ship.md) | fake clocks, CI, and limits across many servers |

## Layout

```text
lab/limits/      the limiters, the server, the client and the CLI
lab/tests/       pytest: limiters with a fake clock, HTTP against a real server
workshop/        the chapters, in Markdown
frontend/        the workshop site (Next.js), which renders workshop/
```

## Run the site locally

```bash
cd frontend
npm ci
npm run dev
```

## License

[MIT](LICENSE)
