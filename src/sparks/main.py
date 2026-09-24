from sparks.config.settings import get_settings
from sparks.core.runtime.application import Application
from sparks.core.runtime.logging import configure_logging, get_logger


def main() -> None:
    settings = get_settings()

    configure_logging()

    logger = get_logger("sparks.main")

    logger.info(
        "Initializing %s in %s environment",
        settings.app_name,
        settings.environment,
    )

    application = Application()

    application.install_signal_handlers()
    application.start()

    logger.info("SPARKS is running")

    try:
        while application.is_running:
            input()
    except EOFError:
        application.request_shutdown()


if __name__ == "__main__":
    main()