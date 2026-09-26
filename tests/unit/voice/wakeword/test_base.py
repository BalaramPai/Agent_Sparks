from sparks.voice.wakeword.base import WakeWordDetector
from sparks.voice.wakeword.types import WakeWordDetection


class FakeWakeWordDetector(WakeWordDetector):
    def __init__(self):
        self.reset_called = False

    def detect(self, audio: bytes) -> WakeWordDetection:
        return WakeWordDetection(
            detected=False,
        )

    def reset(self) -> None:
        self.reset_called = True


def test_wake_word_detector_contract():
    detector = FakeWakeWordDetector()

    result = detector.detect(b"audio")

    assert isinstance(result, WakeWordDetection)
    assert not result.detected

    detector.reset()

    assert detector.reset_called
