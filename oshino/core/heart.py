import os
import asyncio
import sys
import multiprocessing as mp

import logbook

from time import time
from typing import TypeVar, Generic
from asyncio import BaseEventLoop

from logbook import Logger, StreamHandler
from riemann_client.client import QueuedClient
from raven.handlers.logbook import SentryHandler
from raven import Client as SentryClient
from logbook import NestedSetup

from ..config import Config
from ..version import get_version
from . import send_heartbeat, send_timedelta, send_metrics_count
from .admin import run as admin_run


T = TypeVar("T")


def create_loop():
    return asyncio.get_event_loop()


def forever():
    return True


def flush_riemann(client, transport, logger):
    try:
        transport.connect()
        client.flush()
        transport.disconnect()
    except ConnectionRefusedError as ce:
        logger.warn(ce)


def create_agents(agents_cfg: list):
    return list(map(lambda x: (x.instance, x), agents_cfg))


def init(agents: list):
    for agent, _ in agents:
        agent.on_start()


async def step(client: object, agents: list, loop: BaseEventLoop):

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
                    events_count: int,
                    q: mp.Queue):
    send_heartbeat(client.event, logger, int(interval * 1.5))
    send_timedelta(client.event, logger, delta, interval)
    send_metrics_count(client.event, logger, events_count)
    q.put_nowait({"time_delta": delta})
    q.put_nowait({"event_count": events_count})


async def main_loop(cfg: Config,
                    logger: Logger,
                    transport_cls: Generic[T],
                    continue_fn: callable,
                    loop: BaseEventLoop,
                    qin: mp.Queue,
                    qout: mp.Queue):
    riemann = cfg.riemann
    transport = transport_cls(riemann.host, riemann.port)
    client = QueuedClient(transport)
    agents = create_agents(cfg.agents)

    init(agents)

    while True:
        ts = time()
        await step(client, agents, loop=loop)
        te = time()
        td = te - ts
        instrumentation(client,
                        logger,
                        cfg.interval,
                        td,
                        len(client.queue.events),
                        qout)

        flush_riemann(client, transport, logger)
        if continue_fn():
            await asyncio.sleep(cfg.interval - int(td), loop=loop)
        else:
            logger.info("Stopping Oshino")
            break


def start_loop(cfg: Config):
    logger = Logger("Heart")
    handlers = []
    handlers.append(StreamHandler(sys.stdout, level=cfg.log_level))

    if cfg.sentry_dsn:
        client = SentryClient(cfg.sentry_dsn)
        handlers.append(SentryHandler(client,
                                      level=logbook.ERROR,
                                      bubble=True))

    setup = NestedSetup(handlers)
    setup.push_application()

    logger.info("Initializing Oshino v{0}, PID: {1}"
                .format(get_version(), os.getpid()))
    logger.info("Running forever in {0} seconds interval. Press Ctrl+C to exit"
                .format(cfg.interval))
    transport_queue = mp.Queue(maxsize=1000)
    command_queue = mp.Queue(maxsize=100)
    qs = [transport_queue, command_queue]

    admin_cfg = cfg.admin
    logger.info("Admin is enabled? {0}".format(admin_cfg.enabled))
    if admin_cfg.enabled:
        proc = mp.Process(name="Admin Panel",
                          target=admin_run,
                          args=(admin_cfg.host,
                                admin_cfg.port,
                                transport_queue,
                                command_queue))
        proc.daemon = True
        proc.start()

    loop = create_loop()
    try:
        loop.run_until_complete(main_loop(cfg,
                                          logger,
                                          cfg.riemann.transport,
                                          forever,
                                          loop=loop,
                                          qin=command_queue,
                                          qout=transport_queue))
    finally:
        loop.close()
        for q in qs:
            q.close()
            q.join_thread()
