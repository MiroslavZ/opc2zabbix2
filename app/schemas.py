from pydantic import BaseModel


class NodeToReturn(BaseModel):
    node_id: str
    value_type: str
    last_value: str