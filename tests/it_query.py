import time
import logging

import pytest
import wait

from riemann_client.client import Client

from oshino.config import load

logger = logging.getLogger(__name__)


def test_query_healthcheck():
    cfg = load("config.yaml")
    riemann = cfg.riemann
    transport_cls = cfg.riemann.transport
    transport = transport_cls(riemann.host, riemann.port)
    logger.info("Waiting for Riemann")

    #wait.tcp.open(riemann.port, host=riemann.host)
    fail_cnt = 0
    while True:
        try:
            with Client(transport) as client:
                results = client.query("tagged \"healthcheck\"")
                assert len(results) == 0
                time.sleep(5)
                assert len(results) > 0
        except ConnectionError:
            fail_cnt += 1
            time.sleep(0.01)

        if fail_cnt > 5:
            pytest.fail("Too many connection errors has occured while trying to reach Riemann")
