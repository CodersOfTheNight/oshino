import asyncio
from pytest import fixture, mark
from oshino.agents.http_agent import HttpAgent, Success, Failure
from oshino.agents.subprocess_agent import SubprocessAgent
from oshino.agents.test_agent import StubAgent


@fixture
def http_agent():
    cfg = {"name": "test-http-agent",
           "url": "http://localhost:9998/health",
           "headers": [{"x-test-header": 42}],
           "cookies": [{"user": "mr.awesome"}]}
    return HttpAgent(cfg)


@fixture
def subprocess_agent():
    cfg = {"name": "test-subprocess-agent",
           "script": "echo 'Hello world!'"}
    return SubprocessAgent(cfg)


@fixture
def stub_agent():
    cfg = {"name": "stub-agent"}
    return StubAgent(cfg)


@fixture(scope="session", autouse=True)
def stub_server(request):
    from multiprocessing import Process
    from stubilous.server import run
    from stubilous.builder import Builder
    builder = Builder()
    builder.server(host="localhost", port=9998)
    builder.route("GET", "/health")("Ok", 200)
    config = builder.build()
    proc = Process(target=run, args=(config,))

    def on_close():
        proc.terminate()
        proc.join()

    request.addfinalizer(on_close)
    proc.start()
    return proc


class TestGenericAgent(object):

    def test_prefix(self, stub_agent):
        assert stub_agent.prefix == "stub-agent."


class TestHttpAgent(object):

    def test_agent_without_url(self):
        cfg = {}
        incorrect_agent = HttpAgent(cfg)
        assert not incorrect_agent.is_valid()

    def test_agent_with_url(self, http_agent):
        assert http_agent.is_valid()

    def test_agent_url(self, http_agent):
        assert http_agent.url == "http://localhost:9998/health"

    def test_custom_headers(self, http_agent):
        assert len(http_agent.headers) > 0
        assert http_agent.headers[0]["x-test-header"] == 42

    def test_custom_cookies(self, http_agent):
        assert len(http_agent.cookies) > 0
        assert http_agent.cookies[0]["user"] == "mr.awesome"

    def test_translate_status_correct_code(self, http_agent):
        result = http_agent.translate_status(999)
        assert result.code == 999

    def test_translate_status_400(self, http_agent):
        result = http_agent.translate_status(400)
        assert isinstance(result, Failure)

    def test_translate_status_302(self, http_agent):
        result = http_agent.translate_status(302)
        assert isinstance(result, Failure)

    def test_translate_status_200(self, http_agent):
        result = http_agent.translate_status(200)
        assert isinstance(result, Success)

    @mark.asyncio
    async def test_process_reachable(self, http_agent):
        reached = False

        def stub_event_fn(*args, **kwargs):
            nonlocal reached
            reached = True

        await http_agent.process(stub_event_fn)
        assert reached

    @mark.asyncio
    async def test_process_ok(self, http_agent):
        state = None

        def stub_event_fn(*args, **kwargs):
            nonlocal state
            state = kwargs["state"]

        await http_agent.process(stub_event_fn)
        assert state == "success"

    @mark.asyncio
    async def test_process_fail(self, http_agent):
        state = None

        def stub_event_fn(*args, **kwargs):
            nonlocal state
            state = kwargs["state"]

        http_agent._data["url"] = "http://localhost:9998/invalid_url"

        await http_agent.process(stub_event_fn)
        assert state == "failure"


class TestSubprocessAgent(object):

    def test_agent_without_script(self):
        cfg = {}
        incorrect_agent = SubprocessAgent(cfg)
        assert not incorrect_agent.is_valid()

    def test_agent_with_script(self, subprocess_agent):
        assert subprocess_agent.is_valid()

    @mark.asyncio
    async def test_process_ok(self, subprocess_agent):
        state = None

        def stub_event_fn(*args, **kwargs):
            nonlocal state
            state = kwargs["state"]

        await subprocess_agent.process(stub_event_fn)
        assert state == "ok"

    @mark.asyncio
    async def test_process_fail(self, subprocess_agent):
        state = None
        subprocess_agent._data["script"] = "some_random_command"

        def stub_event_fn(*args, **kwargs):
            nonlocal state
            state = kwargs["state"]

        await subprocess_agent.process(stub_event_fn)
        assert state == "failure"