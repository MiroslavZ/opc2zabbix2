from fastapi import FastAPI, HTTPException, status

from app.files_interactions import get_servers_from_config, get_nodes_from_xl
from app.server_interactions import connect_to_servers
from app.singleton import DoubleKeyDict


app = FastAPI()
nodes_dict = DoubleKeyDict()


@app.on_event("startup")
async def startup_event():
    get_nodes_from_xl()
    get_servers_from_config()
    await connect_to_servers()


@app.get("/measurements/{key}")
async def get_last_measurement(key: str):
    if key in nodes_dict.measurements.keys():
        return nodes_dict.measurements[key]
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Measurement for node with key {key} not found")
