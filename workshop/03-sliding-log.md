# Sliding log

> Remember when every allowed request happened, and count only the last second. Exact, with a memory bill.

**Time:** 12 minutes

## Goal

Close the fixed window's hole with a limiter that looks at any one-second span, not fixed ones, and learn what that exactness costs.

## How it works

Instead of a counter, the sliding log keeps a queue of timestamps per key. On each request it first drops the timestamps older than one window, then counts what is left. From `lab/limits/sliding_log.py`:

```python
    def allow(self, key: str, now: float) -> Decision:
        log = self._log[key]
        while log and log[0] <= now - self.window:
            log.popleft()  # older than one window: no longer counts
        if len(log) >= self.limit:
            return Decision(False, 0, log[0] + self.window - now)
        log.append(now)
        return Decision(True, self.limit - len(log), 0.0)
```

`retry_after` is exact too: the moment the oldest request in the log turns one window old, there is room again.

## Run it

Look again at the `edge` simulation from chapter 02. The sliding log allowed 10 and rejected 10, with a worst second of exactly 10. Now try steady traffic at twice the limit:

```bash
uv run python -m limits simulate --pattern steady
```

```text
pattern steady: 60 requests, limit 10 per second

limiter        allowed  rejected  worst 1s
none                60         0        20
fixed-window        30        30        10
sliding-log         30        30        10
token-bucket        39        21        19
```

Under steady load the fixed window and the sliding log agree. They only differ at window edges, which is exactly where an attacker or an unlucky cron job will be.

Put it in front of the API and compare with chapter 02:

```bash
uv run python -m limits serve --limiter sliding-log --limit 5
```

## The cost

The fixed window stores two numbers per key. The sliding log stores one timestamp for every allowed request in the window. For a limit of 10 per second that is nothing. For a limit of 100,000 per hour, it is 100,000 floats per key. That is why real systems often use a cheaper approximation, the sliding window counter: keep the current and the previous fixed window counts, and weigh the previous one by how much of it still overlaps the last second.

## Check it works

- In the `edge` and `steady` simulations, `sliding-log` never shows a `worst 1s` above 10.
- `uv run pytest -k sliding` passes.

## Exercise

Add a fourth limiter, `SlidingWindow`, in a new file named `sliding_window.py`, next to the other limiters. Keep two counts per key: the previous window and the current one. Estimate the count as `previous * (1 - elapsed) + current`, where `elapsed` is how far you are into the current window, from 0 to 1. Register it in `LIMITERS` in `lab/limits/__init__.py` and run the simulator. How close does it get to the sliding log?

### More to try

- Write a test that proves your `SlidingWindow` never lets more than `2 * limit` through in any second, using `simulate` and `worst_window()`.
- What happens to the sliding log if a client keeps sending requests that are all rejected? Does the log grow? Read the code and check.
