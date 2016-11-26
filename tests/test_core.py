import logging

from pytest import mark, fixture
from oshino.core import send_heartbeat, send_timedelta, send_metrics_count
from oshino.config import AgentConfig, Config
from oshino.core.heart import (step,
                               instrumentation,
                               flush_riemann,
                               create_agents,
                               init)
from oshino.agents.test_agent import StubAgent

logger = logging.getLogger(__name__)


class MockClient(object):

    def __init__(self):
        self.events = []

    def event(self, *args, **kwargs):
        self.events.append((args, kwargs))

    def flush(self):
        self.events = []


class MockTransport(object):

    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False


@fixture
def stub_agent():
    return StubAgent({}), AgentConfig({})


@fixture
def mock_client():
    return MockClient()


@fixture
def mock_transport():
    return MockTransport()


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
    async def test_step(self, stub_agent, mock_client):
        await step(mock_client, [stub_agent])
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

    def test_agents_creation(self, base_config):
        result = create_agents(base_config)
        assert len(result) == 1
        agent, cfg = result[0]
        assert isinstance(agent, StubAgent)
        assert isinstance(cfg, AgentConfig)

    def test_init(self, stub_agent):
        init([stub_agent])
