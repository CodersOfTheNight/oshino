import time

import pytest
import wait

from riemann_client.client import Client

from oshino.config import load


def test_query_healthcheck():
    cfg = load("config.yaml")
    riemann = cfg.riemann
    transport_cls = cfg.riemann.transport
    transport = transport_cls(riemann.host, riemann.port)
    print("Waiting for Riemann")

    wait.tcp.open(riemann.port, host=riemann.host)
    with Client(transport) as client:
        results = client.query("tagged \"healthcheck\"")
        assert len(results) == 0
        time.sleep(1000)
        assert len(results) > 0
