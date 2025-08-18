from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WorkflowBase(BaseModel):
    name: str
    definition: str

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowRead(WorkflowBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class WorkflowRunBase(BaseModel):
    status: str

class WorkflowRunCreate(WorkflowRunBase):
    # for now no extra params; could include overrides / input payload
    pass

class WorkflowRunRead(WorkflowRunBase):
    id: int
    workflow_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    logs: Optional[str]
    class Config:
        orm_mode = True
