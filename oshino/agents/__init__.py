from logbook import Logger


class Agent(object):

    def __init__(self, cfg):
        self._data = cfg

    def on_start(self):
        pass

    def on_stop(self):
        pass

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
        return "name" in self._data

    @property
    def lazy(self):
        """
        Agents with flag `lazy` gives data when they want to,
        not when they are requested for.
        """
        return self._data.get("lazy", False)

    @property
    def ready(self):
        """
        Function used when agent is `lazy`.
        It is being processed only when `ready` condition is satisfied
        """
        return False
