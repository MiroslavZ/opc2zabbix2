from asyncio.tasks import Task
from asyncua import Client
from asyncua.common.subscription import Subscription


class Node:
    def __init__(self, item: str, key: str, node_id: str):
        self.item = item
        self.key = key
        self.node_id = node_id

    def __str__(self):
        return f"Node with Item = {self.item}, Key = {self.key}, Node_id = {self.node_id}"


class ServerStatus():
    def __init__(self, connected: bool = False, service_level: int = 0):
        self.connected = connected
        self.service_level = service_level


class ConnectionParams():
    def __init__(self, client: Client = None, subscription: Subscription = None, handles=None, connection_task: Task = None):
        if handles is None:
            handles = []
        self.client = client
        self.subscription = subscription
        self.handles = handles
        self.connection_task = connection_task


class Server():
    def __init__(self, name: str, address: str = None, nodes=None, status: ServerStatus = ServerStatus(), connection_params: ConnectionParams = None):
        if nodes is None:
            nodes = []
        self.name = name
        self.address = address
        self.nodes = nodes
        self.status = status
        self.connection_params = connection_params

    def __str__(self):
        return f"Server with name {self.name}, address {self.address} and {len(self.nodes)} nodes"