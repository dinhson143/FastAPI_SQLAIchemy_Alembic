from pydantic import BaseModel


class TaskRequest(BaseModel):
    task_name: str
    priority: int
