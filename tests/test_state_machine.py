import asyncua
import pytest
from asyncua import Client

from app.additional_classes import Server, Node, ConnectionParams
from app.server_interactions import connect_to_server, get_nodes_and_subscribe


@pytest.mark.asyncio
async def test_success_connect_at_state_1(create_empty_server):
    temp_server: asyncua.Server = create_empty_server
    address = temp_server.endpoint.geturl()
    server = Server(name=temp_server.name, address=address)
    params = ConnectionParams(client=Client(address))
    server.connection_params = params
    result_state = await connect_to_server(server)
    await server.connection_params.client.disconnect()
    assert result_state == 2


@pytest.mark.asyncio
async def test_server_status_changed_after_connection_at_state_1(create_empty_server):
    temp_server: asyncua.Server = create_empty_server
    address = temp_server.endpoint.geturl()
    server = Server(name=temp_server.name, address=address)
    params = ConnectionParams(client=Client(address))
    server.connection_params = params
    result_state = await connect_to_server(server)
    assert server.status.connected
    await server.connection_params.client.disconnect()


@pytest.mark.asyncio
async def test_correct_subscribe_at_state_2(get_server_client_and_one_node_id):
    temp_server: asyncua.Server = get_server_client_and_one_node_id[0]
    client = get_server_client_and_one_node_id[1]
    node_id = get_server_client_and_one_node_id[2]
    nodes_list = [Node("Item1", "Key1", node_id)]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server = Server(name=temp_server.name, address=address, nodes=nodes_list, connection_params=params)
    state = await get_nodes_and_subscribe(server)
    assert state == 3


@pytest.mark.asyncio
async def test_correct_subscribe_at_state_2(get_server_client_and_one_node_id):
    temp_server: asyncua.Server = get_server_client_and_one_node_id[0]
    client = get_server_client_and_one_node_id[1]
    node_id = get_server_client_and_one_node_id[2]
    nodes_list = [Node("Item1", "Key1", node_id)]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server = Server(name=temp_server.name, address=address, nodes=nodes_list, connection_params=params)
    state = await get_nodes_and_subscribe(server)
    assert state == 3


@pytest.mark.asyncio
async def test_saving_subscription_and_handles_at_state_2(get_server_client_and_one_node_id):
    temp_server: asyncua.Server = get_server_client_and_one_node_id[0]
    client = get_server_client_and_one_node_id[1]
    node_id = get_server_client_and_one_node_id[2]
    nodes_list = [Node("Item1", "Key1", node_id)]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server = Server(name=temp_server.name, address=address, nodes=nodes_list, connection_params=params)
    state = await get_nodes_and_subscribe(server)
    assert server.connection_params.subscription is not None and server.connection_params.handles is not None


# тест виснет, фикстура сделана неправильно
# @pytest.mark.asyncio
# async def test_get_first_notification_at_state_2(get_server_client_and_one_node_id_with_periodic_write):
#     temp_server: asyncua.Server = get_server_client_and_one_node_id_with_periodic_write[0]
#     client = get_server_client_and_one_node_id_with_periodic_write[1]
#     node_id = get_server_client_and_one_node_id_with_periodic_write[2]
#     nodes_list = [Node("Item1", "Key1", node_id)]
#     params = ConnectionParams(client=client)
#     address = temp_server.endpoint.geturl()
#     server = Server(name=temp_server.name, address=address, nodes=nodes_list, connection_params=params)
#     state = await get_nodes_and_subscribe(server)
#     await asyncio.sleep(2)
#     measurements = DoubleKeyDict().measurements
#     assert len(measurements.keys())>0


