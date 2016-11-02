class Agent(object):

    def __init__(self, cfg):
        self._data = cfg

    @property
    def prefix(self):
        return "{0}.".format(self._data["name"])

    async def process(self, event_fn, logger):
        pass

    def is_valid(self):
        return True
