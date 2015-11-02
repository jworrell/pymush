import traceback

import autobahn.asyncio.websocket as websocket

import command as pym_command
import db as pym_db


class PyMUSHServerFactory(websocket.WebSocketServerFactory):
    def __init__(self, address, engine, *args, **kwargs):
        super().__init__(address, *args, **kwargs)

        self.engine = engine


class PyMUSHServerProtocol(websocket.WebSocketServerProtocol):
    def onConnect(self, request):
        try:
            self.engine = self.factory.engine
            self.player_object = self.engine.db.create_object(pym_db.Player)
            self.player_object.set_attribute("name", "Wizard")
            self.player_object.connect(self)

        except:
            traceback.print_exc()

    def onOpen(self):
        self.sendMessage("Welcome!".encode("utf-8"))

    def onClose(self, was_clean, code, reason):
        self.player_object.disconnect()

    def onMessage(self, message, is_binary):
        decoded_message = message.decode("utf-8").strip()
        cmd = pym_command.Command.build(self.player_object, decoded_message)
        self.engine.enqueue_command(cmd)

    def send_string(self, message):
        self.sendMessage(message.encode("utf-8"))
