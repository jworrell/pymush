import asyncio


class Engine(object):
    def __init__(self, event_loop, db, config):
        self.running = True

        self.event_loop = event_loop
        self.db = db
        self.config = config

        self.work_queue = asyncio.Queue()

        self.command_runner = self.command_runner_coro()
        asyncio.async(self.command_runner, loop=event_loop)

    def enqueue_command(self, command):
        command.set_engine(self)
        self.work_queue.put_nowait(command)

    @asyncio.coroutine
    def command_runner_coro(self):
        while self.running:
            command = yield from self.work_queue.get()
            command._do()
