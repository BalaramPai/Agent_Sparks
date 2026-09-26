from collections.abc import Iterable
from typing import Any

import numpy as np
from faster_whisper import WhisperModel

from sparks.voice.stt.base import (
    SpeechToText,
    TranscriptionCallback,
)
from sparks.voice.stt.types import (
    TranscriptionResult,
    TranscriptionType,
)


class FasterWhisperSTT(SpeechToText):
    """
    SPARKS Speech-to-Text adapter backed by faster-whisper.

    SPARKS capture provides mono 16-bit PCM bytes.
    This adapter converts that transient PCM data into the
    float32 audio representation expected by faster-whisper.

    Model loading remains explicit so SPARKS can later make
    resource-aware model/device decisions.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = None,
        beam_size: int = 1,
        sample_rate: int = 16_000,
    ) -> None:
        if not model_size:
            raise ValueError("model_size must not be empty")

        if device not in {"cpu", "cuda"}:
            raise ValueError("device must be 'cpu' or 'cuda'")

        if compute_type not in {
            "int8",
            "int8_float16",
            "float16",
            "float32",
        }:
            raise ValueError("unsupported compute_type")

        if beam_size <= 0:
            raise ValueError("beam_size must be positive")

        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.beam_size = beam_size
        self.sample_rate = sample_rate

        self._model: WhisperModel | None = None
        self._cancelled = False

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        if self._model is not None:
            return

        self._model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )

    def transcribe(
        self,
        audio_chunks: Iterable[bytes],
        callback: TranscriptionCallback,
    ) -> None:
        if not callable(callback):
            raise TypeError("callback must be callable")

        self._cancelled = False

        if self._model is None:
            self.load()

        audio = b"".join(audio_chunks)

        if not audio:
            return

        pcm = np.frombuffer(audio, dtype=np.int16)

        if pcm.size == 0:
            return

        audio_float32 = pcm.astype(np.float32) / 32768.0

        segments, info = self._model.transcribe(
            audio_float32,
            language=self.language,
            beam_size=self.beam_size,
            vad_filter=False,
            condition_on_previous_text=False,
        )

        for segment in segments:
            if self._cancelled:
                return

            text = segment.text.strip()

            if not text:
                continue

            callback(
                TranscriptionResult(
                    text=text,
                    result_type=TranscriptionType.FINAL,
                    confidence=self._segment_confidence(segment),
                    language=getattr(info, "language", None),
                )
            )

    def cancel(self) -> None:
        self._cancelled = True

    @staticmethod
    def _segment_confidence(segment: Any) -> float | None:
        avg_logprob = getattr(segment, "avg_logprob", None)

        if avg_logprob is None:
            return None

        import math

        confidence = math.exp(avg_logprob)

        return max(0.0, min(1.0, confidence))
