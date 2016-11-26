from . import Agent


class StubAgent(Agent):

    def is_valid(self):
        return True

    async def process(self, event_fn):
        event_fn(metric_f=1.0,
                 service="test",
                 tags=["test"])
