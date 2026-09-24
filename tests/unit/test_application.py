from sparks.core.runtime.application import Application
from sparks.core.state.runtime_state import RuntimeStatus


def test_application_lifecycle():
    app = Application()

    assert app.state.status == RuntimeStatus.STOPPED

    app.start()

    assert app.is_running is True
    assert app.state.status == RuntimeStatus.RUNNING

    app.stop()

    assert app.is_running is False
    assert app.state.status == RuntimeStatus.STOPPED