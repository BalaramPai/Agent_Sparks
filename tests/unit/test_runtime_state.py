from sparks.core.state.runtime_state import RuntimeState, RuntimeStatus


def test_runtime_starts_and_stops():
    state = RuntimeState()

    assert state.status == RuntimeStatus.STOPPED

    state.start()

    assert state.status == RuntimeStatus.RUNNING
    assert state.is_running is True
    assert state.started_at is not None

    state.stop()

    assert state.status == RuntimeStatus.STOPPED
    assert state.is_running is False
    assert state.stopped_at is not None


def test_context_storage():
    state = RuntimeState()

    state.set_context("active_project", "SPARKS")

    assert state.get_context("active_project") == "SPARKS"
    assert state.get_context("missing") is None