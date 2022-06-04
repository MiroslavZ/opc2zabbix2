from app.additional_classes import Node
from app.files_interactions import get_nodes_from_xl
from app.singleton import DoubleKeyDict, SingletonDict


def test_correct_nodes_count(generate_test_table_with_few_nodes):
    get_nodes_from_xl()
    nodes_dict = DoubleKeyDict()
    nodes_count = len(nodes_dict.node_elements.keys())
    assert nodes_count == 3


def test_get_correct_servers_count(generate_test_table_with_few_servers):
    get_nodes_from_xl()
    servers = SingletonDict()
    servers_count = len(servers.dictionary.keys())
    assert servers_count == 3


def test_get_correct_server_name(generate_test_table_with_one_node):
    get_nodes_from_xl()
    servers = SingletonDict()
    assert "MyServer1" in servers.dictionary.keys()


def test_get_correct_node_data(generate_test_table_with_one_node):
    get_nodes_from_xl()
    nodes_dict = DoubleKeyDict()
    node2: Node = nodes_dict.node_elements["ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2"]
    assert node2.node_id == "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag2" and \
           node2.key == "TestTag2" and node2.item == "Тестовый тег 2"
