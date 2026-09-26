from sparks.voice.wakeword.policy import (
    ActivationConfig,
    ActivationPolicy,
    ActivationState,
)
from sparks.voice.wakeword.types import WakeWordDetection


def test_activation_starts_inactive():
    policy = ActivationPolicy()

    assert policy.state == ActivationState.INACTIVE
    assert not policy.is_active


def test_wake_word_activates_policy():
    policy = ActivationPolicy(
        ActivationConfig(activation_timeout_frames=3)
    )

    event = policy.process(
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.95,
        )
    )

    assert event is not None
    assert event.state == ActivationState.ACTIVE
    assert event.keyword == "sparks"
    assert event.confidence == 0.95
    assert policy.is_active


def test_activation_remains_active_until_timeout():
    policy = ActivationPolicy(
        ActivationConfig(activation_timeout_frames=2)
    )

    policy.process(
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.9,
        )
    )

    assert policy.process(
        WakeWordDetection(detected=False)
    ) is None

    event = policy.process(
        WakeWordDetection(detected=False)
    )

    assert event is not None
    assert event.state == ActivationState.INACTIVE
    assert not policy.is_active


def test_repeated_wake_word_refreshes_activation():
    policy = ActivationPolicy(
        ActivationConfig(activation_timeout_frames=2)
    )

    policy.process(
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.9,
        )
    )

    policy.process(
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.95,
        )
    )

    assert policy.is_active

    assert policy.process(
        WakeWordDetection(detected=False)
    ) is None

    assert policy.is_active


def test_manual_deactivation():
    policy = ActivationPolicy(
        ActivationConfig(activation_timeout_frames=10)
    )

    policy.process(
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.9,
        )
    )

    event = policy.deactivate()

    assert event is not None
    assert event.state == ActivationState.INACTIVE
    assert not policy.is_active


def test_deactivation_when_already_inactive_is_noop():
    policy = ActivationPolicy()

    assert policy.deactivate() is None


def test_disabled_wake_word_policy_is_always_active():
    policy = ActivationPolicy(
        ActivationConfig(enabled=False)
    )

    assert policy.state == ActivationState.ACTIVE
    assert policy.is_active

    assert policy.process(
        WakeWordDetection(detected=False)
    ) is None


def test_reset_returns_enabled_policy_to_inactive():
    policy = ActivationPolicy(
        ActivationConfig(activation_timeout_frames=10)
    )

    policy.process(
        WakeWordDetection(
            detected=True,
            keyword="sparks",
            confidence=0.9,
        )
    )

    policy.reset()

    assert policy.state == ActivationState.INACTIVE
    assert not policy.is_active


def test_invalid_timeout_is_rejected():
    try:
        ActivationConfig(activation_timeout_frames=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
