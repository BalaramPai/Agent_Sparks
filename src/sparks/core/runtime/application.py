import signal
from types import FrameType

from sparks.core.events.bus import EventBus
from sparks.core.runtime.logging import get_logger
from sparks.core.state.runtime_state import RuntimeState, RuntimeStatus


class Application:
    """
    Main lifecycle coordinator for the SPARKS runtime.
    """

    def __init__(self) -> None:
        self.state = RuntimeState()
        self.event_bus = EventBus()
        self.logger = get_logger("sparks.runtime")

        self._shutdown_requested = False

    def start(self) -> None:
        if self.state.is_running:
            return

        self.state.status = RuntimeStatus.STARTING

        self.logger.info("Starting SPARKS runtime")
        self.event_bus.publish("runtime.starting")

        self.state.start()

        self.logger.info("SPARKS runtime started")

        self.event_bus.publish(
            "runtime.started",
            {
                "status": self.state.status.value,
                "started_at": self.state.started_at,
            },
        )

    def stop(self) -> None:
        if self.state.status == RuntimeStatus.STOPPED:
            return

        self.state.status = RuntimeStatus.STOPPING

        self.logger.info("Stopping SPARKS runtime")
        self.event_bus.publish("runtime.stopping")

        self.state.stop()

        self.logger.info("SPARKS runtime stopped")

        self.event_bus.publish(
            "runtime.stopped",
            {
                "status": self.state.status.value,
                "stopped_at": self.state.stopped_at,
            },
        )

    def request_shutdown(self) -> None:
        """
        Request a graceful shutdown.
        """
        if self._shutdown_requested:
            return

        self._shutdown_requested = True
        self.logger.info("Shutdown requested")

        self.stop()

    def install_signal_handlers(self) -> None:
        """
        Register operating-system shutdown signals.
        """
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        self.logger.info("Signal handlers installed")

    def _handle_signal(
        self,
        signum: int,
        frame: FrameType | None,
    ) -> None:
        self.logger.info("Received shutdown signal: %s", signum)
        self.request_shutdown()

    @property
    def is_running(self) -> bool:
        return self.state.is_running