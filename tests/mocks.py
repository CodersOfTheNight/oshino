from riemann_client.transport import BlankTransport

from oshino.core.processor import AugmentFixture


class MockClient(AugmentFixture):

    def __init__(self):
        self.events = []
        self.augments = {}

    def event(self, **kwargs):
        self.apply_augment(**kwargs)
        self.events.append(kwargs)

    def flush(self):
        self.events = []


class MockTransport(BlankTransport):

    def __init__(self, host=None, port=None, broken=False):
        self.connected = False
        self.broken = broken

    def connect(self):
        if self.broken:
            raise ConnectionRefusedError
        self.connected = True

    def disconnect(self):
        self.connected = False
