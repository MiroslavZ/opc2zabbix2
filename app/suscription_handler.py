from asyncua import Node
from app.models import Measurement
from app.singleton import DoubleKeyDict
import logging


_logger = logging.getLogger(__name__)
nodes_dict = DoubleKeyDict()


class SubscriptionHandler:
    """
    Класс обработчика подписок
    """
    async def datachange_notification(self, node: Node, val, data):
        """
        Обработка уведомления об изменении показаний узла.
        Создание объекта измерения и обновление показаний узла в нем
        :param node: объект узла
        :param val: значение узла
        """
        node_id = node.nodeid.to_string()
        if node_id not in nodes_dict.node_elements.keys():
            _logger.warning(f"Received notification from unknown node ({node_id}) ")
        key = nodes_dict.node_elements[node_id].key
        if key in nodes_dict.measurements.keys() and nodes_dict.measurements[key].last_value is not None:
            nodes_dict.measurements[key].last_value = val
        else:
            display_name = (await node.read_display_name()).Text
            value_type = await node.read_data_type_as_variant_type()
            measurement = Measurement(node_id, display_name, value_type, val, False)
            nodes_dict.measurements[key] = measurement

    def event_notification(self, event):
        print("New event", event)
