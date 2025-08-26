from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.exception import DataException
from app.schemas.exception import DataExceptionResponse, ExceptionResolutionRequest
from app.services.exception_service import ExceptionService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DataExceptionResponse])
async def list_exceptions(
    skip: int = 0,
    limit: int = 100,
    resolved: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DataException)
    if resolved is not None:
        query = query.filter(DataException.resolved == resolved)
    
    exceptions = query.offset(skip).limit(limit).all()
    return [
        DataExceptionResponse(
            id=exc.id,
            job_id=exc.job_id,
            exception_type=exc.exception_type,
            message=exc.message,
            severity=exc.severity,
            metadata=exc.metadata,
            resolved=exc.resolved,
            resolved_by=exc.resolved_by,
            resolution_notes=exc.resolution_notes,
            timestamp=exc.timestamp,
            resolved_at=exc.resolved_at
        )
        for exc in exceptions
    ]

@router.get("/{exception_id}", response_model=DataExceptionResponse)
async def get_exception(
    exception_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exception = db.query(DataException).filter(DataException.id == exception_id).first()
    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")
    
    return DataExceptionResponse(
        id=exception.id,
        job_id=exception.job_id,
        exception_type=exception.exception_type,
        message=exception.message,
        severity=exception.severity,
        metadata=exception.metadata,
        resolved=exception.resolved,
        resolved_by=exception.resolved_by,
        resolution_notes=exception.resolution_notes,
        timestamp=exception.timestamp,
        resolved_at=exception.resolved_at
    )

@router.post("/{exception_id}/resolve")
async def resolve_exception(
    exception_id: int,
    resolution: ExceptionResolutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = ExceptionService(db)
        success = await service.resolve_exception(
            exception_id=exception_id,
            resolved_by=current_user.id,
            resolution_notes=resolution.resolution_notes
        )
        if success:
            return {"status": "success", "message": "Exception resolved"}
        else:
            raise HTTPException(status_code=400, detail="Failed to resolve exception")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/job/{job_id}", response_model=List[DataExceptionResponse])
async def get_job_exceptions(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exceptions = db.query(DataException).filter(DataException.job_id == job_id).all()
    return [
        DataExceptionResponse(
            id=exc.id,
            job_id=exc.job_id,
            exception_type=exc.exception_type,
            message=exc.message,
            severity=exc.severity,
            metadata=exc.metadata,
            resolved=exc.resolved,
            resolved_by=exc.resolved_by,
            resolution_notes=exc.resolution_notes,
            timestamp=exc.timestamp,
            resolved_at=exc.resolved_at
        )
        for exc in exceptions
    ]
