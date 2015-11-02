class PyMushDB(object):
    def __init__(self):
        self._db = {}

        self.the_void = self.create_object(Room)
        self.the_void.set_attribute("name", "The Void")
        self.the_void.set_attribute("desc", "Endless nothingness.")

    def _get_free_id(self):
        used_ids = self._db.keys()

        if not used_ids:
            return 0
        else:
            return min(used_ids) + 1

    def create_object(self, ObjectType, container=None):
        if container is None and ObjectType.needs_container:
            container = self.the_void

        free_id = self._get_free_id()
        new_object = ObjectType(self, free_id, container)

        self._db[free_id] = new_object

        return new_object


class PyMushObject(object):
    needs_container = False

    def __init__(self, db, id, container):
        self.db = db
        self.id = id
        self.contents = set()
        self.container = None
        self.attributes = {}

        if container:
            self.move(container)

    def set_attribute(self, attribute, value):
        self.attributes[attribute] = value

    def get_attribute(self, attribute):
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            return "#MISSING#"

    def hear(self, message):
        pass

    def move(self, destination):
        if self.container:
            self.container.contents.remove(self)

        destination.contents.add(self)

        self.container = destination


class Room(PyMushObject):
    needs_container = False

    def hear(self, message):
        for item in self.contents:
            item.hear(message)


class Exit(PyMushObject):
    needs_container = True

    def __init__(self, db, id, container):
        super().__init__(db, id, container)
        self.destination = None

    def set_destination(self, destination):
        self.destination = destination

    def get_destination(self):
        return self.destination


class Player(PyMushObject):
    needs_container = True

    def __init__(self, db, id, container):
        super().__init__(db, id, container)
        self.connection = None

    def connect(self, connection):
        self.connection = connection

    def disconnect(self):
        self.connection = None

    def hear(self, message):
        if self.connection:
            self.connection.send_string(message)


class Thing(PyMushObject):
    needs_container = True
