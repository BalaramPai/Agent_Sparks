class ModelError(Exception):
    """Base error for model-related failures."""


class ModelUnavailableError(ModelError):
    """Raised when a required model/provider is unavailable."""


class NoCompatibleModelError(ModelError):
    """Raised when no model satisfies the current requirements."""


class InferenceFailedError(ModelError):
    """Raised when model inference fails."""