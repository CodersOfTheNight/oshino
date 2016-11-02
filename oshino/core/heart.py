import asyncio
import signal
import sys

from logbook import Logger, StreamHandler
from riemann_client.transport import TCPTransport
from riemann_client.client import QueuedClient
from functools import partial

from ..config import Config
from ..version import get_version
from . import send_heartbeat

loop = asyncio.get_event_loop()


def flush_riemann(client, transport, logger):
    try:
        transport.connect()
        client.flush()
        transport.disconnect()
    except ConnectionRefusedError as ce:
        logger.warn(ce)

async def main_loop(cfg: Config, logger: Logger):
    riemann = cfg.riemann
    transport = TCPTransport(riemann.host, riemann.port)
    client = QueuedClient(transport)
    agents = list(map(lambda x: (x.instance, x), cfg.agents))
    while True:
        send_heartbeat(client, logger)
        for agent, agent_cfg in agents:
            tags = [agent_cfg.tag] if agent_cfg.tag else None
            event_fn = partial(client.event,
                               service=agent_cfg.name,
                               tags=tags)
            await agent.process(event_fn, logger)
        await asyncio.sleep(cfg.interval)
        flush_riemann(client, transport, logger)


def start_loop(cfg: Config):
    StreamHandler(sys.stdout).push_application()
    logger = Logger("Heart")
    logger.info("Initializing Oshino v{0}".format(get_version()))
    logger.info("Running forever in {0} seconds interval. Press Ctrl+C to exit"
                .format(cfg.interval))
    try:
        loop.run_until_complete(main_loop(cfg, logger))
    finally:
        loop.close()
