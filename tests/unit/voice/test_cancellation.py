import pytest

from sparks.voice.cancellation import (
    CancellationError,
    CancellationToken,
)


def test_token_starts_not_cancelled():
    token = CancellationToken()

    assert token.is_cancelled is False


def test_cancel_marks_token_cancelled():
    token = CancellationToken()

    token.cancel()

    assert token.is_cancelled is True


def test_throw_if_cancelled_does_nothing_before_cancel():
    token = CancellationToken()

    token.throw_if_cancelled()


def test_throw_if_cancelled_raises_after_cancel():
    token = CancellationToken()

    token.cancel()

    with pytest.raises(CancellationError, match="Operation cancelled"):
        token.throw_if_cancelled()


def test_cancel_is_idempotent():
    token = CancellationToken()

    token.cancel()
    token.cancel()

    assert token.is_cancelled is True
