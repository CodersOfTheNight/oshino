from pytest import mark
from oshino.run import main


@mark.integration
@mark.skip("It runs forever")
def test_startup():
    main(("--config", "tests/data/test_config.yml", ))
