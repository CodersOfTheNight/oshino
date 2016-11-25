import asyncio

from . import Agent


class SubprocessAgent(Agent):

    @property
    def script(self):
        return self._data["script"]

    def is_valid(self):
        return (super(SubprocessAgent, self).is_valid()
                and "script" in self._data)

    async def process(self, event_fn):
        proc = await asyncio.create_subprocess_shell(self.script)
        exitcode = await proc.wait()
        state = "ok" if exitcode == 0 else "failure"
        event_fn(service=self.prefix + "shell",
                 state=state,
                 metric_f=1.0,
                 description="Exit code: {0}".format(exitcode)
                 )
