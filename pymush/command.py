import traceback

import db as pym_db

COMMANDS = {}
ONE_SYMBOL_COMMANDS = {"\"", "'"}


def mush_command(Cmd):
    for verb in Cmd.verbs:
        print("Registered %s for %s" % (verb, Cmd))
        COMMANDS[verb] = Cmd

    return Cmd


class Command(object):
    @staticmethod
    def build(enactor, message):
        # Handle special commands with no space before their arguments
        if message[0] in ONE_SYMBOL_COMMANDS:
            verb = message[0]
            args = message[1:]

        else:
            split_message = message.split(" ", 1)

            verb = split_message[0].strip()
            args = "" if len(split_message) == 1 else split_message[1]

        verb = verb.lower()

        if verb in COMMANDS:
            command = COMMANDS[verb](enactor, args)
        else:
            command = Error(enactor, args)

        return command

    def __init__(self, enactor, args=""):
        self.args = args

        self.set_engine(None)
        self.set_enactor(enactor)

    def set_engine(self, engine):
        self.engine = engine

    def set_enactor(self, enactor):
        self.enactor = enactor

    def do(self):
        try:
            self._do()
        except:
            traceback.print_exc()


@mush_command
class Say(Command):
    verbs = ["say", "\"", "'"]

    def _do(self):
        enactor = self.enactor
        container = enactor.container

        name = enactor.get_attribute("name")
        message = '%s says, "%s"' % (name, self.args)
        container.hear(message)


@mush_command
class Look(Command):
    verbs = ["look", "l"]

    def _do(self):
        enactor = self.enactor
        container = enactor.container

        room_description = container.get_attribute("name")
        room_description += "/%s" % container.get_attribute("desc")

        for item in container.contents:
            room_description += "/%s" % item.get_attribute("name")

        enactor.hear(room_description)


@mush_command
class Dig(Command):
    verbs = ["dig"]

    def _do(self):
        enactor = self.enactor
        old_room = enactor.container
        db = enactor.db

        new_room = db.create_object(pym_db.Room)
        new_room.set_attribute("desc", "A brand new room!")
        new_room.set_attribute("name", self.args)

        old_room_exit = db.create_object(pym_db.Exit, old_room)
        old_room_exit.set_destination(new_room)
        old_room_exit.set_attribute("name", self.args)
        old_room_exit.set_attribute("desc", "Door to %s" % self.args)

        new_room_exit = db.create_object(pym_db.Exit, new_room)
        new_room_exit.set_destination(old_room)
        new_room_exit.set_attribute("name", old_room.get_attribute("name"))
        new_room_exit.set_attribute("desc", "Door to %s" % old_room.get_attribute("name"))

        enactor.hear("Success!")


@mush_command
class Move(Command):
    verbs = ["move", "m"]

    def _do(self):
        enactor = self.enactor
        container = enactor.container

        for exit in filter(lambda i: isinstance(i, pym_db.Exit), container.contents):
            lc_name = exit.get_attribute("name").lower()
            if lc_name.startswith(self.args):
                container.hear("%s goes through %s" %
                               (enactor.get_attribute("name"), exit.get_attribute("name")))

                enactor.move(exit.destination)

                exit.destination.hear("%s arrives from %s" %
                                      (enactor.get_attribute("name"), container.get_attribute("name")))

                self.engine.enqueue_command(Look(self.enactor))

                break
        else:
            enactor.hear("I don't see that here!")


@mush_command
class Error(Command):
    verbs = []

    def _do(self):
        enactor = self.enactor
        enactor.hear("Error! Inavlid command!")
