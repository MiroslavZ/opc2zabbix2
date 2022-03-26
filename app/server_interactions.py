import asyncio
import logging
from asyncua import Client
from asyncua.ua import NodeId

from app.additional_classes import Server
from app.files_interactions import get_servers_from_config, get_nodes_from_xl
from app.singleton import SingletonDict
from app.suscription_handler import SubscriptionHandler


_logger = logging.getLogger(__name__)

servers = SingletonDict()


async def connect_to_servers():
    for server_key in servers.dictionary.keys():
        server = servers.dictionary[server_key]
        asyncio.create_task(run_connect_cycle(server))


async def run_connect_cycle(server: Server):
    address = server.address
    client = Client(address)
    subscription = None
    handles = None
    state = 1
    _logger.info(f"Started connect cycle for {server.name}")
    while 1:
        if state == 1:  # connect
            try:
                await client.connect()
                _logger.info(f"Client successfully connected to {server.name}")
                server.status.connection = True
                state = 2
            except:
                _logger.warning(f"Unable to connect to server {server.name}")
                state = 1
                await asyncio.sleep(2)
        elif state == 2:  # get nodes & subscribe
            try:
                nodes_list = map(lambda node: node.node_id, server.nodes)
                required_nodes = list(await get_required_nodes(client, nodes_list))
                _logger.info(f"{len(required_nodes)} nodes received from {server.name}")
                subscription, handles = await subscribe_to_server_nodes(client, required_nodes)
                _logger.info(f"Created subscription for {server.name}")
                state = 3
            except:
                _logger.warning(f"Error with subscription to {server.name}")
                state = 4
                await asyncio.sleep(0)
        elif state == 3:  # read cyclic the service level if it fails disconnect & unsubscribe => reconnect
            simple_check = await check_first_node(client, server)
            normal_service_level = await check_service_level(client, server)
            if not normal_service_level and not simple_check:
                state = 4
                _logger.warning(f"Error with checking status of server {server.name}")
            await asyncio.sleep(2)
        elif state == 4:  # unsubscribe, delete subscription then disconnect
            try:
                _logger.info(f"Unsubscribing from server {server.name}")
                if handles:
                    await subscription.unsubscribe(handles)
                await subscription.delete()
            except:
                _logger.exception(f"Error with unsubscribing from {server.name}")
                subscription = None
                handles = []
                await asyncio.sleep(0)
            try:
                _logger.info(f"Disconnecting from {server.name}")
                await client.disconnect()
                server.status.connection = False
            except:
                _logger.warning(f"Error with disconnecting from {server.name}")
            state = 0
        else:
            state = 1
            await asyncio.sleep(2)


async def get_required_nodes(client: Client, nodes_ids_str):
    nodes_ids = map(lambda ns: NodeId.from_string(ns), nodes_ids_str)
    return map(lambda node_id: client.get_node(node_id), nodes_ids)


async def subscribe_to_server_nodes(client: Client, nodes):
    handler = SubscriptionHandler()
    subscription = await client.create_subscription(500, handler)
    handles = await subscription.subscribe_data_change(nodes)
    return subscription, handles


async def check_service_level(client: Client, server: Server):
    # what's if we haven't service level node?
    try:
        service_level = await client.nodes.service_level.get_value()
        server.status.service_level = service_level
        if service_level >= 200:
            return True
        else:
            return False
    except:
        server.status.service_level = "unknown"
        _logger.warning(f"Failed to check server {server.name} status via service_level node")
        return False


async def check_first_node(client: Client, server: Server):
    try:
        node = client.get_node(server.nodes[0].node_id)  # unreliable check
        value = await node.get_value()
        return True
    except:
        return False



# if __name__ == '__main__':
#     get_nodes_from_xl()
#     get_servers_from_config()
#     asyncio.run(connect_to_servers())
