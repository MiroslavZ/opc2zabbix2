class Measurement():
    def __init__(self, node_id, display_name=None, value_type=None, last_value=None, health_is_good: bool = True):
        self.node_id = node_id
        self.display_name = display_name
        self.value_type = value_type
        self.last_value = last_value
        self.health_is_good = health_is_good
