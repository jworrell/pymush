import asyncio
import os

import aiohttp.web as web


class SimpleStaticServer(object):
    def __init__(self, server_config, base_path, loop):
        self.server_config = server_config
        self.base_path = base_path
        self.valid_files = {}

        self.app = web.Application(loop=loop)
        self.app.router.add_route('GET', '/{path:.*}', self.handle)

        for dirpath, dirnames, filenames in os.walk(base_path):
            for filename in filenames:
                if filename.startswith("."):
                    continue

                full_path = os.path.join(dirpath, filename)

                with open(full_path, encoding='utf-8') as file_to_cache:
                    self.valid_files[full_path] = file_to_cache.read().encode('utf-8')
                    print("Cached:", full_path)

    def make_handler(self):
        return self.app.make_handler()

    @asyncio.coroutine
    def handle(self, request):
        path = request.match_info.get("path", "")

        if path == "":
            path = "index.html"

        full_path = os.path.join(self.base_path, path)

        if full_path not in self.valid_files:
            raise web.HTTPNotFound()

        if self.server_config["DebugMode"] in ["yes", "true", "1"]:
            with open(full_path, encoding='utf-8') as file_to_send:
                response_body = file_to_send.read().encode('utf-8')

        else:
            response_body = self.valid_files[full_path]

        return web.Response(body=response_body)
