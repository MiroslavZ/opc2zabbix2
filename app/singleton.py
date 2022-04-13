from app.models import Measurement


class SingletonBase(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonBase, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonDict(metaclass=SingletonBase):
    """
    Singleton словарь для хранения информации о серверах
    """
    def __init__(self):
        self.dictionary = {}


class DoubleKeyDict(metaclass=SingletonBase):
    """
    Пара словарей для хранения измерений по каждому узлу и быстрого поиска
    """
    def __init__(self):
        """
        node_elements - получение узла по node id (для обработки входящих уведомлений)
        measurements - получение измерения узла по полю key из excel документа (для ответов api)
        """
        self.node_elements = {}
        self.measurements = {}

    def update_value(self, node_id: str, new_value):
        """
        Обновление показаний узла по входящему уведомлению (через node id)
        :param node_id: Строковое представление node id узла
        :param new_value: Новое значение узла
        """
        if node_id in self.node_elements.keys():
            key = self.node_elements[node_id]
            self.measurements[key].last_value = new_value
        else:
            raise KeyError

    def add_key(self, key: str, node_id: str):
        """Добавление key и node id узла в словари"""
        self.node_elements[node_id] = key
        self.measurements[key] = None

    def get_by_key(self, key: str) -> Measurement:
        """
        Получение измерения по ключу key
        :param key: ключ из excel документа
        :return: Экземпляр измерения для соответствующего узла
        """
        if key in self.measurements.keys():
            return self.measurements[key]
        else:
            raise KeyError

    def get_by_node_id(self, node_id: str) -> Measurement:
        """
        Получение измерения по node id узла
        :param node_id: адрес узла в OPC-сервере
        :return: Экземпляр измерения для соответствующего узла
        """
        if node_id in self.node_elements.keys():
            key = self.node_elements[node_id]
            if key in self.measurements.keys():
                return self.measurements[key]
            else:
                raise KeyError
        else:
            raise KeyError
