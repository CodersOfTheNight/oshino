import asyncio

from pytest import mark
from oshino.core.heart import start_loop
from oshino.config import load
from mock import patch


def create_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


@mark.integration
@patch("oshino.core.heart.forever", lambda: False)
@patch("oshino.core.heart.create_loop", create_loop)
def test_clean_shutdown():
    cfg = load("tests/data/test_config.yml")
    start_loop(cfg)
