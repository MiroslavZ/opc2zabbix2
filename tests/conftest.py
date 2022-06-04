import asyncua
import pytest
import os
import pandas as pd
from asyncua import ua, Client
from pandas import DataFrame

from app import additional_classes
from app.singleton import SingletonDict, DoubleKeyDict
from app.subscription_handler import SubscriptionHandler


def clear_servers_dict():
    servers = SingletonDict()
    servers.dictionary.clear()


def clear_nodes_dict():
    nodes_dict = DoubleKeyDict()
    nodes_dict.node_elements.clear()
    nodes_dict.measurements.clear()


@pytest.fixture
def add_one_server_into_config():
    os.environ["SERVERS"] = '{"MyServer1":"opc.tcp://192.168.0.8:54000"}'
    yield
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
    clear_servers_dict()
    clear_nodes_dict()
    nodes = {"Item": pd.Series(["Тестовый тег 2"]),
             "Key": pd.Series(["TestTag2"]),
             "Node": pd.Series(["ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2"])}
    df = DataFrame(nodes)
    df.to_excel("../nodes.xlsx", index=False, sheet_name="MyServer1")


@pytest.fixture
def generate_test_table_with_few_nodes():
    nodes = {"Item": pd.Series(["Тестовый тег 2", "Тестовый тег 3", "Тестовый тег 4"]),
             "Key": pd.Series(["TestTag2", "TestTag3", "TestTag4"]),
             "Node": pd.Series(["ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag3",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag4"])}
    writer = pd.ExcelWriter('../nodes.xlsx', engine='xlsxwriter')
    df = DataFrame(nodes)
    df.to_excel(writer, sheet_name="MyServer1", index=False)
    clear_servers_dict()
    clear_nodes_dict()


@pytest.fixture
def generate_test_table_with_few_servers():
    nodes = {"Item": pd.Series(["Тестовый тег 2", "Тестовый тег 3", "Тестовый тег 4"]),
             "Key": pd.Series(["TestTag2", "TestTag3", "TestTag4"]),
             "Node": pd.Series(["ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag3",
                                "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag4"])}
    writer = pd.ExcelWriter('../nodes.xlsx', engine='xlsxwriter')
    df = DataFrame(nodes)
    df.to_excel(writer, sheet_name="MyServer1", index=False)
    df.to_excel(writer, sheet_name="MyServer2", index=False)
    df.to_excel(writer, sheet_name="MyServer3", index=False)
    writer.save()
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
async def create_server_with_few_nodes():
    server = asyncua.Server()
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
    myvar_1 = await myobj.add_variable(idx, 'MyVariable1', 10)
    myvar_2 = await myobj.add_variable(idx, 'MyVariable2', 20)
    myvar_3 = await myobj.add_variable(idx, 'MyVariable3', 30)
    async with server:
        yield server, [myvar_1.nodeid, myvar_2.nodeid, myvar_3.nodeid]


@pytest.fixture
async def create_server(create_server_with_few_nodes):
    temp_server: asyncua.Server = create_server_with_few_nodes[0]
    address = temp_server.endpoint.geturl()
    server = additional_classes.Server(name=temp_server.name, address=address)
    params = additional_classes.ConnectionParams(client=Client(address))
    server.connection_params = params
    yield server
    await server.connection_params.client.disconnect()


@pytest.fixture
async def create_not_working_server(create_server_with_few_nodes):
    temp_server: asyncua.Server = create_server_with_few_nodes[0]
    address = temp_server.endpoint.geturl()
    server = additional_classes.Server(name=temp_server.name, address=address)
    params = additional_classes.ConnectionParams(client=Client(address))
    server.connection_params = params
    await temp_server.stop()
    yield server


@pytest.fixture
async def create_server_with_connected_client(create_server_with_few_nodes):
    temp_server: asyncua.Server = create_server_with_few_nodes[0]
    nodes_ids = create_server_with_few_nodes[1]
    address = temp_server.endpoint.geturl()
    server = additional_classes.Server(name=temp_server.name, address=address)
    client = Client(address)
    params = additional_classes.ConnectionParams(client=client)
    server.connection_params = params
    server.nodes = [
        additional_classes.Node("MyVar1", "MyVar1", nodes_ids[0].to_string()),
        additional_classes.Node("MyVar2", "MyVar2", nodes_ids[1].to_string()),
        additional_classes.Node("MyVar3", "MyVar3", nodes_ids[2].to_string()),
    ]
    async with client:
        yield server, temp_server


@pytest.fixture
async def create_server_with_subscribed_client(create_server_with_few_nodes):
    temp_server: asyncua.Server = create_server_with_few_nodes[0]
    nodes_ids = create_server_with_few_nodes[1]
    address = temp_server.endpoint.geturl()
    server = additional_classes.Server(name=temp_server.name, address=address)
    client = Client(address)
    params = additional_classes.ConnectionParams(client=client)
    server.connection_params = params
    server.nodes = [
        additional_classes.Node("MyVar1", "MyVar1", nodes_ids[0].to_string()),
        additional_classes.Node("MyVar2", "MyVar2", nodes_ids[1].to_string()),
        additional_classes.Node("MyVar3", "MyVar3", nodes_ids[2].to_string()),
    ]
    async with client:
        handler = SubscriptionHandler()
        subscription = await client.create_subscription(500, handler)
        nodes = list(map(lambda n: client.get_node(n), nodes_ids))
        handles = await subscription.subscribe_data_change(nodes)
        server.connection_params.subscription = subscription
        server.connection_params.handles = handles
        yield server, temp_server


@pytest.fixture
async def create_server_dictionary(create_server_with_few_nodes):
    clear_servers_dict()
    temp_server: asyncua.Server = create_server_with_few_nodes[0]
    nodes_ids = create_server_with_few_nodes[1]
    address = temp_server.endpoint.geturl()
    server = additional_classes.Server(name=temp_server.name, address=address)
    server.nodes = [
        additional_classes.Node("MyVar1", "MyVar1", nodes_ids[0].to_string()),
        additional_classes.Node("MyVar2", "MyVar2", nodes_ids[1].to_string()),
        additional_classes.Node("MyVar3", "MyVar3", nodes_ids[2].to_string()),
    ]
    servers = SingletonDict()
    servers.dictionary[server.name] = server
    yield
    clear_servers_dict()
