# Fixed window

> The simplest limiter: count requests in each one-second window. It is easy to build and it has a hole you can drive twice the traffic through.

**Time:** 15 minutes

## Goal

Read the fixed window limiter, put it in front of the API, and then find its weak spot with the simulator.

## How it works

Time is cut into windows: 0 to 1 second, 1 to 2, and so on. Each key gets a counter per window. When the counter reaches the limit, the rest of that window is rejected. Here is all of it, from `lab/limits/fixed_window.py`:

```python
    def allow(self, key: str, now: float) -> Decision:
        current = int(now // self.window)
        number, count = self._counts.get(key, (current, 0))
        if number != current:
            count = 0  # a new window: the count starts again
        if count >= self.limit:
            return Decision(False, 0, (current + 1) * self.window - now)
        self._counts[key] = (current, count + 1)
        return Decision(True, self.limit - count - 1, 0.0)
```

It stores two numbers per key, and `retry_after` is simply the time left until the next window starts.

## Put it in front of the API

Stop the server from chapter 01 and start it with a limit of 5 per second:

```bash
uv run python -m limits serve --limiter fixed-window --limit 5
```

Then hammer it again from the second terminal:

```bash
uv run python -m limits hammer
```

```text
200  x5
429  x35
40 requests in 0.59s
```

Five got through, 35 were turned away with `429 Too Many Requests`. That looks like a working limit.

## Find the hole

The simulator replays traffic against a limiter with a fake clock, so you can test things that are hard to time by hand. The `edge` pattern sends 20 requests between 0.90 and 1.09 seconds, right across the edge between two windows:

```bash
uv run python -m limits simulate --pattern edge
```

```text
pattern edge: 20 requests, limit 10 per second

limiter        allowed  rejected  worst 1s
none                20         0        20
fixed-window        20         0        20
sliding-log         10        10        10
token-bucket        11         9        11
```

`worst 1s` is the most requests your backend received inside any one second. The fixed window allowed all 20 in a fifth of a second: 10 at the end of the first window, then 10 more at the start of the next. The limit says 10 per second, and your backend just took 20.

This is the classic weakness of fixed windows. A client that learns where your windows start can always send twice the limit in a burst.

## Check it works

- `hammer` against `--limiter fixed-window --limit 5` shows exactly 5 responses with `200`.
- In the `edge` simulation, `fixed-window` has `worst 1s` of 20.

## Exercise

Change the edge pattern in `lab/limits/simulate.py` so it starts at `0.50` instead of `0.90`, and run the simulation again. Does the fixed window still let 20 through? Explain why, then put it back.

### More to try

- Run the simulator with `--limit 5`. What is the fixed window's worst second now? Find the rule: it is always a multiple of the limit.
- The dictionary `_counts` never forgets a key. With a million different API keys, what happens to memory? Sketch a fix.
