import asyncio
import signal

from logbook import Logger

from ..config import Config
from ..version import get_version

loop = asyncio.get_event_loop()


def ask_exit():
    loop.stop()


def start_loop(cfg: Config):
    logger = Logger("Heart")
    logger.info("Initializing Oshino v{0}".format(get_version()))
    exit_signals = ("SIGINT", "SIGTERM", )
    for signame in exit_signals:
        loop.add_signal_handler(getattr(signal, signame), ask_exit)

    logger.info("Running forever in {0}seconds interval. Press Ctrl+C to exit"
                .format(cfg.interval))
    try:
        loop.run_forever()
    finally:
        loop.close()
