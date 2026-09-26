from __future__ import annotations

from sparks.voice.interruption import (
    InterruptionController,
    InterruptionReason,
)


def test_interrupt_calls_cancellation() -> None:
    calls = []

    controller = InterruptionController(
        lambda: calls.append("cancel") or True
    )

    assert controller.interrupt() is True
    assert calls == ["cancel"]
    assert controller.interrupted is True


def test_interrupt_records_reason_and_source() -> None:
    controller = InterruptionController(
        lambda: True
    )

    controller.interrupt(
        InterruptionReason.USER_REQUEST,
        source="voice",
    )

    event = controller.last_event

    assert event is not None
    assert event.reason == InterruptionReason.USER_REQUEST
    assert event.source == "voice"


def test_failed_interruption_is_not_recorded() -> None:
    controller = InterruptionController(
        lambda: False
    )

    assert controller.interrupt() is False
    assert controller.interrupted is False
    assert controller.last_event is None


def test_reset_clears_interruption() -> None:
    controller = InterruptionController(
        lambda: True
    )

    controller.interrupt()

    assert controller.interrupted is True

    controller.reset()

    assert controller.interrupted is False
    assert controller.last_event is None


def test_invalid_callback_rejected() -> None:
    try:
        InterruptionController(None)
        assert False, "Expected TypeError"
    except TypeError:
        pass
