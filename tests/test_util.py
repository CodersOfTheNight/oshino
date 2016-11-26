from oshino.util import dynamic_import
from oshino.agents.test_agent import StubAgent


def test_dynamic_import_sucessful():
    agent = dynamic_import("oshino.agents.test_agent.StubAgent")
    assert agent == StubAgent
