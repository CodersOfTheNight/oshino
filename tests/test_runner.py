from pytest import mark
from oshino.run import main


@mark.integration
def test_startup():
    main(("--config", "tests/data/test_config.yml", ))
