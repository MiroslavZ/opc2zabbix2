from asyncua import Node

from models import Measurement
from schemas import NodeToReturn
from singleton import SingletonDict, DoubleKeyDict
import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')
# nodes_dict = SingletonDict()
nodes_dict = DoubleKeyDict()


class SubscriptionHandler:
    async def datachange_notification(self, node: Node, val, data):
        # _logger.info('datachange_notification %r %s', node.nodeid.to_string(), val)
        # if node.nodeid.to_string() not in nodes_dict.dictionary.keys():
        #     data_type = str(await node.read_data_type_as_variant_type())
        #     node_to_return = NodeToReturn(node_id=node.nodeid.to_string(), value_type=data_type, last_value=val)
        #     nodes_dict.dictionary[node.nodeid.to_string()] = node_to_return
        # print(data)
        # nodes_dict.dictionary[node.nodeid.to_string()].last_value = val

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
