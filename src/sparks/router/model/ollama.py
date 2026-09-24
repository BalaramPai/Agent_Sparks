import httpx

from sparks.router.model.provider import (
    InferenceRequest,
    InferenceResult,
    ModelProviderInterface,
)


class OllamaProvider(ModelProviderInterface):
    """
    Ollama-backed model provider.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            response = httpx.get(
                f"{self.base_url}/api/tags",
                timeout=5.0,
            )

            return response.is_success

        except httpx.HTTPError:
            return False

    def is_model_warm(self, model_name: str) -> bool:
        """
        Check whether Ollama currently has the model loaded in memory.
        """
        try:
            response = httpx.get(
                f"{self.base_url}/api/ps",
                timeout=5.0,
            )

            response.raise_for_status()

            data = response.json()

            return any(
                model.get("name") == model_name
                for model in data.get("models", [])
            )

        except httpx.HTTPError:
            return False

    def generate(
        self,
        request: InferenceRequest,
    ) -> InferenceResult:
        payload = {
            "model": request.model.name,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }

        if request.system_prompt:
            payload["system"] = request.system_prompt

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        return InferenceResult(
            text=data.get("response", ""),
            model_name=request.model.name,
            provider=request.model.provider.value,
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
        )
