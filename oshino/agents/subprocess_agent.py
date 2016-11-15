import asyncio

from . import Agent
from asyncio.subprocess import PIPE


class SubprocessAgent(Agent):

    @property
    def script(self):
        return self._data["script"]

    def is_valid(self):
        return "script" in self._data

    async def process(self, event_fn):
        logger = self.get_logger()
        proc = await asyncio.create_subprocess_shell(self.script)
        exitcode = await proc.wait()
        state = "ok" if exitcode == 0 else "failure"
        event_fn(service=self.prefix,
                 state=state,
                 metric_f=1.0
                 )
