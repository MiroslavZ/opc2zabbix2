import logging

from fastapi import FastAPI, HTTPException, status

from app.files_interactions import get_servers_from_config, get_nodes_from_xl
from app.models import LoggerSettings
from app.server_interactions import connect_to_servers, stop_connect_cycles
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


@app.get("/control/{command}",
         description="Endpoint to control the gateway connection. "
                     "Supported commands: \"start\", \"stop\", \"restart\"")
async def control(command: str):
    if command == "stop":
        await stop_connect_cycles()
        return "connection task stopped, subscription deleted, client disconnected"
    elif command == "start":
        await connect_to_servers()
        return "connecting started"
    elif command == "restart":
        await stop_connect_cycles()
        await connect_to_servers()
        return "restarting"
    else:
        return "unknown command"


@app.post("/control/logs", description="Endpoint to control log level of gateway and libraries "
                                       "(asyncua, uvicorn.access, uvicorn.error etc.)")
async def change_log_level(logger_name: str, log_level: LoggerSettings):
    logger = logging.getLogger(name=logger_name)
    if logger:
        logger.setLevel(log_level.log_level.value)
        for h in logger.handlers:
            h.setLevel(log_level.log_level.value)
        return f"Log level for logger {logger_name} updated to {log_level.log_level.value}"
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Logger with name {logger_name} not found")
