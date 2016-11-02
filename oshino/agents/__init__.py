from logbook import Logger


class Agent(object):

    def __init__(self, cfg):
        self._data = cfg

    @property
    def name(self):
        return self._data["name"].lower().replace(" ", "-")

    @property
    def prefix(self):
        return "{0}.".format(self.name)

    def get_logger(self):
        return Logger(self.__class__.__name__)

    async def process(self, event_fn):
        pass

    def is_valid(self):
        return True
