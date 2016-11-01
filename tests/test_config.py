from pytest import fixture

from oshino.config import Config, RiemannConfig


@fixture
def base_config():
    return Config({"riemann": {"host": "localhost",
                               "port": 5555
                               },
                   "interval": 5
                   })


@fixture
def incomplete_config():
    return Config({})


class TestBase(object):

    def test_base_config_interval(self, base_config):
        assert base_config.interval == 5


class TestRiemann(object):

    def test_base_config_get_riemann(self, base_config):
        assert isinstance(base_config.riemann, RiemannConfig)

    def test_incomplete_config_get_riemann(self, incomplete_config):
        assert isinstance(incomplete_config.riemann, RiemannConfig)
