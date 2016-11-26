import mock
import logbook

from pytest import fixture

from oshino.config import Config, RiemannConfig
from oshino.agents.test_agent import StubAgent
from oshino import version
from oshino import get_version


@fixture
def base_config():
    return Config({"riemann": {"host": "localhost",
                               "port": 5555
                               },
                   "interval": 5,
                   "agents": [{"name": "test-agent",
                               "module": "oshino.agents.test_agent.StubAgent",
                               "tag": "test"
                               }
                              ]
                   })


@fixture
def incomplete_config():
    return Config({})


def test_version_formatting():
    app_version = get_version()
    assert app_version.split(".") == list(map(lambda x: str(x),
                                              version.VERSION))


@mock.patch("oshino.version.VERSION", (1, 2, 3))
def test_version_number():
    assert get_version() == "1.2.3"


class TestBase(object):

    def test_base_config_interval(self, base_config):
        assert base_config.interval == 5

    def test_default_log_level(self, base_config):
        assert base_config.log_level == logbook.INFO


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


class TestAgents(object):

    def test_agent_loader(self, base_config):
        agents = base_config.agents
        assert len(agents) == 1
        obj = agents[0].instance
        assert isinstance(obj, StubAgent)

    def test_agent_tag(self, base_config):
        agents = base_config.agents
        assert agents[0].tag == "test"
