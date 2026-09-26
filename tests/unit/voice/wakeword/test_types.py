from sparks.voice.wakeword.types import WakeWordDetection


def test_wake_word_detection_defaults():
    result = WakeWordDetection(detected=False)

    assert not result.detected
    assert result.keyword is None
    assert result.confidence is None


def test_wake_word_detection():
    result = WakeWordDetection(
        detected=True,
        keyword="sparks",
        confidence=0.94,
    )

    assert result.detected
    assert result.keyword == "sparks"
    assert result.confidence == 0.94


def test_wake_word_detection_rejects_invalid_confidence():
    for confidence in (-0.1, 1.1):
        try:
            WakeWordDetection(
                detected=True,
                keyword="sparks",
                confidence=confidence,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError")


def test_detected_wake_word_requires_keyword():
    try:
        WakeWordDetection(
            detected=True,
            confidence=0.9,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
