from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from datetime import datetime
from app.core.database import Base

class DataLineage(Base):
    __tablename__ = "data_lineage"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"))
    job_id = Column(Integer, ForeignKey("processing_jobs.id"))
    event_type = Column(String, nullable=False)
    additional_metadata = Column(JSON)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    transformation_details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
