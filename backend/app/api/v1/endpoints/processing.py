from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.processing_job import ProcessingJob
from app.schemas.processing import ProcessingJobResponse, TransformationRuleCreate
from app.services.data_processing_service import DataProcessingService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/jobs", response_model=List[ProcessingJobResponse])
async def list_processing_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    jobs = db.query(ProcessingJob).offset(skip).limit(limit).all()
    return [
        ProcessingJobResponse(
            id=job.id,
            name=job.name,
            description=job.description,
            source_id=job.source_id,
            status=job.status,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at
        )
        for job in jobs
    ]

@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
async def get_processing_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    return ProcessingJobResponse(
        id=job.id,
        name=job.name,
        description=job.description,
        source_id=job.source_id,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        transformation_rules=job.transformation_rules,
        error_message=job.error_message
    )

@router.post("/jobs/{job_id}/transform")
async def apply_transformation_rules(
    job_id: int,
    rules: List[TransformationRuleCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    try:
        service = DataProcessingService(db)
        result = await service.apply_transformation_rules(job, rules)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/jobs/{job_id}/retry")
async def retry_processing_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    try:
        service = DataProcessingService(db)
        result = await service.retry_job(job)
        return {"status": "success", "message": "Job retry initiated", "new_job_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
