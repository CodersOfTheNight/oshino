from pytest import fixture
from .mocks import MockClient, MockTransport


@fixture
def mock_client():
    return MockClient()


@fixture
def mock_transport():
    return MockTransport()


@fixture
def broken_transport():
    return MockTransport(broken=True)
