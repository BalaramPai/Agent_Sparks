from unittest.mock import Mock

from sparks.router.model.manager import ModelManager
from sparks.router.model.provider import InferenceRequest, InferenceResult
from sparks.router.model.types import (
    ModelCapability,
    ModelDefinition,
    ModelProvider,
)


def make_model(name: str) -> ModelDefinition:
    return ModelDefinition(
        name=name,
        provider=ModelProvider.OLLAMA,
        capability=ModelCapability.FAST,
        context_window=8192,
    )


def make_provider() -> Mock:
    provider = Mock()
    provider.is_available.return_value = True
    provider.generate.return_value = InferenceResult(
        text="hello from model",
        model_name="fast-local",
        provider="ollama",
    )
    return provider


def test_model_starts_unloaded():
    manager = ModelManager()

    manager.register(make_model("fast-local"), make_provider())

    state = manager.get("fast-local")

    assert state is not None
    assert state.loaded is False
    assert state.active is False


def test_model_can_be_loaded():
    manager = ModelManager()

    manager.register(make_model("fast-local"), make_provider())
    manager.load("fast-local")

    assert manager.get("fast-local").loaded is True


def test_model_must_be_loaded_before_activation():
    manager = ModelManager()

    manager.register(make_model("fast-local"), make_provider())

    try:
        manager.activate("fast-local")
        assert False
    except RuntimeError:
        assert True


def test_loaded_model_can_be_activated():
    manager = ModelManager()

    manager.register(make_model("fast-local"), make_provider())
    manager.load("fast-local")
    manager.activate("fast-local")

    assert manager.active_model.model.name == "fast-local"


def test_only_one_model_is_active():
    manager = ModelManager()

    manager.register(make_model("fast-local"), make_provider())
    manager.register(make_model("reasoning-local"), make_provider())

    manager.load("fast-local")
    manager.load("reasoning-local")

    manager.activate("fast-local")
    manager.activate("reasoning-local")

    assert manager.get("fast-local").active is False
    assert manager.get("reasoning-local").active is True


def test_unload_removes_active_state():
    manager = ModelManager()

    manager.register(make_model("fast-local"), make_provider())
    manager.load("fast-local")
    manager.activate("fast-local")

    manager.unload("fast-local")

    assert manager.get("fast-local").loaded is False
    assert manager.get("fast-local").active is False
    assert manager.active_model is None


def test_generate_uses_registered_provider():
    manager = ModelManager()

    provider = make_provider()
    model = make_model("fast-local")

    manager.register(model, provider)
    manager.load(model.name)

    request = InferenceRequest(
        model=model,
        prompt="hello",
    )

    result = manager.generate(request)

    assert result.text == "hello from model"
    provider.generate.assert_called_once_with(request)


def test_generate_rejects_unloaded_model():
    manager = ModelManager()

    model = make_model("fast-local")
    manager.register(model, make_provider())

    request = InferenceRequest(
        model=model,
        prompt="hello",
    )

    try:
        manager.generate(request)
        assert False
    except RuntimeError as error:
        assert "not loaded" in str(error)


def test_generate_rejects_unavailable_provider():
    manager = ModelManager()

    provider = make_provider()
    provider.is_available.return_value = False

    model = make_model("fast-local")

    manager.register(model, provider)
    manager.load(model.name)

    request = InferenceRequest(
        model=model,
        prompt="hello",
    )

    try:
        manager.generate(request)
        assert False
    except RuntimeError as error:
        assert "unavailable" in str(error)
