import logging

from pytest import mark, fixture
from oshino.core import send_heartbeat, send_timedelta, send_metrics_count
from oshino.config import AgentConfig, Config
from oshino.core.heart import (step,
                               instrumentation,
                               flush_riemann,
                               create_agents,
                               init,
                               forever)
from oshino.agents.test_agent import StubAgent
from .fixtures import mock_transport, mock_client, broken_transport

logger = logging.getLogger(__name__)


@fixture
def stub_agent():
    return StubAgent({}), AgentConfig({})


@fixture
def base_config():
    return Config({"agents": [{"name": "test-agent",
                               "module": "oshino.agents.test_agent.StubAgent",
                               }
                              ]
                   })


class TestInstrumentation(object):

    def test_heartbeat(self):
        reached = False

        def stub_event_fn(**kwargs):
            nonlocal reached
            assert kwargs["ttl"] == 10
            reached = True

        send_heartbeat(stub_event_fn, logger, 10)
        assert reached

    def test_td_ok(self):
        reached = False

        def stub_event_fn(**kwargs):
            nonlocal reached
            assert kwargs["state"] == "ok"
            reached = True

        send_timedelta(stub_event_fn, logger, 10, 100)
        assert reached

    def test_td_too_long(self):
        reached = False

        def stub_event_fn(**kwargs):
            nonlocal reached
            assert kwargs["state"] == "error"
            reached = True

        send_timedelta(stub_event_fn, logger, 110, 100)
        assert reached

    def test_metrics_count(self):
        reached = False

        def stub_event_fn(**kwargs):
            nonlocal reached
            reached = True

        send_metrics_count(stub_event_fn, logger, 10)
        assert reached


class TestHeart(object):

    @mark.asyncio
    async def test_step(self, stub_agent, mock_client, event_loop):
        await step(mock_client, [stub_agent], loop=event_loop)
        assert len(mock_client.events) == 1

    def test_instrumentation(self, mock_client):
        instrumentation(mock_client, logger, 0, 0, 0)
        assert len(mock_client.events) == 3

    def test_flush(self, mock_client, mock_transport):
        assert len(mock_client.events) == 0
        mock_client.event()
        assert len(mock_client.events) == 1
        flush_riemann(mock_client, mock_transport, logger)
        assert len(mock_client.events) == 0
        assert not mock_transport.connected

    def test_flush_w_error(self, mock_client, broken_transport):
        flush_riemann(mock_client, broken_transport, logger)

    def test_agents_creation(self, base_config):
        result = create_agents(base_config.agents)
        assert len(result) == 1
        agent, cfg = result[0]
        assert isinstance(agent, StubAgent)
        assert isinstance(cfg, AgentConfig)

    def test_init(self, stub_agent):
        init([stub_agent])

    def test_forever(self):
        assert all([forever() for i in range(0, 10)])
