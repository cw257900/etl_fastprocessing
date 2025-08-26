from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.processing_job import JobStatus

class TransformationRuleCreate(BaseModel):
    rule_type: str
    parameters: Dict[str, Any]
    description: Optional[str] = None

class ProcessingJobResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_id: Optional[int]
    status: JobStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    transformation_rules: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
