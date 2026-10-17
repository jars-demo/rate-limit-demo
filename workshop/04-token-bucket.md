# Token bucket

> Allow short bursts on purpose, and hold the average rate steady. The limiter most public APIs use.

**Time:** 15 minutes

## Goal

Understand the token bucket, see why its worst second is higher than the limit, and decide when that is what you want.

## How it works

Every key has a bucket that holds up to `burst` tokens. Each request takes one. The bucket refills at a steady `limit` tokens per window, and never past full. From `lab/limits/token_bucket.py`:

```python
    def allow(self, key: str, now: float) -> Decision:
        tokens, last = self._buckets.get(key, (float(self.capacity), now))
        tokens = min(self.capacity, tokens + (now - last) * self.rate)
        if tokens < 1:
            self._buckets[key] = (tokens, now)
            return Decision(False, 0, (1 - tokens) / self.rate)
        tokens -= 1
        self._buckets[key] = (tokens, now)
        return Decision(True, int(tokens), 0.0)
```

There is no timer refilling buckets in the background. The refill is computed lazily from the time since the key was last seen, so an idle key costs nothing.

## Two numbers, two promises

The token bucket separates two things the window limiters mix together:

- **Rate**: the long-run average. Over an hour, a client can never beat `limit` per second.
- **Burst**: how much a client can do at once after being quiet. A page that loads and fires 8 requests at the same time is normal, not abuse.

Look at the `steady` simulation from chapter 03 again: `token-bucket` allowed 39, with a worst second of 19. It started with a full bucket of 10, spent it, and then let through the refill of 10 per second. That is the trade: a full bucket plus one second of refill can land inside the same second.

Now the `burst` pattern, 30 requests at once and then one per second:

```bash
uv run python -m limits simulate --pattern burst
```

```text
pattern burst: 35 requests, limit 10 per second

limiter        allowed  rejected  worst 1s
none                35         0        30
fixed-window        15        20        10
sliding-log         15        20        10
token-bucket        15        20        10
```

Against one big burst, all three limiters agree: 10 now, then the trickle.

## Run it for real

```bash
uv run python -m limits serve --limiter token-bucket --limit 5
uv run python -m limits hammer
```

```text
200  x7
429  x33
40 requests in 0.59s
```

Seven, not five: the bucket started full with 5, and the hammer ran for about 0.6 seconds, long enough for 2 more tokens to drip in.

## Check it works

- `uv run pytest -k token` passes.
- `hammer` against the token bucket shows a few more `200` responses than the limit, and the extra matches the run time multiplied by the rate.

## Exercise

`TokenBucket` already accepts a `burst` argument, but the server always uses the default (`burst` equals `limit`). Add a `--burst` option to `serve` in `lab/limits/__main__.py`, pass it through, and run `hammer` with `--limit 2 --burst 10`. Predict the number of `200` responses before you run it.

### More to try

- Write a test showing that over a long period, say 0 to 100 seconds with a request every 0.01 seconds, the token bucket allows close to `limit * 100` requests. That is the average-rate promise.
- The leaky bucket is the token bucket's twin: requests queue and drain at a fixed rate instead of being rejected. When would you rather queue than reject?
