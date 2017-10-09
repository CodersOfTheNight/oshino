import asyncio
import sys
import logbook

from time import time
from typing import TypeVar, Generic
from asyncio import BaseEventLoop
from concurrent.futures import ThreadPoolExecutor

from logbook import Logger, StreamHandler
from raven.handlers.logbook import SentryHandler
from raven import Client as SentryClient
from logbook import NestedSetup

from ..config import Config
from ..version import get_version
from . import (send_heartbeat,
               send_timedelta,
               send_pending_events_count,
               send_metrics_count)
from . import processor


T = TypeVar("T")


def create_loop():
    return asyncio.get_event_loop()


def forever():
    return True


def create_agents(agents_cfg: list):
    return list(map(lambda x: (x.instance, x), agents_cfg))


def init(agents: list):
    for agent, _ in agents:
        agent.on_start()


async def step(client: object,
               agents: list,
               timeout: int,
               loop: BaseEventLoop):
    tasks = []

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

        tasks.append(agent.process(event_fn))
    return await asyncio.wait(tasks, timeout=timeout)


def instrumentation(client: processor.QClient,
                    logger: Logger,
                    interval: int,
                    delta: int,
                    events_count: int,
                    pending_events: int):
    send_heartbeat(client.event, logger, int(interval * 1.5))
    send_timedelta(client.event, logger, delta, interval)
    send_metrics_count(client.event, logger, events_count)
    send_pending_events_count(client.event, logger, events_count)


async def main_loop(cfg: Config,
                    logger: Logger,
                    transport_cls: Generic[T],
                    continue_fn: callable,
                    loop: BaseEventLoop):
    riemann = cfg.riemann
    transport = transport_cls(riemann.host, riemann.port)
    client = processor.QClient(transport)
    agents = create_agents(cfg.agents)
    executor = cfg.executor_class(max_workers=cfg.executors_count)
    loop.set_default_executor(executor)

    init(agents)

    while True:
        ts = time()
        (done, pending) = await step(client,
                                     agents,
                                     timeout=cfg.interval * 1.5,
                                     loop=loop)

        te = time()
        td = te - ts
        instrumentation(client,
                        logger,
                        cfg.interval,
                        td,
                        len(client.queue.events),
                        len(pending))

        await processor.flush(client, transport, logger)
        if continue_fn():
            await asyncio.sleep(cfg.interval - int(td), loop=loop)
        else:
            logger.info("Stopping Oshino")
            break


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

    loop = create_loop()
    try:
        loop.run_until_complete(main_loop(cfg,
                                          logger,
                                          cfg.riemann.transport,
                                          forever,
                                          loop=loop))
    finally:
        loop.close()
