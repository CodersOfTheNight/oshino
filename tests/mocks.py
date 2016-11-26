class MockClient(object):

    def __init__(self):
        self.events = []

    def event(self, *args, **kwargs):
        self.events.append((args, kwargs))

    def flush(self):
        self.events = []


class MockTransport(object):

    def __init__(self, broken=False):
        self.connected = False
        self.broken = broken

    def connect(self):
        if self.broken:
            raise ConnectionRefusedError
        self.connected = True

    def disconnect(self):
        self.connected = False
