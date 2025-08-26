from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.data_lineage import DataLineage
from app.schemas.lineage import DataLineageResponse
from app.services.lineage_service import DataLineageService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/job/{job_id}", response_model=List[DataLineageResponse])
async def get_job_lineage(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lineage_records = db.query(DataLineage).filter(DataLineage.job_id == job_id).all()
    return [
        DataLineageResponse(
            id=record.id,
            source_id=record.source_id,
            job_id=record.job_id,
            event_type=record.event_type,
            metadata=record.metadata,
            input_schema=record.input_schema,
            output_schema=record.output_schema,
            transformation_details=record.transformation_details,
            timestamp=record.timestamp
        )
        for record in lineage_records
    ]

@router.get("/source/{source_id}", response_model=List[DataLineageResponse])
async def get_source_lineage(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lineage_records = db.query(DataLineage).filter(DataLineage.source_id == source_id).all()
    return [
        DataLineageResponse(
            id=record.id,
            source_id=record.source_id,
            job_id=record.job_id,
            event_type=record.event_type,
            metadata=record.metadata,
            input_schema=record.input_schema,
            output_schema=record.output_schema,
            transformation_details=record.transformation_details,
            timestamp=record.timestamp
        )
        for record in lineage_records
    ]

@router.get("/trace/{job_id}")
async def trace_data_flow(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = DataLineageService(db)
        trace = await service.trace_data_flow(job_id)
        return {"status": "success", "trace": trace}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
