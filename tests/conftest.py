import pytest
import os
import pandas as pd
from pandas import DataFrame

from app.singleton import SingletonDict, DoubleKeyDict


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


def clear_servers_dict():
    servers = SingletonDict()
    servers.dictionary.clear()


def clear_nodes_dict():
    nodes_dict = DoubleKeyDict()
    nodes_dict.node_elements.clear()
    nodes_dict.measurements.clear()


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


if __name__ == '__main__':
    generate_test_table_with_few_servers()
