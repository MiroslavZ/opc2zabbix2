import asyncua
import pytest

from app.additional_classes import Server
from app.server_interactions import connect_to_server, get_nodes_and_subscribe, check_server_state, \
    disconnect_from_server, check_service_level, get_required_nodes, subscribe_to_server_nodes


@pytest.mark.asyncio
async def test_state_changed_after_successful_connection_at_state_1(create_server):
    server: Server = create_server
    result_state = await connect_to_server(server)
    assert result_state == 2


@pytest.mark.asyncio
async def test_server_status_changed_after_successful_connection_at_state_1(create_server):
    server = create_server
    await connect_to_server(server)
    assert server.status.connected


@pytest.mark.asyncio
async def test_state_not_changed_after_failed_connection_at_state_1(create_not_working_server):
    server = create_not_working_server
    state = await connect_to_server(server)
    assert state == 1


@pytest.mark.asyncio
async def test_server_status_not_changed_after_failed_connection_at_state_1(create_not_working_server):
    server = create_not_working_server
    await connect_to_server(server)
    assert server.status.connected is False


@pytest.mark.asyncio
async def test_get_required_nodes(create_server_with_connected_client):
    server = create_server_with_connected_client[0]
    nodes_ids_str = map(lambda n: n.node_id, server.nodes)
    nodes = list(await get_required_nodes(server.connection_params.client, nodes_ids_str))
    assert len(nodes) == 3 \
           and nodes[0].nodeid.to_string() == 'ns=2;i=2' \
           and nodes[1].nodeid.to_string() == 'ns=2;i=3' \
           and nodes[2].nodeid.to_string() == 'ns=2;i=4'


@pytest.mark.asyncio
async def test_subscribe_to_server_nodes(create_server_with_connected_client):
    server = create_server_with_connected_client[0]
    nodes_ids_str = map(lambda n: n.node_id, server.nodes)
    nodes = list(await get_required_nodes(server.connection_params.client, nodes_ids_str))
    subscription, handles = await subscribe_to_server_nodes(server.connection_params.client, nodes)
    assert subscription and handles


@pytest.mark.asyncio
async def test_state_changed_after_successful_subscription_at_state_2(create_server_with_connected_client):
    server = create_server_with_connected_client[0]
    state = await get_nodes_and_subscribe(server)
    assert state == 3


@pytest.mark.asyncio
async def test_saving_params_after_successful_subscription_at_state_2(create_server_with_connected_client):
    server = create_server_with_connected_client[0]
    await get_nodes_and_subscribe(server)
    assert server.connection_params.subscription is not None and server.connection_params.handles is not None


@pytest.mark.asyncio
async def test_state_changed_after_failed_subscription_at_state_2(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    temp_server: asyncua.Server = create_server_with_connected_client[1]
    await temp_server.stop()
    state = await get_nodes_and_subscribe(server)
    assert state == 4


@pytest.mark.asyncio
async def test_check_service_level_ok(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    can_check_service_level, service_level_is_normal = \
        await check_service_level(server.connection_params.client, server)
    assert can_check_service_level and service_level_is_normal


# писать в сервер некорректный service_level нельзя, будет исключение

@pytest.mark.asyncio
async def test_check_service_level_lost_connection(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    temp_server: asyncua.Server = create_server_with_connected_client[1]
    await temp_server.stop()
    can_check_service_level, service_level_is_normal = \
        await check_service_level(server.connection_params.client, server)
    assert not can_check_service_level and not service_level_is_normal


@pytest.mark.asyncio
async def test_state_not_changed_after_successful_check_at_state_3(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    state = await check_server_state(server)
    assert state == 3


@pytest.mark.asyncio
async def test_state_changed_after_lost_connection_at_state_3(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    temp_server: asyncua.Server = create_server_with_connected_client[1]
    await temp_server.stop()
    state = await check_server_state(server)
    assert state == 4


@pytest.mark.asyncio
async def test_state_changed_after_successful_disconnect_at_state_4(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    temp_server: asyncua.Server = create_server_with_connected_client[1]
    await temp_server.stop()
    state = await disconnect_from_server(server)
    assert state == 1


@pytest.mark.asyncio
async def test_server_status_changed_after_successful_disconnect_at_state_4(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    temp_server: asyncua.Server = create_server_with_connected_client[1]
    await disconnect_from_server(server)
    assert server.status.connected is False


@pytest.mark.asyncio
async def test_sub_and_handles_cleared_after_failed_disconnect_at_state_4(create_server_with_connected_client):
    server: Server = create_server_with_connected_client[0]
    temp_server: asyncua.Server = create_server_with_connected_client[1]
    await temp_server.stop()
    await disconnect_from_server(server)
    assert len(server.connection_params.handles) == 0 and server.connection_params.subscription is None
