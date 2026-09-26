from abc import ABC, abstractmethod
from collections.abc import Callable


class AudioCaptureConfig:
    """
    Configuration for microphone capture.

    SPARKS uses mono 16-bit PCM at 16 kHz as its initial
    speech-processing boundary.
    """

    def __init__(
        self,
        sample_rate: int = 16_000,
        channels: int = 1,
        sample_width_bytes: int = 2,
        block_size: int = 320,
    ) -> None:
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        if channels != 1:
            raise ValueError("SPARKS voice capture currently requires mono audio")

        if sample_width_bytes != 2:
            raise ValueError(
                "SPARKS voice capture currently requires 16-bit PCM audio"
            )

        if block_size <= 0:
            raise ValueError("block_size must be positive")

        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width_bytes = sample_width_bytes
        self.block_size = block_size


AudioCallback = Callable[[bytes], None]


class AudioCapture(ABC):
    """
    Provider-independent microphone capture contract.

    Implementations are responsible for acquiring audio from
    a physical or virtual input device. Consumers should not
    depend on a specific audio library.
    """

    def __init__(self, config: AudioCaptureConfig | None = None) -> None:
        self.config = config or AudioCaptureConfig()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    @abstractmethod
    def start(self, callback: AudioCallback) -> None:
        """
        Start microphone capture.

        The callback receives one PCM audio block as bytes.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop microphone capture."""
        raise NotImplementedError
