import os
import yaml

from jinja2 import Template
from .util import dynamic_import


class ConfigBase(object):

    """
    Base config class
    """

    def is_valid(self):
        return True


class RiemannConfig(ConfigBase):

    """
    Riemann Config object
    """

    def __init__(self, cfg):
        self._data = cfg

    @property
    def host(self):
        return self._data.get("host", "localhost")

    @property
    def port(self):
        return int(self._data.get("port", 5555))

    @staticmethod
    def default():
        return RiemannConfig({})


class AgentConfig(ConfigBase):

    """
    Config for setuping agent
    """

    def __init__(self, cfg):
        self._data = cfg
        self._instance = None

    @property
    def name(self):
        return self._data["name"]

    @property
    def module(self):
        return self._data["module"]

    @property
    def instance(self):
        if self._instance is None:
            self._instance = dynamic_import(self.module)(self._data)
        return self._instance

    def is_valid(self):
        return self.instance.is_valid()


class Config(ConfigBase):

    """
    Config object
    """

    def __init__(self, cfg):
        self._data = cfg
        self.is_valid()

    def is_valid(self):
        checks = ([self.riemann.is_valid] +
                  list(map(lambda x: x.is_valid, self.agents)))
        return all([c() for c in checks])

    @property
    def riemann(self):
        if "riemann" in self._data:
            return RiemannConfig(self._data["riemann"])
        else:
            return RiemannConfig.default()

    @property
    def interval(self):
        return self._data["interval"]

    @property
    def agents(self):
        return [AgentConfig(a) for a in self._data.get("agents", [])]


def load(config_file):
    """
    Processes and loads config file.
    """
    with open(config_file, "r") as f:

        def env_get():
            return dict(os.environ)
        tmpl = Template(f.read())
        return Config(yaml.load(tmpl.render(**env_get())))
