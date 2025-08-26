from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Boolean
from datetime import datetime
import enum
from app.core.database import Base

class WorkflowState(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class ApprovalType(enum.Enum):
    DATA_PROMOTION = "data_promotion"
    SCHEMA_CHANGE = "schema_change"
    JOB_EXECUTION = "job_execution"

class WorkflowApproval(Base):
    __tablename__ = "workflow_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("processing_jobs.id"))
    approval_type = Column(Enum(ApprovalType), nullable=False)
    state = Column(Enum(WorkflowState), default=WorkflowState.PENDING)
    submitted_by = Column(Integer, nullable=False)
    approved_by = Column(Integer)
    comments = Column(Text)
    additional_metadata = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
