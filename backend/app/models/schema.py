from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DetectedSchema(Base):
    __tablename__ = "detected_schemas"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"))
    schema_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=0.0)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer)
    detection_method = Column(String)
    sample_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
