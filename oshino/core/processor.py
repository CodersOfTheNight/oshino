import asyncio
import threading

from copy import copy

from logbook import Logger
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from riemann_client.client import QueuedClient


logger = Logger("Processor")


class StopEvent(object):
    pass


class AugmentFixture(object):

    def apply_augment(self, data):
        if "service" not in data:
            return

        key = data["service"]
        subscribers = self.augments[key]
        for sub in subscribers:
            sub.put_nowait(data)

    def on_stop(self):
        logger.info("Stopping all augments")
        for _, subscribers in self.augments.items():
            for sub in subscribers:
                sub.put_nowait(StopEvent())


class QClient(QueuedClient, AugmentFixture):
    def __init__(self, *args, **kwargs):
        super(QClient, self).__init__(*args, **kwargs)
        self.augments = {}
        self.tasks = []

    def event(self, **data):
        self.tasks.append(self.apply_augment(copy(data)))
        super(QClient, self).event(**data)


async def flush(client, transport, logger):
    future = asyncio.Future()

    async def process_async(future):
        try:
            transport.connect()
            client.flush()
            transport.disconnect()

            future.set_result(True)
        except ConnectionRefusedError as ce:
            logger.warn(ce)

            future.set_result(False)

    asyncio.ensure_future(process_async(future))
    await future
    return future.result()


def register_augment(client, key, augment_fn, logger):
    if key not in client.augments:
        client.augments[key] = []

    loop = asyncio.get_event_loop()

    def generator(q):
        while True:
            logger.debug("Waiting for event for {0}".format(augment_fn))
            event = q.get()
            if isinstance(event, StopEvent):
                break
            yield event

    q = Queue()
    g = generator(q)
    def execute_in_thread(fn, client, g):
        fn(client, g)

    loop.run_in_executor(None, execute_in_thread, augment_fn, client, g)

    client.augments[key].append(q)
