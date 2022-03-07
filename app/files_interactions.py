import logging
import os
import json
import pandas
from dotenv import load_dotenv
from app.additional_classes import Node, Server
from app.singleton import SingletonDict, DoubleKeyDict

_logger = logging.getLogger('files_interactions')


load_dotenv()
servers = SingletonDict()
nodes_dict = DoubleKeyDict()


def get_nodes_from_xl():
    file = pandas.ExcelFile("nodes.xlsx")
    sheets = file.sheet_names
    for sheet_name in sheets:
        server = Server(sheet_name)
        df = file.parse(sheet_name)
        for i in range(df.shape[0]):
            series = df.loc[i]
            item = series[0]
            key = series[1]
            node_id = series[2]
            node = Node(item, key, node_id)
            server.nodes.append(node)
            nodes_dict.node_elements[node_id] = node
        servers.dictionary[server.name] = server
        _logger.info(f"Loaded server {server.name} with {len(server.nodes)} nodes")
    _logger.info(servers.dictionary.keys())


def get_servers_from_config():
    servers_json = os.getenv("SERVERS")
    servers_dict = json.loads(servers_json)
    _logger.info(servers.dictionary.keys())
    for name in servers_dict.keys():
        if name in servers.dictionary.keys():
            servers.dictionary[name].address = servers_dict[name]
            _logger.info(f"Loaded server {name} with address {servers_dict[name]}")
        else:
            _logger.warning(f"Server {name} with address {servers_dict[name]} not declared in excel document!")
    _logger.info(f"Loaded {len(servers_dict.keys())} servers from config")


# if __name__ == '__main__':
#     get_nodes_from_xl()
#     get_servers_from_config()