from asyncio.tasks import Task
from asyncua import Client
from asyncua.common.subscription import Subscription


class Node:
    """
    Класс для хранения информации об узле из excel документа
    Не путать с Node из asyncua!
    """
    def __init__(self, item: str, key: str, node_id: str):
        """
        :param item: Имя узла
        :param key: Ключ для получения показаний через api
        :param node_id: Адрес узла в OPC-сервере
        """
        self.item = item
        self.key = key
        self.node_id = node_id

    def __str__(self):
        return f"Node with Item = {self.item}, Key = {self.key}, Node_id = {self.node_id}"


class ServerStatus():
    """
    Класс для представления информации о состоянии сервера.
    """
    def __init__(self, connected: bool = False, service_level: int = 0):
        """
        :param connected: Подключение к серверу
        :param service_level: Значение service level узла сервера (при наличии)
        """
        self.connected = connected
        self.service_level = service_level


class ConnectionParams():
    """
    Дополнительные параметры для работы с подключением к серверу
    """
    def __init__(self, client: Client = None, subscription: Subscription = None, handles=None, connection_task: Task = None):
        """
        :param client: Экземпляр OPC-клиента
        :param subscription: Экземпляр объекта подписки
        :param handles: Список элементов для отмены подписки
        :param connection_task: Задача на подключение к серверу
        """
        if handles is None:
            handles = []
        self.client = client
        self.subscription = subscription
        self.handles = handles
        self.connection_task = connection_task


class Server():
    """
    Класс для представления OPC-сервера
    """
    def __init__(self, name: str, address: str = None, nodes=None, status: ServerStatus = ServerStatus(),
                 connection_params: ConnectionParams = None):
        """
        :param name: Имя сервера (Имя листа сервера из excel документа)
        :param address: Адрес сервера из конфиг файла
        :param nodes: Список узлов из excel документа
        :param status: Класс для представления информации о состоянии сервера
        :param connection_params: Дополнительные параметры для работы с подключением к серверу
        """
        if nodes is None:
            nodes = []
        self.name = name
        self.address = address
        self.nodes = nodes
        self.status = status
        self.connection_params = connection_params

    def __str__(self):
        return f"Server with name {self.name}, address {self.address} and {len(self.nodes)} nodes"