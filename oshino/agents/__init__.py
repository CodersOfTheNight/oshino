class Agent(object):

    def __init__(self, cfg):
        self._data = cfg

    async def process(self, event_fn, logger):
        pass

    def is_valid(self):
        return True
