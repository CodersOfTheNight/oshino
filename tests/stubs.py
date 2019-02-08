from pytest import fixture


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
