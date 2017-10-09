import asyncio

from copy import copy

from logbook import Logger
from concurrent.futures import ThreadPoolExecutor

from riemann_client.client import QueuedClient


logger = Logger("Processor")


class AugmentFixture(object):

    def apply_augment(self, data):
        async def process_async(executor):
            if "service" not in data:
                return []

            loop = asyncio.get_event_loop()

            key = data["service"]
            blocking_tasks = []
            if key in self.augments:
                subscribers = self.augments[key]

                def blocking():
                    for sub in subscribers:
                        sub.send(data)

                blocking_tasks.append(
                        loop.run_in_executor(executor, blocking)
                )
            return blocking_tasks
        return process_async

    async def consume_augments(self, executor, timeout=0.5):
        futures = [t(executor) for t in self.tasks]

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


async def flush(client, transport, executor, logger):
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

    await client.consume_augments(executor)
    asyncio.ensure_future(process_async(future))
    await future
    return future.result()


def register_augment(client, key, generator, logger):
    if key not in client.augments:
        client.augments[key] = []

    next(generator)

    generator.send(client)
    client.augments[key].append(generator)
