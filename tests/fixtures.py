import asyncio

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
def executor(request):
    loop = asyncio.get_event_loop()
    print("Loop: {0}".format(loop))
    ex = ThreadPoolExecutor(max_workers=3)
    def on_stop():
        ex.shutdown(wait=True)
        loop.close()
        print("done closing")

    loop.set_default_executor(ex)
    request.addfinalizer(on_stop)
    return ex
