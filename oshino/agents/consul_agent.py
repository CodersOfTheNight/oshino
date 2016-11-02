import aiohttp

from functools import partial

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
        def health(host, port, service_name):
            return ("http://{host}:{port}/v1/health/service/{service}"
                    .format(host=host,
                            port=port,
                            service=service_name))

        return partial(health, self.host, self.port)

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

    async def health(self, service_name):
        return await self.get_json(self.health_url(service_name))

    @property
    def host(self):
        return self._data.get("host", "localhost")

    @property
    def port(self):
        return int(self._data.get("port", 8500))

    async def process(self, event_fn):
        logger = self.get_logger()
        services = await self.services
        logger.debug("Got services: {0}".format(services))

        nodes = await self.nodes
        logger.debug("Got nodes: {0}".format(nodes))
        for service_name, _ in services.items():
            health_nodes = await self.health(service_name)
            for node in health_nodes:
                logger.debug("HealthInfo: {0}".format(node))
                ok = all([check["Status"] == "passing" for check in node["Checks"]])
                logger.debug("Node is Ok? {0}".format(ok))
                event_fn(metric_f=1.0 if ok else 0.0,
                         service=self.prefix + service_name,
                         host=node["Node"]["Node"])
