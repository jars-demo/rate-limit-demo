# Retry politely

> The other side of the limit: a client that backs off, adds jitter and respects Retry-After, instead of hammering harder.

**Time:** 15 minutes

## Goal

Switch the hammer from "give up on 429" to "wait and retry", and understand why every retry needs randomness.

## The naive retry makes it worse

When a request is rejected, the obvious fix is to try again right away. Now picture a thousand clients that were all rejected at the same moment. They all retry at the same moment, are all rejected again, and retry again. Your rate limit turns into a load generator. This is the thundering herd.

Two fixes, both in `lab/limits/client.py`:

1. **Exponential backoff**: wait longer after each failure, 0.1 seconds, then 0.2, 0.4, and so on, up to a cap.
2. **Jitter**: pick a random wait between 0 and that number, so clients spread out instead of returning together.

```python
def backoff(attempt: int, base: float = 0.1, cap: float = 2.0, rng=random.random) -> float:
    """Full jitter: a random wait between 0 and base * 2^attempt, never more than cap."""
    return rng() * min(cap, base * 2**attempt)
```

When the server sends `Retry-After`, the client trusts it, and still adds a little jitter on top. Only `429` and `503` are retried; a `400` or a `500` will not fix itself by waiting.

## Run it

Start the token bucket server from chapter 04:

```bash
uv run python -m limits serve --limiter token-bucket --limit 5
```

Hammer it with retries on:

```bash
uv run python -m limits hammer --retry
```

```text
200  x37
429  x3
40 requests in 7.59s
```

Compare with chapter 04, where 7 of 40 got through in 0.6 seconds. Now 37 got through, and the run took longer, because the clients waited their turn. The 3 that still failed used up all 5 attempts. That is correct behaviour: a retry loop must end, and the caller has to decide what to do next.

Rough sum: at 5 per second, 40 requests need about 7 seconds. The client paced itself to the limit without knowing the limit.

## Check it works

- `hammer --retry` shows far more `200` responses than `hammer` without it.
- `uv run pytest -k retry` passes: the tests use a fake `sleep` and a fixed `rng`, so they run instantly.

## Exercise

Run `hammer --retry --requests 40 --concurrency 40`: every request starts at once. Then edit `call_with_retry` in `lab/limits/client.py` to ignore the jitter (`rng=lambda: 1.0` everywhere) and run it again. Compare the number of `429` answers and the run time. Put the jitter back.

### More to try

- Add a total deadline to `call_with_retry`: give up when the next wait would go past, say, 5 seconds from the first attempt, even if attempts remain.
- Only retry requests that are safe to repeat. A `GET` is. A `POST /payments` is not, unless it carries an idempotency key. How would you add one?
