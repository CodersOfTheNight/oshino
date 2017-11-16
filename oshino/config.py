import os
import yaml
import logbook
import riemann_client.transport

from functools import partial

from riemann_client.transport import BlankTransport, TLSTransport, TCPTransport

from jinja2 import Template
from .util import dynamic_import


class ConfigBase(object):

    """
    Base config class
    """

    def is_valid(self):
        return True


class InstanceMixin(object):
    """
    Mixin used for configs which are loaded dynamically
    """
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


class TagMixin(object):
    """
    Mixin used for adding tag functionallity to configs
    """

    @property
    def tag(self):
        return self._data.get("tag", None)

    @property
    def tags(self):
        return self._data.get("tags", []) + ([self.tag] if self.tag else [])


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

    @property
    def ca_certs(self):
        return self._data.get("ca-certs", None)

    def transport(self, noop=False):
        if noop:
            return BlankTransport

        raw = self._data.get("transport", None)
        if raw:  # Transport is defined
            return getattr(riemann_client.transport, raw)
        elif self.ca_certs:
            return partial(TLSTransport, ca_certs=self.ca_certs)
        else:
            return TCPTransport


class AgentConfig(InstanceMixin, TagMixin):

    """
    Config for setuping agent
    """

    def __init__(self, cfg):
        self._data = cfg
        self._instance = None


class AugmentConfig(InstanceMixin, TagMixin):

    """
    Config for setuping augment
    """

    def __init__(self, cfg):
        self._data = cfg
        self._instance = None

    @property
    def key(self):
        return self._data["key"]


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
    def log_level(self):
        raw = self._data.get("loglevel", "INFO").upper()
        return getattr(logbook, raw)

    @property
    def agents(self):
        return [AgentConfig(a) for a in self._data.get("agents", [])]

    @property
    def augments(self):
        return [AugmentConfig(a) for a in self._data.get("augments", [])]

    @property
    def sentry_dsn(self):
        return self._data.get("sentry-dsn", None)

    @property
    def executors_count(self):
        return self._data.get("executors-count", 10)

    @property
    def executor_class(self):
        raw = self._data.get(
                "executor",
                "concurrent.futures.ThreadPoolExecutor"
        )
        return dynamic_import(raw)


def load(config_file):
    """
    Processes and loads config file.
    """
    with open(config_file, "r") as f:

        def env_get():
            return dict(os.environ)
        tmpl = Template(f.read())
        return Config(yaml.load(tmpl.render(**env_get())))
