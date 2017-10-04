from riemann_client.client import QueuedClient


class QClient(QueuedClient):
    def __init__(self, *args, **kwargs):
        super(QClient, self).__init__(*args, **kwargs)
        self.augments = []

    def event(self, **data):
        if data['service'] in self.augments:
            subscribers = self.augments[data["service"]]
            for sub in subscribers:
                sub.send(**data)
        super(QClient, self).event(**data)


def flush(client, transport, logger):
    try:
        transport.connect()
        client.flush()
        transport.disconnect()
    except ConnectionRefusedError as ce:
        logger.warn(ce)


def register_augment(client, key, generator, logger):
    pass
