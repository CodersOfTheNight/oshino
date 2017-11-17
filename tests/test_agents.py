from pytest import fixture, mark
from oshino.agents.http_agent import HttpAgent, Success, Failure
from oshino.agents.subprocess_agent import SubprocessAgent, StdoutAgent
from oshino import Agent


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
def stdout_agent():
    fake_metrics = """
    test1 = 1
    test2 = 2
    test3 = 3
    """
    cfg = {"name": "test-stdout-agent",
           "cmd": "echo '{0}'".format(fake_metrics)}
    return StdoutAgent(cfg)


@fixture
def generic_agent():
    cfg = {"name": "Generic Agent"}
    return Agent(cfg)


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

    def test_is_valid(self, generic_agent):
        assert generic_agent.is_valid()

    def test_name(self, generic_agent):
        assert generic_agent._data["name"] == "Generic Agent"
        assert generic_agent.name == "generic-agent"

    def test_prefix(self, generic_agent):
        assert generic_agent.prefix == "generic-agent."

    def test_logger(self, generic_agent):
        logger = generic_agent.get_logger()
        assert logger.name == "Agent"

    def test_start_stop(self, generic_agent):
        # Just touching at the moment
        generic_agent.on_start()
        generic_agent.on_stop()

    @mark.asyncio
    async def test_process_reachable(self, generic_agent):
        # Just touching at the moment

        def stub_event_fn(*args, **kwargs):
            pass

        await generic_agent.process(stub_event_fn)


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


class TestStdoutAgent(object):
    @mark.asyncio
    async def test_parse_content(self, stdout_agent):
        metrics_output = []

        def stub_event_fn(*args, **kwargs):
            nonlocal metrics_output
            metrics_output.append(kwargs)

        await stdout_agent.process(stub_event_fn)

        assert len(metrics_output) == 3
        assert sum(map(lambda x: x["metric_f"], metrics_output)) == 6
