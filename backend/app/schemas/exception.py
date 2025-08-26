from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.exception import ExceptionSeverity

class ExceptionResolutionRequest(BaseModel):
    resolution_notes: str

class DataExceptionResponse(BaseModel):
    id: int
    job_id: Optional[int]
    exception_type: str
    message: str
    severity: ExceptionSeverity
    metadata: Optional[Dict[str, Any]]
    resolved: bool
    resolved_by: Optional[int]
    resolution_notes: Optional[str]
    timestamp: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
