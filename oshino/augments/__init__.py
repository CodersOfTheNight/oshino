from time import time

class AugmentBase(object):
    def __init__(self, data):
        self._data = data

    def activate(self, client, g):
        pass

    def send_event(self, client, **kwargs):
        tags = [self.tag] if self.tag else []
        if "tags" in kwargs:
            for tag in tags:
                kwargs["tags"].append(tag)
        else:
            kwargs["tags"] = tags

        if "time" not in kwargs:
            kwargs["time"] = int(time())

        client.event(**kwargs)


def consume(q):
    while not q.empty():
        yield q.get()
