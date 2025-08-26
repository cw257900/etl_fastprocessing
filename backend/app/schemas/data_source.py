from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.data_source import SourceType

class DataSourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: SourceType
    connection_config: Optional[Dict[str, Any]] = None
    schema_config: Optional[Dict[str, Any]] = None

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    schema_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class DataSourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_type: SourceType
    connection_config: Optional[Dict[str, Any]]
    schema_config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
