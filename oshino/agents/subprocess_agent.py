import asyncio
import importlib

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


def split_transform(m):
    try:
        key, val = m.split("=", 1)
        return key.strip(), val.strip()
    except:
        return None


def is_parsed(m):
    return m is not None


class StdoutAgent(Agent):
    @property
    def cmd(self):
        return self._data["cmd"]

    @property
    def metric_separator(self):
        return self._data.get("metric-separator", "=")

    @property
    def transform_fn(self):
        raw = self.data.get("transform-fn", "split_transform")
        return importlib.import_module(raw)

    async def process(self, event_fn):
        proc = await asyncio.create_subprocess_shell(
                self.cmd,
                stdout=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        content = stdout.decode().strip()
        transform = self.transform_fn
        metrics = filter(is_parsed, map(transform, content.split("\n")))

        for key, val in metrics:
            event_fn(service=self.prefix + key,
                     state="ok",
                     metric_f=float(val))
