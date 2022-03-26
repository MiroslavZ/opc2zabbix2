import logging

from fastapi import FastAPI, HTTPException, status

from app.files_interactions import get_servers_from_config, get_nodes_from_xl
from app.server_interactions import connect_to_servers
from app.singleton import DoubleKeyDict, SingletonDict


app = FastAPI()
nodes_dict = DoubleKeyDict()
servers = SingletonDict()


@app.on_event("startup")
async def startup_event():
    get_nodes_from_xl()
    get_servers_from_config()
    await connect_to_servers()


_logger = logging.getLogger(__name__)


@app.get("/measurements/{key}")
async def get_last_measurement(key: str):
    if key in nodes_dict.measurements.keys():
        return nodes_dict.measurements[key]
    else:
        _logger.warning(f"Requesting measurements using an unknown key {key}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Measurement for node with key {key} not found")


@app.get("/servers/{name}")
async def get_server_status(name: str):
    if name in servers.dictionary.keys():
        return servers.dictionary[name].status
    else:
        _logger.warning(f"Server status query with unknown name {name}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server named {name} not found")