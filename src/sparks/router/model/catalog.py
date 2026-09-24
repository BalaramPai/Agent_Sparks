from dataclasses import dataclass

import httpx

from sparks.router.model.types import ModelProvider


@dataclass(frozen=True)
class InstalledModel:
    name: str
    provider: ModelProvider


class OllamaCatalog:
    """
    Discovers models currently installed in Ollama.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 5.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def list_models(self) -> list[InstalledModel]:
        response = httpx.get(
            f"{self.base_url}/api/tags",
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        return [
            InstalledModel(
                name=model["name"],
                provider=ModelProvider.OLLAMA,
            )
            for model in data.get("models", [])
        ]