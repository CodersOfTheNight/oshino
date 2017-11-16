import asyncio

from pytest import mark, raises
from oshino.run import main
from mock import patch


def create_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


@mark.integration
@patch("oshino.core.heart.forever", lambda: False)
@patch("oshino.core.heart.create_loop", create_loop)
def test_startup():
    with raises(SystemExit):
        main(("--config", "tests/data/test_config.yml", "--noop"))
