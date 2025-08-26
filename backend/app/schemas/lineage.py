from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DataLineageResponse(BaseModel):
    id: int
    source_id: Optional[int]
    job_id: Optional[int]
    event_type: str
    metadata: Optional[Dict[str, Any]]
    input_schema: Optional[Dict[str, Any]]
    output_schema: Optional[Dict[str, Any]]
    transformation_details: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True
