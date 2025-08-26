from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DataLineage(Base):
    __tablename__ = "data_lineage"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"))
    job_id = Column(Integer, ForeignKey("processing_jobs.id"))
    event_type = Column(String, nullable=False)
    metadata = Column(JSON)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    transformation_details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
