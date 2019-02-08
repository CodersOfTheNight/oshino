import time
import logging

import pytest
import wait

from riemann_client.client import Client

from oshino.config import load

logger = logging.getLogger(__name__)

def with_retry(fn):
    def wrapper(*args, **kwargs):
        for i in range(0, 10):
            try:
                result = fn(*args, **kwargs)
                return result
            except Exception as ex:
                time.sleep(1)
                continue
        pytest.fail("Retry limit reached")
    return wrapper


@with_retry
def test_query_healthcheck():
    cfg = load("config.yaml")
    riemann = cfg.riemann
    transport_cls = cfg.riemann.transport
    transport = transport_cls(riemann.host, riemann.port)
    logger.info("Waiting for Riemann")

    #wait.tcp.open(riemann.port, host=riemann.host)

    @with_retry
    def query():
        with Client(transport) as client:
            results = client.query("tagged \"healthcheck\"")
            assert len(results) == 0
            time.sleep(5)
            results = client.query("tagged \"healthcheck\"")
            assert len(results) > 0
