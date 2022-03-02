class NodeElement:
    def __init__(self, item: str, key: str, node_id: str):
        self.item = item
        self.key = key
        self.node_id = node_id

    def __str__(self):
        return f"Node with Item = {self.item}, Key = {self.key}, Node_id = {self.node_id}"
