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
        self.apply_augment(**data)
        super(QClient, self).event(**data)


def flush(client, transport, logger):
    try:
        transport.connect()
        client.flush()
        transport.disconnect()
    except ConnectionRefusedError as ce:
        logger.warn(ce)


def register_augment(client, key, generator, logger):
    if key not in client.augments:
        client.augments[key] = []

    next(generator)

    generator.send(client)
    client.augments[key].append(generator)
