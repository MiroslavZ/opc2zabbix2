import asyncio
import logging
from asyncua import Client
from asyncua.ua import NodeId

from app.files_interactions import get_servers_from_config, get_nodes_from_xl
from app.singleton import SingletonDict
from app.suscription_handler import SubscriptionHandler

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('server_interactions')

servers = SingletonDict()


async def connect_to_servers():
    for server_key in servers.dictionary.keys():
        server = servers.dictionary[server_key]
        _logger.info(server)
        address = server.address
        client = Client(address)
        try:
            _logger.info(f"Connecting to server {server.name} with address {address}")
            await client.connect()
            nodes_list = map(lambda node: node.node_id, server.nodes)
            required_nodes = list(await get_required_nodes(client, nodes_list))
            if len(required_nodes) < 1:
                _logger.info(f"Server with address {address} doesn't have necessary nodes")
                continue
            await subscribe_to_server_nodes(client, required_nodes)
        except TimeoutError:
            _logger.exception(f"Unable to connect to server with address {address}")
            await client.disconnect()


async def get_required_nodes(client: Client, nodes_ids_str):
    nodes_ids = map(lambda ns: NodeId.from_string(ns), nodes_ids_str)
    return map(lambda node_id: client.get_node(node_id), nodes_ids)


async def subscribe_to_server_nodes(client: Client, nodes):
    handler = SubscriptionHandler()
    subscription = await client.create_subscription(500, handler)
    await subscription.subscribe_data_change(nodes)

# if __name__ == '__main__':
#     get_nodes_from_xl()
#     get_servers_from_config()
#     asyncio.run(connect_to_servers())
