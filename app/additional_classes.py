class Node:
    def __init__(self, item: str, key: str, node_id: str):
        self.item = item
        self.key = key
        self.node_id = node_id

    def __str__(self):
        return f"Node with Item = {self.item}, Key = {self.key}, Node_id = {self.node_id}"


class Server():
    def __init__(self, name: str, address: str = None, nodes=None):
        if nodes is None:
            nodes = []
        self.name = name
        self.address = address
        self.nodes = nodes

    def __str__(self):
        return f"Server with name {self.name}, address {self.address} and {len(self.nodes)} nodes"