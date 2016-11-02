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

    @property
    def host(self):
        return self._data.get("host", "localhost")

    @property
    def port(self):
        return int(self._data.get("port", 8500))
