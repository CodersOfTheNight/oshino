import asyncio

from riemann_client.client import QueuedClient


class AugmentFixture(object):

    def apply_augment(self, **data):
        async def process_async(future):
            if "service" not in data:
                return

            key = data["service"]
            if key in self.augments:
                subscribers = self.augments[key]
                for sub in subscribers:
                    sub.send(data)
            future.set_result(True)
        return process_async

    async def consume_augments(self, timeout=0.5):
        futures = []
        for task in self.tasks:
            future = asyncio.Future()
            asyncio.ensure_future(task(future))
            futures.append(future)


        if len(futures) > 0:
            return await asyncio.wait(futures, timeout=timeout)


class QClient(QueuedClient, AugmentFixture):
    def __init__(self, *args, **kwargs):
        super(QClient, self).__init__(*args, **kwargs)
        self.augments = {}
        self.tasks = []

    def event(self, **data):
        self.tasks.append(self.apply_augment(**data))
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


def register_augment(client, key, generator, logger):
    if key not in client.augments:
        client.augments[key] = []

    next(generator)

    generator.send(client)
    client.augments[key].append(generator)
