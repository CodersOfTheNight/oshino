import os

import jinja2

from logbook import Logger
from aiohttp import web
from aiohttp_jinja2 import template, setup as jinja_setup


@template("index.html")
def index(request):
    return {}


def run(host, port, qin, qout):
    logger = Logger("Admin")
    app = web.Application()
    logger.info("Starting admin panel on: {0}:{1}, PID: {2}"
                .format(host,
                        port,
                        os.getpid()))
    app.router.add_get("/", index)

    def stats(request):
        data = {}
        while not qin.empty():
            item = qin.get_nowait()
            data.update(item)
        return web.json_response(data)

    app.router.add_get("/stats", stats)

    jinja_setup(app, loader=jinja2.PackageLoader("oshino", "templates"))
    web.run_app(app, host=host, port=port)
