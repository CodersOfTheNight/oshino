from pytest import mark, raises
from oshino.run import main
from mock import patch


@mark.integration
@patch("oshino.core.heart.forever", lambda: False)
def test_startup():
    with raises(SystemExit):
        main(("--config", "tests/data/test_config.yml", ))
