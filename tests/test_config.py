from json import JSONDecodeError

import pytest

from app.additional_classes import Server
from app.files_interactions import get_servers_from_config
from app.singleton import SingletonDict


def test_get_correct_servers_count(add_few_servers_into_config):
    get_servers_from_config()
    servers_count = len(SingletonDict().dictionary.keys())
    assert servers_count == 2


def test_get_one_correct_server(add_one_server_into_config):
    get_servers_from_config()
    result: Server = SingletonDict().dictionary["MyServer1"]
    assert result.name == "MyServer1" and result.address == "opc.tcp://192.168.0.8:54000"


def test_get_few_correct_servers(add_few_servers_into_config):
    get_servers_from_config()
    server2: Server = SingletonDict().dictionary["MyServer2"]
    server3: Server = SingletonDict().dictionary["MyServer3"]
    assert server2.name == "MyServer2" and \
           server2.address == "opc.tcp://192.168.0.8:54000" and \
           server3.name == "MyServer3" and \
           server3.address == "opc.tcp://192.168.0.1:54000"


def test_invalid_json(add_invalid_server_into_config):
    with pytest.raises(JSONDecodeError):
        get_servers_from_config()
