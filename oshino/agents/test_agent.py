import asyncio

from . import Agent


class StubAgent(Agent):

    def is_valid(self):
        return True

    async def process(self, event_fn):
        event_fn(metric_f=1.0,
                 service="test",
                 tags=["test"])


class LaggingAgent(Agent):

    def __init__(self, cfg, lag):
        super(LaggingAgent, self).__init__(cfg)
        self.lag = lag

    def is_valid(self):
        return True

    async def process(self, event_fn):
        await asyncio.sleep(self.lag)
        event_fn(metric_f=1.0,
                 service="lagging_test",
                 tags=["test"])
