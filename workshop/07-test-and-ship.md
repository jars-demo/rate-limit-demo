# Test it, then ship it

> Limiters are full of time and threads, which makes them easy to get wrong. Test them with a fake clock, run the tests in CI, and know what changes with more than one server.

**Time:** 12 minutes

## Goal

Read how the lab tests time without waiting, run the same checks CI runs, and list what you would change before putting a limiter in front of real traffic.

## Time you control

Every limiter takes `now` as an argument, so tests pass whatever time they like. From `lab/tests/test_limiters.py`:

```python
def test_token_bucket_refills_at_the_limit_rate():
    limiter = TokenBucket(limit=2)
    allowed(limiter, [0.0, 0.0])

    assert allowed(limiter, [0.25, 0.5]) == [False, True]
```

No `sleep`, no flaky timing, and the test reads like the rule it checks. The HTTP tests in `lab/tests/test_http.py` start a real server on a free port with a frozen clock, so the count of `200` and `429` answers is exact even on a slow CI machine.

## Run what CI runs

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

The workflow in `.github/workflows/lab.yml` runs these on every push and pull request that touches `lab/`, then runs the `edge` simulation so its table shows up in the CI log.

## One server is the easy case

Everything in this lab keeps counters in memory, inside one process. That is fine for one server. With three servers behind a load balancer, each one keeps its own counts, and a client gets three times the limit. Real deployments move the counters to a shared store, usually Redis:

- The fixed window becomes `INCR` plus `EXPIRE` on a key like `rate:alice:1760700000`.
- The token bucket becomes a small Lua script, so read, refill and take happen in one atomic step.
- When the store is down, you must choose: allow everything (fail open) or reject everything (fail closed). Most APIs fail open and alert, because a broken limiter should not become an outage.

## Check it works

- All three commands above pass.
- You can say, in one sentence each, what fixed window, sliding log and token bucket are best at.

## Exercise

Add a test to `lab/tests/test_limiters.py` that would have caught the fixed window's edge burst if someone had claimed "never more than the limit in any second". Write it for `SlidingLog` first, where it passes, then point it at `FixedWindow` and watch it fail. Keep the passing version.

### More to try

- Run 50 threads that call one limiter's `allow` at the same time without the server's lock. Can you make the count go wrong? Then add the lock back and prove it holds.
- Write a short decision note for your team: which limiter, what key, what limit, fail open or closed, and how clients find out. One page is enough.
