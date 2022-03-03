from asyncua import Node
from app.models import Measurement
from app.singleton import DoubleKeyDict
import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')
nodes_dict = DoubleKeyDict()


class SubscriptionHandler:
    async def datachange_notification(self, node: Node, val, data):

        node_id = node.nodeid.to_string()
        if node_id not in nodes_dict.node_elements:
            raise KeyError
        key = nodes_dict.node_elements[node_id].key
        if key in nodes_dict.measurements:
            nodes_dict.measurements[key].last_value = val
        else:
            display_name = (await node.read_display_name()).Text
            value_type = await node.read_data_type_as_variant_type()
            measurement = Measurement(node_id, display_name, value_type, val)
            nodes_dict.measurements[key] = measurement
