import asyncio
import signal
import sys
from time import time

from logbook import Logger, StreamHandler
from riemann_client.transport import TCPTransport
from riemann_client.client import QueuedClient
from functools import partial

from ..config import Config
from ..version import get_version
from . import send_heartbeat, send_timedelta, send_metrics_count

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
        ts = time()
        for agent, agent_cfg in agents:
            tags = [agent_cfg.tag] if agent_cfg.tag else None
            event_fn = partial(client.event,
                               tags=tags,
                               time=int(time()))
            await agent.process(event_fn)

        te = time()
        td = te - ts
        # Instrumentation
        send_heartbeat(client.event, logger, int(cfg.interval * 1.5))
        send_timedelta(client.event, logger, td, cfg.interval)
        send_metrics_count(client.event, logger, len(client.queue.events))

        flush_riemann(client, transport, logger)
        await asyncio.sleep(cfg.interval - int(td))


def start_loop(cfg: Config):
    StreamHandler(sys.stdout, level=cfg.log_level).push_application()
    logger = Logger("Heart")
    logger.info("Initializing Oshino v{0}".format(get_version()))
    logger.info("Running forever in {0} seconds interval. Press Ctrl+C to exit"
                .format(cfg.interval))
    try:
        loop.run_until_complete(main_loop(cfg, logger))
    finally:
        loop.close()
