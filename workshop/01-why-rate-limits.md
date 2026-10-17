# Why rate limits

> One busy client can take your API down for everyone. Start a real server with no limit and watch it say yes to everything.

**Time:** 10 minutes

## Goal

Run the lab, start the API with no limit, and send it 40 requests at once. By the end you know what a rate limit protects and which questions every limiter has to answer.

## Set up

You need [uv](https://docs.astral.sh/uv/) and git. uv installs Python for you. There are no other dependencies: the lab uses the Python standard library only.

```bash
git clone https://github.com/jars-demo/rate-limit-demo.git
cd rate-limit-demo/lab
uv sync
```

## Start the API with no limit

The API lives in `lab/limits/server.py`. It has one endpoint, `/api/hello`, and a limiter in front of it. For now the limiter is `none`, which says yes to everything.

```bash
uv run python -m limits serve
```

Leave it running. In a second terminal, send 40 requests, 8 at a time:

```bash
uv run python -m limits hammer
```

```text
200  x40
40 requests in 0.60s
```

Every request got through. That is fine for one polite client. Now imagine a script with a bug that loops, a scraper, or a customer who runs a batch job at noon. Each request costs you CPU, database time, and maybe money for an upstream API. Without a limit, the busiest client decides how slow your API is for everyone else.

## What a limiter decides

A rate limit is a promise: "each client gets at most N requests per period". Every limiter in this workshop answers the same three questions for each request:

1. **Who is asking?** The key. Here it is the `X-Api-Key` header, or the client's address when there is none.
2. **Is there room?** Allowed or rejected.
3. **If not, when?** How many seconds until this key could pass. Clients need this to back off properly.

That is the whole interface, in `lab/limits/core.py`:

```python
@dataclass(frozen=True)
class Decision:
    allowed: bool
    remaining: int
    # Seconds until this key could pass again. 0 when the request was allowed.
    retry_after: float
```

Each limiter has one method, `allow(key, now)`, which returns a `Decision`. Taking `now` as an argument, instead of reading the clock inside, is what makes limiters easy to test: you can replay a whole day of traffic in a millisecond.

## Check it works

- `hammer` printed `200  x40`.
- Stop the server with Ctrl+C. Run `hammer` again: it says it could not reach the server and asks if `serve` is running.

## Exercise

Run `uv run python -m limits hammer --requests 400 --concurrency 32`. How long does it take? Your laptop is fast and the endpoint does nothing. Write down one thing a real endpoint does that would make 400 requests at once hurt.

### More to try

- Open `lab/limits/server.py` and find where the key comes from. What could go wrong if you trusted any client-sent header as the key?
- Read `lab/limits/__init__.py`. Which limiters are there? Guess how each one works before chapter 02.
