import logging
import os
import json
import pandas
from dotenv import load_dotenv
from app.additional_classes import Node, Server
from app.models import Measurement
from app.singleton import SingletonDict, DoubleKeyDict

load_dotenv()

servers = SingletonDict()
nodes_dict = DoubleKeyDict()


def setup_loggers():
    log_level = os.getenv("LOG_LEVEL")
    logging.basicConfig(level=log_level)
    asyncua_log_level = os.getenv("ASYNCUA_LOG_LEVEL")
    logging.getLogger("asyncua").setLevel(asyncua_log_level)
    uvicorn_log_level = os.getenv("UVICORN_LOG_LEVEL")
    uvicorn_loggers = [logging.getLogger("uvicorn.access"), logging.getLogger("uvicorn.error")]
    for ul in uvicorn_loggers:
        ul.setLevel(uvicorn_log_level)


setup_loggers()
_logger = logging.getLogger(__name__)


def get_nodes_from_xl():
    """
    Чтение списков узлов из excel файла и сохранение в словарь.
    Имена листов документа соответствуют именам серверов
    из конфиг файла.
    """
    file = pandas.ExcelFile("nodes.xlsx")
    sheets = file.sheet_names
    _logger.info("Reading the list of nodes from the excel document")
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
            nodes_dict.measurements[key] = Measurement(node_id)
        servers.dictionary[server.name] = server
        _logger.info(f"Loaded server {server.name} with {len(server.nodes)} nodes")


def get_servers_from_config():
    """
    Получение адресов серверов из конфиг файла.
    Сопоставление адреса по имени сервера из excel документа.
    """
    servers_json = os.getenv("SERVERS")
    servers_dict = json.loads(servers_json)
    _logger.info("Reading servers from config file")
    undeclared = 0
    for name in servers_dict.keys():
        if name in servers.dictionary.keys():
            servers.dictionary[name].address = servers_dict[name]
            _logger.info(f"Loaded server {name} with address {servers_dict[name]}")
        else:
            undeclared += 1
            servers.dictionary[name] = Server(name=name, address=servers_dict[name])
            _logger.warning(f"Server {name} with address {servers_dict[name]} not declared in excel document!")
    _logger.info(f"Loaded {len(servers_dict.keys())-undeclared} servers from config")