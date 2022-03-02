class SingletonBase(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonBase, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonDict(metaclass=SingletonBase):
    def __init__(self):
        self.dictionary = {}


class DoubleKeyDict(metaclass=SingletonBase):
    def __init__(self):
        self.node_elements = {}  # fast search node_element by node_id
        self.measurements = {}

    def update_value(self, node_id, new_value):
        if node_id in self.node_elements.keys():
            key = self.node_elements[node_id]
            self.measurements[key].last_value = new_value

    def add_key(self, key, node_id):
        self.node_elements[node_id] = key
        self.measurements[key] = None

    def get_by_key(self, key):
        if key in self.measurements.keys():
            return self.measurements[key]
        else:
            raise KeyError

    def get_by_node_id(self, node_id):
        if node_id in self.node_elements.keys():
            key = self.node_elements[node_id]
            if key in self.measurements.keys():
                return self.measurements[key]
            else:
                raise KeyError
        else:
            raise KeyError
