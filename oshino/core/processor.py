import asyncio

from riemann_client.client import QueuedClient


class AugmentFixture(object):
    def apply_augment(self, **data):
        if "service" not in data:
            return

        key = data["service"]
        if key in self.augments:
            subscribers = self.augments[key]
            for sub in subscribers:
                sub.send(data)


class QClient(QueuedClient, AugmentFixture):
    def __init__(self, *args, **kwargs):
        super(QClient, self).__init__(*args, **kwargs)
        self.augments = {}

    def event(self, **data):
        super(QClient, self).event(**data)

    async def augmented_event(self, **data):
        await self.apply_augment(**data)
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


def register_augment(client, key, generator, logger):
    if key not in client.augments:
        client.augments[key] = []

    next(generator)

    generator.send(client)
    client.augments[key].append(generator)
