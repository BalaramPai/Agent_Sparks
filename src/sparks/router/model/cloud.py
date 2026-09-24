from sparks.router.model.provider import (
    InferenceRequest,
    InferenceResult,
    ModelProviderInterface,
)


class CloudProvider(ModelProviderInterface):
    """
    Cloud inference provider boundary.

    The concrete API integration will be configured later.
    This provider currently exposes availability and a clear
    unsupported state rather than silently pretending cloud
    inference exists.
    """

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def is_available(self) -> bool:
        return self.enabled

    def generate(
        self,
        request: InferenceRequest,
    ) -> InferenceResult:
        if not self.enabled:
            raise RuntimeError(
                "Cloud inference is not configured"
            )

        raise RuntimeError(
            "Cloud inference backend is not implemented"
        )