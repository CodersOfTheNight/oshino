from copy import copy

from riemann_client.transport import BlankTransport, RiemannError

from oshino.core.processor import AugmentFixture


class MockClient(AugmentFixture):

    def __init__(self, transport=None):
        self.events = []
        self.augments = {}
        self.tasks = []
        self.transport = transport

    def event(self, **kwargs):
        self.tasks.append(self.apply_augment(copy(kwargs)))
        self.events.append(kwargs)

    def clear_queue(self):
        self.events = []

    def flush(self):
        response = self.transport.send(self.events)
        self.clear_queue()
        return response


class MockTransport(BlankTransport):

    def __init__(self, host=None, port=None, broken=False):
        self.connected = False
        self.broken = broken
        self.sneaky = False

    def connect(self):
        if self.broken:
            raise ConnectionRefusedError
        self.connected = True

    def disconnect(self):
        self.connected = False

    def send(self, message):
        if self.broken or self.sneaky:
            raise RiemannError

        return True
