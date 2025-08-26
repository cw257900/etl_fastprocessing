from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.workflow import WorkflowState, ApprovalType

class ApprovalRequest(BaseModel):
    approval_type: ApprovalType
    comments: Optional[str] = None

class WorkflowApprovalResponse(BaseModel):
    id: int
    job_id: int
    approval_type: ApprovalType
    state: WorkflowState
    submitted_by: int
    approved_by: Optional[int]
    comments: Optional[str]
    submitted_at: datetime
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True
