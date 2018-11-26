import aiohttp

from ..util import timer
from . import Agent


class Success(object):

    def __repr__(self):
        return "success"


class Failure(object):

    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return "failure"


class HttpAgent(Agent):

    def is_valid(self):
        checks = [("url" in self._data)
                  ]
        return super(HttpAgent, self).is_valid() and all(checks)

    @property
    def url(self):
        return self._data["url"]

    @property
    def headers(self):
        return self._data.get("headers", [])

    @property
    def cookies(self):
        return self._data.get("cookies", [])

    def translate_status(self, code):
        if code in [200, 201, 202, 204, 205, 206]:
            return Success()
        else:
            return Failure(code)

    async def process(self, event_fn):
        logger = self.get_logger()
        ts = timer()
        state = None
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                state = self.translate_status(resp.status)
        te = timer()
        span = int(te - ts)
        logger.debug("Request to {url} returned status code {code}(as {state})"
                     "in {span} milliseconds.".format(url=self.url,
                                                      code=resp.status,
                                                      state=state,
                                                      span=span))

        event_fn(service=self.prefix + "health",
                 metric_f=span,
                 state=str(state),
                 description=self.url)
