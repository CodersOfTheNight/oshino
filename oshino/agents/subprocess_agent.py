import asyncio

from . import Agent
from asyncio.subprocess import Pipe


class SubprocessAgent(Agent):

    @property
    def script(self):
        return self._data["script"]

    def is_valid(self):
        return "script" in self._data

    async def process(self, event_fn):
        logger = self.get_logger()

        proc = await asyncio.create_subprocess_exec(self.script,
                                                    stdout=PIPE)
        stdout, stderr = await proc.communicate()
        state = "ok" if proc.returncode == 0 else "failure"
        event_fn(self.prefix,
                 state=state,
                 metric_f=1.0,
                 description="Stdout: {0}, Stderr: {1}".format(stdout, stderr)
                 )
