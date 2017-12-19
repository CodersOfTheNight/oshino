import asyncio
import sys
import logbook

from time import time
from typing import TypeVar, Generic
from asyncio import BaseEventLoop

from logbook import Logger, StreamHandler
from raven.handlers.logbook import SentryHandler
from raven import Client as SentryClient
from raven.exceptions import InvalidDsn
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
    return list(map(lambda x: (x.instance, x),
                    filter(lambda x: x.is_valid(), agents_cfg)))


def register_augments(client: processor.QClient,
                      augments_cfg: list,
                      logger: Logger):
    for augment in augments_cfg:
        if not augment.is_valid():
            logger.warn("Augment '{0}' failed to pass validation"
                        .format(augment))
            continue

        inst = augment.instance

        processor.register_augment(client, augment.key, inst.activate, logger)


def init(agents: list):
    for agent, _ in agents:
        agent.on_start()


async def step(client: object,
               agents: list,
               timeout: int,
               loop: BaseEventLoop):
    tasks = []

    for agent, agent_cfg in agents:
        tags = agent_cfg.tags

        if agent.lazy and not agent.ready:
            continue

        def event_fn(**kwargs):
            if "tags" in kwargs:
                for tag in tags:
                    kwargs["tags"].append(tag)
            else:
                kwargs["tags"] = tags

            if "time" not in kwargs:
                kwargs["time"] = int(time())

            client.event(**kwargs)

        tasks.append(agent.pull_metrics(event_fn))
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
    register_augments(client, cfg.augments, logger)
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

    client.on_stop()


def start_loop(cfg: Config, noop=False):
    handlers = []
    handlers.append(StreamHandler(sys.stdout, level=cfg.log_level))
    logger = Logger("Heart")
    logger.info("Initializing Oshino v{0}".format(get_version()))
    logger.info("Running forever in {0} seconds interval. Press Ctrl+C to exit"
                .format(cfg.interval))
    if cfg.sentry_dsn:
        try:
            client = SentryClient(cfg.sentry_dsn)
            handlers.append(SentryHandler(client,
                                          level=logbook.ERROR,
                                          bubble=True))
        except InvalidDsn:
            logger.warn("Invalid Sentry DSN '{0}' providen. Skipping"
                        .format(cfg.sentry_dsn))

    setup = NestedSetup(handlers)
    setup.push_application()

    loop = create_loop()
    try:
        loop.run_until_complete(main_loop(cfg,
                                          logger,
                                          cfg.riemann.transport(noop),
                                          forever,
                                          loop=loop))
    finally:
        loop.close()
