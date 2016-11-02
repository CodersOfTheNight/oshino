from logbook import Logger


class Agent(object):

    def __init__(self, cfg):
        self._data = cfg

    @property
    def prefix(self):
        return "{0}.".format(self._data["name"])

    def get_logger(self):
        return Logger(self.__class__.__name__)

    async def process(self, event_fn):
        pass

    def is_valid(self):
        return True
