import asyncio
import signal
import sys

from logbook import Logger, StreamHandler
from riemann_client.transport import TCPTransport
from riemann_client.client import QueuedClient

from ..config import Config
from ..version import get_version
from .core import send_heartbeat

loop = asyncio.get_event_loop()


async def main_loop(cfg: Config):
    riemann = cfg.riemann
    while True:
        with QueuedClient(TCPTransport(riemann.host, riemann.port)) as client:
            send_heartbeat(client, logger)
            asyncio.sleep(cfg.interval)
            client.flush()


def start_loop(cfg: Config):
    StreamHandler(sys.stdout).push_application()
    logger = Logger("Heart")
    logger.info("Initializing Oshino v{0}".format(get_version()))
    logger.info("Running forever in {0} seconds interval. Press Ctrl+C to exit"
                .format(cfg.interval))
    try:
        loop.run_until_complete(main_loop(cfg))
    finally:
        loop.close()
