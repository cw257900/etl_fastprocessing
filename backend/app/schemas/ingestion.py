from pydantic import BaseModel
from typing import Optional, Dict, Any

class DataIngestionRequest(BaseModel):
    source_id: int
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class SwiftMessageRequest(BaseModel):
    message_type: str
    message_content: str
    sender: str
    receiver: str
    metadata: Optional[Dict[str, Any]] = None

class BatchUploadResponse(BaseModel):
    job_id: int
    filename: str
    file_size: int
    status: str
    message: str
