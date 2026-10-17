# AGENTS.md

Guidance for AI coding agents and developers. Humans: start with [README.md](README.md).

## What this is

A short workshop, "Rate limits from scratch": three rate limiters in plain Python, a real HTTP
server that answers 429, and a client that backs off. The lab in `lab/` and the chapters in
`workshop/` are the product; `frontend/` is the site.

## Map

```text
lab/limits/core.py        Decision, the Limiter protocol, Unlimited
lab/limits/fixed_window.py, sliding_log.py, token_bucket.py
                          one limiter each; allow(key, now) takes the time as an argument
lab/limits/simulate.py    traffic PATTERNS replayed with a fake clock, worst_window()
lab/limits/server.py      ThreadingHTTPServer on 127.0.0.1, 429 + Retry-After + RateLimit-*
lab/limits/client.py      get(), backoff() with full jitter, call_with_retry()
lab/limits/__main__.py    CLI: simulate, serve, hammer
workshop/NN-slug.md       chapters; code quoted from lab/ must match it exactly
frontend/                 Next.js site; reads ../workshop at build time
```

## Commands

```bash
cd lab && uv sync && uv run pytest && uv run python -m limits simulate
cd frontend && npm ci && npm run verify
```

## Rules

1. **No runtime dependencies** in `lab/`. Standard library only, so it runs anywhere.
2. **Limiters never read the clock.** They take `now`, so tests and the simulator control time.
3. **Chapters quote real code and real output.** A unit test checks each `allow()` quoted in
   chapters 02 to 04 and every file path chapters mention. Rerun commands before changing output.
4. **Writing style.** Plain English, short sentences, no em dashes. Conventional Commits, no AI
   attribution trailers.
