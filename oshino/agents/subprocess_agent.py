import re
import json
import asyncio

from functools import partial
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


def split_transform(m, logger, metric_sep="="):

    try:
        key, val = m.split(metric_sep, 1)
        return key.strip(), float(val.strip())
    except Exception as ex:
        logger.warn("Failed to parse '{0}' with '{1}' as sep, Reason: {2}"
                    .format(m, metric_sep, ex))
        return None


def regex_transform(m, logger):
    raw = re.match(
            r"(?P<key>(\w|[.-])+)\s*[:=]\s*(?P<val>(-?\d+([.]\d{1,2})?))",
            m
    )

    if raw:
        return raw.group("key"), float(raw.group("val"))
    else:
        return None


def json_transform(m, logger, selector):
    raw = json.loads(m)
    return selector, raw[selector]


def is_parsed(m):
    return m is not None


class StdoutAgent(Agent):
    @property
    def cmd(self):
        return self._data["cmd"]

    @property
    def args(self):
        return self._data.get("args", {})

    @property
    def transform_fn(self):
        local_fn = self._data.get("local-transform", None)
        if local_fn:
            raw = "oshino.agents.subprocess_agent.{0}".format(local_fn)
        else:
            raw = self._data.get(
                    "transform-fn",
                    "oshino.agents.subprocess_agent.split_transform"
            )

        mod, func = raw.rsplit(".", 1)
        m = __import__(mod, fromlist=[func])
        return getattr(m, func)

    async def process(self, event_fn):
        logger = self.get_logger()
        proc = await asyncio.create_subprocess_shell(
                self.cmd,
                stdout=asyncio.subprocess.PIPE
        )

        def strip(x):
            return x.strip()
        stdout, stderr = await proc.communicate()
        content = stdout.decode().strip()
        transform = partial(self.transform_fn, logger=logger, **self.args)
        metrics = filter(
                is_parsed,
                map(transform, map(strip, content.split("\n")))
        )

        for key, val in metrics:
            event_fn(service=self.prefix + key,
                     state="ok",
                     metric_f=float(val))
