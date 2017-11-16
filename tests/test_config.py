import mock
import logbook

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from pytest import fixture

from riemann_client.transport import (TCPTransport,
                                      BlankTransport,
                                      TLSTransport)

from oshino.config import Config, RiemannConfig, load, AgentConfig
from oshino.agents.test_agent import StubAgent
from oshino.augments.stats import SimpleMovingAverage
from oshino import version
from oshino import get_version


@fixture
def base_config():
    return Config({
        "riemann": {
            "host": "localhost",
            "port": 5555
        },
        "interval": 5,
        "sentry-dsn": "http://test:test@sentry.io",
        "agents": [
            {
                "name": "test-agent",
                "module": "oshino.agents.test_agent.StubAgent",
                "tag": "test"
            }
        ],
       "augments": [
            {
                "name": "moving average",
                "key": "cpu",
                "module": "oshino.augments.stats.SimpleMovingAverage",
                "step": 5,
                "tag": "sma"
            }
        ]
    })


@fixture
def incomplete_config():
    return Config({})


class TestVersion(object):

    def test_version_formatting(self):
        app_version = get_version()
        assert app_version.split(".") == list(map(lambda x: str(x),
                                                  version.VERSION))

    @mock.patch("oshino.version.VERSION", (1, 2, 3))
    def test_version_number(self):
        assert get_version() == "1.2.3"


class TestBase(object):

    def test_base_config_interval(self, base_config):
        assert base_config.interval == 5

    def test_default_log_level(self, base_config):
        assert base_config.log_level == logbook.INFO

    def test_sentry_dsn(self, base_config):
        assert base_config.sentry_dsn == "http://test:test@sentry.io"

    def test_loading_config(self):
        cfg = load("tests/data/test_config.yml")
        assert isinstance(cfg, Config)

    def test_default_executor_class(self, base_config):
        obj = base_config.executor_class()
        assert isinstance(obj, ThreadPoolExecutor)

    def test_custom_executor_class(self):
        cfg = load("tests/data/test_config.yml")
        obj = cfg.executor_class()
        assert isinstance(obj, ProcessPoolExecutor)


class TestRiemann(object):

    def test_base_config_get_riemann(self, base_config):
        assert isinstance(base_config.riemann, RiemannConfig)

    def test_incomplete_config_get_riemann(self, incomplete_config):
        obj = incomplete_config.riemann
        assert isinstance(obj, RiemannConfig)
        assert isinstance(obj._data, dict)

    def test_riemann_default_host(self, incomplete_config):
        assert incomplete_config.riemann.host == "localhost"

    def test_riemann_default_port(self, incomplete_config):
        assert incomplete_config.riemann.port == 5555

    def test_default_transport_class(self, base_config):
        assert base_config.riemann.transport(noop=False) == TCPTransport

    def test_noop_transport_class(self, base_config):
        assert base_config.riemann.transport(noop=True) == BlankTransport

    def test_tls_transport_class(self, base_config):
        # Hacking a bit >:)
        base_config._data["riemann"]["ca-certs"] = "/tmp/ca_bundle.pem"
        klass = base_config.riemann.transport()
        transport = klass()
        assert transport.ca_certs == "/tmp/ca_bundle.pem"
        assert isinstance(transport, TLSTransport)


class TestAgents(object):

    def test_agent_loader(self, base_config):
        agents = base_config.agents
        assert len(agents) == 1
        obj = agents[0].instance
        assert isinstance(obj, StubAgent)

    def test_single_tag(self):
        cfg = {
            "name": "test-agent",
            "module": "oshino.agents.test_agent.StubAgent",
            "tag": "test"
        }
        agent_cfg = AgentConfig(cfg)
        assert agent_cfg.tag == "test"

    def test_single_w_multiple_tags(self):
        cfg = {
            "name": "test-agent",
            "module": "oshino.agents.test_agent.StubAgent",
            "tag": "test",
            "tags": ["test2", "test3"]
        }
        agent_cfg = AgentConfig(cfg)
        assert agent_cfg.tag == "test"
        assert set(agent_cfg.tags) == set(["test", "test2", "test3"])

    def test_multiple_wo_single_tags(self):
        cfg = {
            "name": "test-agent",
            "module": "oshino.agents.test_agent.StubAgent",
            "tags": ["test2", "test3"]
        }
        agent_cfg = AgentConfig(cfg)
        assert set(agent_cfg.tags) == set(["test2", "test3"])


class TestAugments(object):
    def test_config_is_valid(self, base_config):
        augments = base_config.augments
        assert all([augment.is_valid() for augment in augments])


    def test_augment_loader(self, base_config):
        augments = base_config.augments
        assert len(augments) == 1
        obj = augments[0].instance
        assert isinstance(obj, SimpleMovingAverage)

    def test_augment_tag(self, base_config):
        augments = base_config.augments
        assert augments[0].tag == "sma"
