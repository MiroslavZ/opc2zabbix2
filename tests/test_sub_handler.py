import asyncio

import pytest

from app import additional_classes, models
from app.singleton import DoubleKeyDict


@pytest.mark.asyncio
async def test_create_measurement(create_server_with_subscribed_client_for_sub_handler):
    server: additional_classes.Server = create_server_with_subscribed_client_for_sub_handler[0]
    nodes_dict = DoubleKeyDict()
    first_node: additional_classes.Node = server.nodes[0]
    await asyncio.sleep(1)
    measurement: models.Measurement = nodes_dict.measurements[first_node.key]
    assert measurement.display_name and measurement.value_type and measurement.last_value and measurement.health_is_good
