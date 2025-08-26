from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, Boolean, Text
from datetime import datetime
import enum
from app.core.database import Base

class SourceType(enum.Enum):
    API = "api"
    SWIFT = "swift"
    BATCH = "batch"

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    source_type = Column(Enum(SourceType), nullable=False)
    connection_config = Column(JSON)
    schema_config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
