import asyncio
import threading

from copy import copy

from logbook import Logger
from concurrent.futures import ThreadPoolExecutor

from riemann_client.client import QueuedClient


logger = Logger("Processor")


class AugmentFixture(object):

    def apply_augment(self, data):
        def process_async():
            if "service" not in data:
                return []

            loop = asyncio.get_event_loop()

            key = data["service"]
            blocking_tasks = []
            if key in self.augments:
                subscribers = self.augments[key]

                def execute_in_thread(sub):
                    def wrapped():
                        return sub.send(data)
                    logger.debug("Registering in executor")
                    return loop.run_in_executor(None, wrapped)

                tasks = [execute_in_thread(sub)
                         for sub in subscribers]

                blocking_tasks += tasks

            logger.debug("Giving away blocking tasks")
            return blocking_tasks
        return process_async

    async def consume_augments(self, timeout=0.5):
        futures = [fut
                   for t in self.tasks
                   for fut in t()]

        logger.debug("Futures to be consumed: {0}".format(futures))

        if len(futures) > 0:
            return await asyncio.wait(futures, timeout=timeout)


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

    await client.consume_augments()
    asyncio.ensure_future(process_async(future))
    await future
    return future.result()


def register_augment(client, key, augment_fn, logger):
    if key not in client.augments:
        client.augments[key] = []

    def generator():
        while True:
            logger.debug("Waiting for event for {0}".format(augment_fn))
            event = yield

    g = generator()
    next(g)
    augment_fn(client, g)

    client.augments[key].append(g)
