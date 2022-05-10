import asyncio
from datetime import datetime

import pytest
import os
import pandas as pd
from asyncua import Server, ua, Client, Node
from asyncua.ua import NodeId, DataValue
from pandas import DataFrame

from app.singleton import SingletonDict, DoubleKeyDict


def clear_servers_dict():
    servers = SingletonDict()
    servers.dictionary.clear()


def clear_nodes_dict():
    nodes_dict = DoubleKeyDict()
    nodes_dict.node_elements.clear()
    nodes_dict.measurements.clear()


async def write_tag_task(server: Server, myvar: Node):
    n = 0
    while True:
        await server.write_attribute_value(myvar.nodeid, DataValue(n))
        n += 1


@pytest.fixture
def add_one_server_into_config():
    os.environ["SERVERS"] = '{"MyServer1":"opc.tcp://192.168.0.8:54000"}'
    # передача управления тесту
    yield
    # очистка после теста
    os.unsetenv("SERVERS")
    clear_servers_dict()


@pytest.fixture
def add_few_servers_into_config():
    os.environ["SERVERS"] = '{"MyServer2":"opc.tcp://192.168.0.8:54000","MyServer3":"opc.tcp://192.168.0.1:54000"}'
    yield
    os.unsetenv("SERVERS")
    clear_servers_dict()


@pytest.fixture
def add_invalid_server_into_config():
    os.environ["SERVERS"] = '{"MyServer1":opc.tcp://192.168.0.8:54000}'
    yield
    os.unsetenv("SERVERS")
    clear_servers_dict()


@pytest.fixture
def clear_server_into_config():
    os.unsetenv("SERVERS")


@pytest.fixture
def generate_test_table_with_one_node():
    nodes = {"Item": pd.Series(["Тестовый тег 2"]),
             "Key": pd.Series(["TestTag2"]),
             "Node": pd.Series(["ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2"])}
    df = DataFrame(nodes)
    df.to_excel("../nodes.xlsx", index=False, sheet_name="MyServer1")
    yield
    clear_servers_dict()
    clear_nodes_dict()


@pytest.fixture
def generate_test_table_with_few_nodes():
    nodes = {"Item": pd.Series(["Тестовый тег 2", "Тестовый тег 3", "Тестовый тег 4"]),
             "Key": pd.Series(["TestTag2", "TestTag3", "TestTag4"]),
             "Node": pd.Series(["ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag3",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag4"])}
    df = DataFrame(nodes)
    df.to_excel("../nodes.xlsx", index=False, sheet_name="MyServer1")
    yield
    clear_servers_dict()
    clear_nodes_dict()


@pytest.fixture
def generate_test_table_with_few_servers():
    nodes = {"Item": pd.Series(["Тестовый тег 2", "Тестовый тег 3", "Тестовый тег 4"]),
             "Key": pd.Series(["TestTag2", "TestTag3", "TestTag4"]),
             "Node": pd.Series(["ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag3",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag4"])}
    with pd.ExcelWriter("../nodes.xlsx") as writer:
        df = DataFrame(nodes)
        df.to_excel(writer, sheet_name="MyServer1", index=False)
        df.to_excel(writer, sheet_name="MyServer2", index=False)
        df.to_excel(writer, sheet_name="MyServer3", index=False)
    yield
    clear_servers_dict()
    clear_nodes_dict()


@pytest.fixture
def add_loggers_variables():
    os.environ["LOG_LEVEL"] = 'DEBUG'
    os.environ["ASYNCUA_LOG_LEVEL"] = 'INFO'
    os.environ["UVICORN_LOG_LEVEL"] = 'WARNING'
    yield
    os.unsetenv("LOG_LEVEL")
    os.unsetenv("ASYNCUA_LOG_LEVEL")
    os.unsetenv("UVICORN_LOG_LEVEL")


@pytest.fixture
async def create_empty_server():
    server = Server()
    await server.init()
    server.disable_clock()
    server.set_endpoint(f'opc.tcp://127.0.0.1:54000')
    server.set_server_name("FreeOpcUa Example Server")
    server.set_security_policy([
        ua.SecurityPolicyType.NoSecurity,
        ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
        ua.SecurityPolicyType.Basic256Sha256_Sign])

    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    await server.start()
    yield server
    await server.stop()


@pytest.fixture
async def create_server_with_one_node():
    server = Server()
    await server.init()
    server.disable_clock()
    server.set_endpoint(f'opc.tcp://127.0.0.1:54000')
    server.set_server_name("FreeOpcUa Example Server")
    server.set_security_policy([
        ua.SecurityPolicyType.NoSecurity,
        ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
        ua.SecurityPolicyType.Basic256Sha256_Sign])

    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    myobj = await server.nodes.objects.add_object(idx, 'MyObject')
    myvar = await myobj.add_variable(idx, 'MyVariable', 10)
    async with server:
        yield server, myvar.nodeid


@pytest.fixture
async def get_server_client_and_one_node_id(create_server_with_one_node):
    temp_server: Server = create_server_with_one_node[0]
    node_id: NodeId = create_server_with_one_node[1]
    client = Client(temp_server.endpoint.geturl())
    async with client:
        yield temp_server, client, node_id.to_string()
    clear_nodes_dict()


# цикл while не дает выполниться yield но как тогда писать в переменную в фоне?
# без обновления переменной мы не получим уведомление для теста
# @pytest.fixture
# async def get_server_client_and_one_node_id_with_periodic_write(create_server_with_one_node):
#     temp_server: Server = create_server_with_one_node[0]
#     node_id: NodeId = create_server_with_one_node[1]
#     client = Client(temp_server.endpoint.geturl())
#     async with client:
#         myvar = client.get_node(node_id)
#         task = asyncio.create_task(write_tag_task(temp_server, myvar))
#         yield temp_server, client, node_id.to_string()
#         task.cancel()
#     clear_nodes_dict()
