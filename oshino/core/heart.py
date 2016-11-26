import asyncio
import sys
import logbook

from time import time
from typing import TypeVar, Generic

from logbook import Logger, StreamHandler
from riemann_client.transport import TCPTransport, Transport
from riemann_client.client import QueuedClient
from raven.handlers.logbook import SentryHandler
from raven import Client as SentryClient
from logbook import NestedSetup

from ..config import Config
from ..version import get_version
from . import send_heartbeat, send_timedelta, send_metrics_count

loop = asyncio.get_event_loop()

T = TypeVar("T")


def flush_riemann(client, transport, logger):
    try:
        transport.connect()
        client.flush()
        transport.disconnect()
    except ConnectionRefusedError as ce:
        logger.warn(ce)


def create_agents(agents_cfg: list):
    return list(map(lambda x: (x.instance, x), agents_cfg.agents))


def init(agents: list):
    for agent, _ in agents:
        agent.on_start()


async def step(client: object, agents: list):

    for agent, agent_cfg in agents:
        tags = [agent_cfg.tag] if agent_cfg.tag else []

        def event_fn(**kwargs):
            if "tags" in kwargs:
                for tag in tags:
                    kwargs["tags"].append(tag)
            else:
                kwargs["tags"] = tags

            if "time" not in kwargs:
                kwargs["time"] = int(time())

            client.event(**kwargs)

        await agent.process(event_fn)


def instrumentation(client: QueuedClient,
                    logger: Logger,
                    interval: int,
                    delta: int,
                    events_count: int):
    send_heartbeat(client.event, logger, int(interval * 1.5))
    send_timedelta(client.event, logger, delta, interval)
    send_metrics_count(client.event, logger, events_count)


async def main_loop(cfg: Config,
                    logger: Logger,
                    transport_cls: Generic[T]=TCPTransport):
    riemann = cfg.riemann
    transport = transport_cls(riemann.host, riemann.port)
    client = QueuedClient(transport)
    agents = create_agents(cfg.agents)

    init(agents)

    while True:
        ts = time()
        await step(client, agents)
        te = time()
        td = te - ts
        instrumentation(client,
                        logger,
                        cfg.interval,
                        td,
                        len(client.queue.events))

        flush_riemann(client, transport, logger)
        await asyncio.sleep(cfg.interval - int(td))


def start_loop(cfg: Config):
    handlers = []
    handlers.append(StreamHandler(sys.stdout, level=cfg.log_level))
    logger = Logger("Heart")
    logger.info("Initializing Oshino v{0}".format(get_version()))
    logger.info("Running forever in {0} seconds interval. Press Ctrl+C to exit"
                .format(cfg.interval))
    if cfg.sentry_dsn:
        client = SentryClient(cfg.sentry_dsn)
        handlers.append(SentryHandler(client,
                                      level=logbook.ERROR,
                                      bubble=True))

    setup = NestedSetup(handlers)
    setup.push_application()

    try:
        loop.run_until_complete(main_loop(cfg, logger))
    finally:
        loop.close()
