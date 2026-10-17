import pytest

from limits import FixedWindow, SlidingLog, TokenBucket, make
from limits.simulate import PATTERNS, Result, simulate


def allowed(limiter, times, key="k"):
    return [limiter.allow(key, t).allowed for t in times]


def test_fixed_window_allows_the_limit_then_rejects_until_the_next_window():
    limiter = FixedWindow(limit=2)

    assert allowed(limiter, [0.1, 0.2, 0.3, 1.0]) == [True, True, False, True]


def test_fixed_window_retry_after_points_at_the_next_window():
    limiter = FixedWindow(limit=1)
    limiter.allow("k", 0.25)

    assert limiter.allow("k", 0.25).retry_after == pytest.approx(0.75)


def test_fixed_window_lets_twice_the_limit_through_across_a_window_edge():
    result = simulate(FixedWindow(limit=10), PATTERNS["edge"])

    assert result.worst_window() == 20


def test_sliding_log_never_allows_more_than_the_limit_in_any_window():
    for pattern in PATTERNS.values():
        assert simulate(SlidingLog(limit=10), pattern).worst_window() <= 10


def test_sliding_log_retry_after_is_when_the_oldest_request_expires():
    limiter = SlidingLog(limit=2)
    limiter.allow("k", 0.2)
    limiter.allow("k", 0.5)

    assert limiter.allow("k", 0.6).retry_after == pytest.approx(0.6)


def test_token_bucket_allows_a_burst_up_to_its_capacity():
    limiter = TokenBucket(limit=1, burst=3)

    assert allowed(limiter, [0.0, 0.0, 0.0, 0.0]) == [True, True, True, False]


def test_token_bucket_refills_at_the_limit_rate():
    limiter = TokenBucket(limit=2)
    allowed(limiter, [0.0, 0.0])

    assert allowed(limiter, [0.25, 0.5]) == [False, True]


def test_token_bucket_retry_after_is_the_time_to_one_token():
    limiter = TokenBucket(limit=4)
    allowed(limiter, [0.0] * 4)

    assert limiter.allow("k", 0.0).retry_after == pytest.approx(0.25)


@pytest.mark.parametrize("name", ["fixed-window", "sliding-log", "token-bucket"])
def test_each_key_has_its_own_limit(name):
    limiter = make(name, limit=1)

    assert [limiter.allow(key, 0.0).allowed for key in ("a", "a", "b")] == [True, False, True]


def test_make_rejects_an_unknown_limiter():
    with pytest.raises(ValueError, match="unknown limiter"):
        make("leaky", limit=1)


def test_worst_window_counts_the_busiest_second():
    assert Result([0.0, 0.5, 0.9, 1.4, 3.0], rejected=0).worst_window() == 3
