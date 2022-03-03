import logging
from asyncua import Node, Client
from asyncua.ua import NodeId
from dotenv import load_dotenv
import os
import json
import pandas
from app.node_element import NodeElement
from app.singleton import DoubleKeyDict
from app.suscription_handler import SubscriptionHandler

load_dotenv()
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')
servers_addresses = []
nodes_from_xl = []
nodes_dict = DoubleKeyDict()


def get_nodes_from_xl():
    file = pandas.read_excel("./app/nodes.xlsx")
    for i in range(file.shape[0]):
        series = file.loc[i]
        item = series[0]
        key = series[1]
        node_id = series[2]
        node_element = NodeElement(item, key, node_id)
        nodes_from_xl.append(node_id)
        nodes_dict.node_elements[node_id] = node_element


def get_servers_from_config():
    servers_json = os.getenv("SERVERS")
    servers_addresses.extend(json.loads(servers_json))
    _logger.info(servers_addresses)


async def browse_nodes(node: Node, nodes_list=[]):
    nodes_list.append(node.nodeid.to_string())
    children = await node.get_children()
    if len(children) == 0:
        return
    for child in children:
        await browse_nodes(child, nodes_list)
    return nodes_list


async def connect_to_servers():
    for address in servers_addresses:
        client = Client(address)
        try:
            await client.connect()
            server_nodes = await browse_nodes(client.nodes.objects)
            _logger.info(server_nodes)
            required_nodes = list(filter(lambda n: n in nodes_from_xl, server_nodes))
            _logger.info(required_nodes)
            if len(required_nodes) < 1:
                _logger.info(f"Server with address {address} doesn't have necessary nodes")
                continue
            await subscribe_to_server_nodes(client, required_nodes)
        except TimeoutError:
            _logger.exception(f"Unable to connect to server with address {address}")
        finally:
            await client.disconnect()


async def subscribe_to_server_nodes(client: Client, nodes_ids_str):
    handler = SubscriptionHandler()
    nodes_ids = map(lambda ns: NodeId.from_string(ns), nodes_ids_str)
    nodes = map(lambda ni: client.get_node(ni), nodes_ids)
    subscription = await client.create_subscription(500, handler)
    await subscription.subscribe_data_change(nodes)

# if __name__ == '__main__':
#     get_nodes_from_xl()
#     get_servers_from_config()
#     asyncio.run(connect_to_servers())
