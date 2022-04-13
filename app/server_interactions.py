import asyncio
import logging

from asyncua import Client
from asyncua.ua import NodeId

from app.additional_classes import Server, ConnectionParams
from app.singleton import SingletonDict, DoubleKeyDict
from app.suscription_handler import SubscriptionHandler


_logger = logging.getLogger(__name__)

servers = SingletonDict()
nodes_dict = DoubleKeyDict()


async def connect_to_servers():
    """
    Поключение к серверам. Планирование задачи на подключение для каждого сервера.
    Сохранение ссылки на задачу для последующей отмены.
    """
    for server_key in servers.dictionary.keys():
        server = servers.dictionary[server_key]
        if server.status.connected:
            _logger.warning(f"Trying to connect to already connected server {server.name}")
            continue
        task = asyncio.create_task(run_connect_cycle(server))
        params = ConnectionParams(connection_task=task)
        server.connection_params = params


async def run_connect_cycle(server: Server):
    """
    Бесконечный цикл, state-машина
    для переподключения и проверки состояния сервера
    state 1 - подключение
    state 2 - получение узлов и подписка
    state 3 - циклическая проверка сервера и узлов
    state 4 - отписка от узлов, удаление подписки, отсоединение клиента => state 1
    :param server: Экземпляр сервера из словаря сереров
    """
    address = server.address
    server.connection_params.client = Client(address)
    server.connection_params.subscription = None
    server.connection_params.handles = None
    state = 1
    required_nodes = []
    _logger.info(f"Started connect cycle for {server.name}")
    while 1:
        if state == 1:  # connect
            try:
                await server.connection_params.client.connect()
                _logger.info(f"Client successfully connected to {server.name}")
                server.status.connected = True
                state = 2
            except:
                _logger.warning(f"Unable to connect to server {server.name}")
                state = 1
                await asyncio.sleep(2)
        elif state == 2:  # get nodes & subscribe
            try:
                nodes_list = map(lambda node: node.node_id, server.nodes)
                required_nodes = list(await get_required_nodes(server.connection_params.client, nodes_list))
                _logger.info(f"{len(required_nodes)} nodes received from {server.name}")
                subscription, handles = await subscribe_to_server_nodes(server.connection_params.client, required_nodes)
                server.connection_params.subscription = subscription
                server.connection_params.handles = handles
                _logger.info(f"Created subscription for {server.name}")
                state = 3
            except:
                _logger.warning(f"Error with subscription to {server.name}")
                state = 4
                await asyncio.sleep(0)
        elif state == 3:  # read cyclic the service level if it fails disconnect & unsubscribe => reconnect
            service_level_is_normal = await check_service_level(server.connection_params.client, server)
            all_nodes_is_normal = await check_nodes_health(required_nodes)
            if not service_level_is_normal and not all_nodes_is_normal:
                state = 4
                _logger.warning(f"Error with checking status of server {server.name}")
            await asyncio.sleep(2)
        elif state == 4:  # unsubscribe, delete subscription then disconnect
            try:
                _logger.info(f"Unsubscribing from server {server.name}")
                if server.connection_params.handles:
                    await server.connection_params.subscription.unsubscribe(server.connection_params.handles)
                await server.connection_params.subscription.delete()
            except:
                _logger.exception(f"Error with unsubscribing from {server.name}")
                server.connection_params.subscription = None
                server.connection_params.handles = []
                await asyncio.sleep(0)
            try:
                _logger.info(f"Disconnecting from {server.name}")
                await server.connection_params.client.disconnect()
                server.status.connected = False
            except:
                _logger.warning(f"Error with disconnecting from {server.name}")
            state = 1
        else:
            state = 1
            await asyncio.sleep(2)


async def get_required_nodes(client: Client, nodes_ids_str):
    """
    Формирование списка узлов по списку их node id.
    client.get_node не провряет существование узла на сервере!
    :param client: Экземпляр OPC-клиента для получения узлов
    :param nodes_ids_str: Список строковых представлений node id узлов
    """
    nodes_ids = map(lambda ns: NodeId.from_string(ns), nodes_ids_str)
    return map(lambda node_id: client.get_node(node_id), nodes_ids)


async def subscribe_to_server_nodes(client: Client, nodes):
    """
    Подписка на узлы
    :param client: Экземпляр OPC-клиента для создания подписки
    :param nodes: Список узлов для подписки
    :return: Экземпляр подписки и список элементов для отмены подписки
    """
    handler = SubscriptionHandler()
    subscription = await client.create_subscription(500, handler)
    handles = await subscription.subscribe_data_change(nodes)
    return subscription, handles


async def check_service_level(client: Client, server: Server):
    """
    Проверка здоровья сервера через значение service level узла
    При отсутствии узла - unknown
    :param client: Экземпляр клиента
    :param server: Экземпляр сервера из словаря сереров
    :return: True - здоровье сервера в норме,
    False - с сервером проблемы / не удалось проверить service level
    """
    try:
        service_level = await client.nodes.service_level.get_value()
        server.status.service_level = service_level
        return service_level >= 200
    except:
        server.status.service_level = "unknown"
        _logger.warning(f"Failed to check server {server.name} status via service_level node")
        return False


async def check_nodes_health(nodes: list):
    """
    Проверка здоровья узлов сервера.
    При значении отличном от GOOD в asyncua вызывается исключение.
    :param nodes: список узлов для проверки
    :return: True - все узлы впорядке, False - есть проблемные узлы
    """
    all_nodes_is_normal = True
    for node in nodes:
        node_id = node.nodeid.to_string()
        key = nodes_dict.node_elements[node_id].key
        try:
            data_val = await node.read_data_value()
            status = data_val.StatusCode.is_good()
            if key in nodes_dict.measurements.keys():
                nodes_dict.measurements[key].health_is_good = status
        except:
            all_nodes_is_normal = False
            _logger.warning(f"Error with checking status of node {node.nodeid.to_string()}")
            if key in nodes_dict.measurements.keys():
                nodes_dict.measurements[key].health_is_good = False
    return all_nodes_is_normal


async def stop_connect_cycles():
    """
    Остановка шлюза.
    Отмена задчи на подключение, изменение статуса подключения,
    отписка от узлов, удаление подписки, отсоединение клиента
    """
    for server_key in servers.dictionary.keys():
        server = servers.dictionary[server_key]
        params = server.connection_params
        task = params.connection_task
        cancelled = task.cancelled()
        if not cancelled:
            task.cancel()
        if not server.status.connected:  # server already disconnected in connect cycle
            return
        try:
            await task
        except asyncio.CancelledError:
            _logger.info(f'Connection task for server {server.name} already cancelled')
            try:
                _logger.info(f"Unsubscribing from server {server.name}")
                if server.connection_params.handles:
                    await server.connection_params.subscription.unsubscribe(server.connection_params.handles)
                await server.connection_params.subscription.delete()
            except:
                _logger.warning(f"Error with unsubscribing from {server.name}")
                server.connection_params.subscription = None
                server.connection_params.handles = []
                await asyncio.sleep(0)
            try:
                _logger.info(f"Disconnecting from {server.name}")
                await server.connection_params.client.disconnect()
                server.status.connected = False
            except:
                _logger.warning(f"Error with disconnecting from {server.name}")
