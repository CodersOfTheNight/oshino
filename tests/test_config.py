from pytest import fixture

from oshino.config import Config, RiemannConfig


@fixture
def base_config():
    return Config({"riemann": {"host": "localhost",
                               "port": 5555
                               },
                   "interval": 5
                   })


def test_base_config_get_riemann(base_config):
    assert isinstance(base_config.riemann, RiemannConfig)


def test_base_config_interval(base_config):
    assert base_config.interval == 5
