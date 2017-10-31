from time import time

from oshino.config import TagMixin


class AugmentBase(TagMixin):
    def __init__(self, data):
        self._data = data

    def activate(self, client, g):
        pass

    def is_valid(self):
        return True

    @property
    def name(self):
        return self._data["name"].lower().replace(" ", "-")

    @property
    def prefix(self):
        return "{0}.".format(self.name)

    @property
    def key(self):
        return self._data["key"]

    def send_event(self, client, **kwargs):
        tags = self.tags
        if "tags" in kwargs:
            for tag in tags:
                kwargs["tags"].append(tag)
        else:
            kwargs["tags"] = tags

        if "time" not in kwargs:
            kwargs["time"] = int(time())

        client.event(**kwargs)


class InvalidAugment(AugmentBase):
    """
    Only for Testing purposes
    """

    def is_valid(self):
        return False

    def activate(self, client, g):
        raise RuntimeError("We shouldn't get here!")
