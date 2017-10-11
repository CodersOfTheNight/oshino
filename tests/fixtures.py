from concurrent.futures import ThreadPoolExecutor

from pytest import fixture

from .mocks import MockClient, MockTransport



@fixture
def mock_client(request):
    client = MockClient()
    request.addfinalizer(client.on_stop)
    return client


@fixture
def mock_transport():
    return MockTransport()


@fixture
def broken_transport():
    return MockTransport(broken=True)

@fixture(scope="session")
def executor():
    return ThreadPoolExecutor(max_workers=3)
