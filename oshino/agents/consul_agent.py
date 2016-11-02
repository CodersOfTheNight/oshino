import aiohttp
from . import Agent


class ConsulAgent(Agent):

    @property
    def leader_url(self):
        return "http://{host}:{port}/v1/status/leader".format(host=self.host,
                                                              port=self.port)

    @property
    def services_url(self):
        return ("http://{host}:{port}/v1/catalog/services"
                .format(host=self.host,
                        port=self.port))

    @property
    def nodes_url(self):
        return ("http://{host}:{port}/v1/catalog/nodes"
                .format(host=self.host,
                        port=self.port))

    @property
    def health_url(self):
        return ("http://{host}:{port}/v1/health/service/"
                .format(host=self.host,
                        port=self.port))

    async def get_json(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    @property
    async def services(self):
        return await self.get_json(self.services_url)

    @property
    async def nodes(self):
        return await self.get_json(self.nodes_url)

    @property
    def host(self):
        return self._data.get("host", "localhost")

    @property
    def port(self):
        return int(self._data.get("port", 8500))

    async def process(self, event_fn, logger):
        services = await self.services
        logger.debug("Got services: {0}".format(services))

        nodes = await self.nodes
        logger.debug("Got nodes: {0}".format(nodes))
