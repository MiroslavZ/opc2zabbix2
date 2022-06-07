import pytest

from app import additional_classes
from app.server_interactions import connect_to_servers
from app.singleton import SingletonDict


@pytest.mark.asyncio
async def test_connect_to_servers_create_task(create_server_dictionary):
    await connect_to_servers()
    servers = SingletonDict()
    server: additional_classes.Server = servers.dictionary["FreeOpcUa Example Server"]
    assert server.connection_params and server.connection_params.connection_task
    if server.connection_params.connection_task:
        server.connection_params.connection_task.cancel()


@pytest.mark.asyncio
async def test_connect_to_servers_skipping_already_connected_servers_on_first_run(create_server_dictionary):
    servers = SingletonDict()
    server: additional_classes.Server = servers.dictionary["FreeOpcUa Example Server"]
    server.status.connected = True
    await connect_to_servers()
    assert server.connection_params is None

