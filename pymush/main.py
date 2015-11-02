import asyncio
import configparser
import os

import server as pym_server
import engine as pym_engine
import db as pym_db


def cfg_bool(config):
    return config in ["yes", "true", "1"]


def main():
    PYMUSH_BASE = os.environ["PYMUSH_BASE"]

    game_config = configparser.ConfigParser()
    game_config.read("%s/conf/pymush.conf" % PYMUSH_BASE)
    server_config = game_config["SERVER"]

    loop = asyncio.get_event_loop()

    if cfg_bool(server_config["UseInternalWebServer"]):
        import webserver as pym_webserver
        webserver = pym_webserver.SimpleStaticServer(server_config, "%s/static" % PYMUSH_BASE, loop)
        create_server_coroutine = loop.create_server(webserver.make_handler(), '', int(server_config["InternalWebServerPort"]))
        loop.run_until_complete(create_server_coroutine)

    main_db = pym_db.PyMushDB()
    main_engine = pym_engine.Engine(loop, main_db, game_config)

    factory = pym_server.PyMUSHServerFactory("ws://localhost:%s" % server_config["WebSocketPort"],
                                             main_engine,
                                             debug=cfg_bool(server_config["DebugAutobahn"]))

    factory.protocol = pym_server.PyMUSHServerProtocol

    create_server_coroutine = loop.create_server(factory, '', int(server_config["WebSocketPort"]))

    server = loop.run_until_complete(create_server_coroutine)

    try:
        loop.run_forever()
    except:
        server.close()
        loop.close()


if __name__ == "__main__":
    main()
