from dataclasses import dataclass
from enum import Enum


class ModelCapability(str, Enum):
    FAST = "fast"
    GENERAL = "general"
    REASONING = "reasoning"
    VISION = "vision"
    EMBEDDING = "embedding"
    STT = "stt"
    TTS = "tts"


class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    LOCAL = "local"


@dataclass(frozen=True)
class ModelDefinition:
    name: str
    provider: ModelProvider
    capability: ModelCapability

    context_window: int
    requires_gpu: bool = False
    minimum_vram_mb: int = 0

    priority: int = 100
