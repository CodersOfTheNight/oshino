from abc import ABC, abstractmethod

from oshino.util import current_ts

from logbook import Logger


class Agent(ABC):

    def __init__(self, cfg):
        self._data = cfg
        self._last_run = current_ts()

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

    @abstractmethod
    async def process(self, event_fn):
        """
        Each agent must implement this one to provide actual logic
        """
        pass

    def is_valid(self):
        return "name" in self._data

    async def pull_metrics(self, event_fn):
        """
        Method called by core.
        Should not be overwritten.
        """
        if self.lazy and not self.ready:
            return None

        result = await self.process(event_fn)
        self._last_run = current_ts()
        return result

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
        logger = self.get_logger()
        now = current_ts()
        logger.trace("Current time: {0}".format(now))
        logger.trace("Last Run: {0}".format(self._last_run))
        delta = (now - self._last_run)
        logger.trace("Delta: {0}, Interval: {1}"
                     .format(delta, self.interval * 1000))
        return delta > self.interval * 1000

    @property
    def interval(self):
        """
        By default, lazy agents expects to have some kind of time interval.
        `ready` output is calculated according to this interval.
        """
        return self._data["interval"]
