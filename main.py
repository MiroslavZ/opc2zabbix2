from fastapi import FastAPI
from singleton import DoubleKeyDict
from server_interactions import get_nodes_from_xl, get_servers_from_config, connect_to_servers

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
        return f"Node with id {key} not found"
