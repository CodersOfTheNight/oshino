from time import time


class AugmentBase(object):
    def __init__(self, data):
        self._data = data

    def activate(self, client, g):
        pass

    @property
    def name(self):
        return self._data["name"].lower().replace(" ", "-")

    @property
    def prefix(self):
        return "{0}.".format(self.name)

    @property
    def key(self):
        return self._data["key"]

    @property
    def tag(self):
        return self._data.get("tag", None)

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


class InvalidAugment(AugmentBase):
    """
    Only for Testing purposes
    """

    def is_valid(self):
        return False

    def activate(self, client, g):
        raise RuntimeError("We shouldn't get here!")
