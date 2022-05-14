import asyncua
import pytest
from asyncua import Client

from app.additional_classes import Server, Node, ConnectionParams, ServerStatus
from app.server_interactions import connect_to_server, get_nodes_and_subscribe, check_server_state


@pytest.mark.asyncio
async def test_state_changed_after_success_connection_at_state_1(create_empty_server):
    temp_server: asyncua.Server = create_empty_server
    address = temp_server.endpoint.geturl()
    server = Server(name=temp_server.name, address=address)
    params = ConnectionParams(client=Client(address))
    server.connection_params = params
    result_state = await connect_to_server(server)
    await server.connection_params.client.disconnect()
    assert result_state == 2


@pytest.mark.asyncio
async def test_state_not_changed_after_failed_connection_at_state_1(create_empty_not_working_server):
    temp_server: asyncua.Server = create_empty_not_working_server
    server = Server(name=temp_server.name, address=temp_server.endpoint.geturl())
    params = ConnectionParams(client=Client(server.address))
    server.connection_params = params
    state = await connect_to_server(server)
    assert state == 1


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
async def test_server_status_not_changed_after_failed_connection_at_state_1(create_empty_not_working_server):
    temp_server: asyncua.Server = create_empty_not_working_server
    server = Server(name=temp_server.name, address=temp_server.endpoint.geturl())
    params = ConnectionParams(client=Client(server.address))
    server.connection_params = params
    await connect_to_server(server)
    assert server.status.connected is False


@pytest.mark.asyncio
async def test_state_changed_after_correct_subscription_at_state_2(get_server_client_and_one_node_id):
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


@pytest.mark.asyncio
async def test_state_changed_after_failed_subscription_at_state_2(get_server_client_and_one_node_id):
    temp_server: asyncua.Server = get_server_client_and_one_node_id[0]
    client = get_server_client_and_one_node_id[1]
    node_id = get_server_client_and_one_node_id[2]
    nodes_list = [Node("Item1", "Key1", node_id)]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server = Server(name=temp_server.name, address=address, nodes=nodes_list, connection_params=params)
    await temp_server.stop()
    state = await get_nodes_and_subscribe(server)
    assert state == 4


@pytest.mark.asyncio
async def test_state_changed_on_lost_connection_at_state_3(get_server_client):
    temp_server: asyncua.Server = get_server_client[0]
    client = get_server_client[1]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server_status = ServerStatus(connected=True, service_level=200)
    server = Server(name=temp_server.name, address=address, connection_params=params, status=server_status)
    await temp_server.stop()
    state = await check_server_state(server)
    assert state == 4


@pytest.mark.asyncio
async def test_server_status_changed_on_lost_connection_at_state_3(get_server_client):
    temp_server: asyncua.Server = get_server_client[0]
    client = get_server_client[1]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server_status = ServerStatus(connected=True, service_level=200)
    server = Server(name=temp_server.name, address=address, connection_params=params, status=server_status)
    await temp_server.stop()
    state = await check_server_state(server)
    assert server.status.connected is False



@pytest.mark.asyncio
async def test_state_not_changed_on_normal_server_at_state_3(get_server_client):
    temp_server: asyncua.Server = get_server_client[0]
    client = get_server_client[1]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server_status = ServerStatus(connected=True, service_level=200)
    server = Server(name=temp_server.name, address=address, connection_params=params, status=server_status)
    state = await check_server_state(server)
    assert state == 3


@pytest.mark.asyncio
async def test_saved_correct_service_level_on_normal_server_at_state_3(get_server_client):
    temp_server: asyncua.Server = get_server_client[0]
    client = get_server_client[1]
    params = ConnectionParams(client=client)
    address = temp_server.endpoint.geturl()
    server_status = ServerStatus(connected=True, service_level=200)
    server = Server(name=temp_server.name, address=address, connection_params=params, status=server_status)
    state = await check_server_state(server)
    assert server.status.service_level >= 200