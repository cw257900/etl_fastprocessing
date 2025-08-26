from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.ingestion import DataIngestionRequest, SwiftMessageRequest, BatchUploadResponse
from app.services.ingestion_service import IngestionService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/api")
async def ingest_api_data(
    request: DataIngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = IngestionService(db)
        result = await service.process_api_data(request, current_user.id)
        return {"status": "success", "job_id": result.job_id, "message": "Data ingestion started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/swift")
async def ingest_swift_message(
    request: SwiftMessageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = IngestionService(db)
        result = await service.process_swift_message(request, current_user.id)
        return {"status": "success", "job_id": result.job_id, "message": "Swift message processing started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch", response_model=BatchUploadResponse)
async def upload_batch_file(
    file: UploadFile = File(...),
    source_id: int = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = IngestionService(db)
        result = await service.process_batch_file(file, source_id, current_user.id)
        
        background_tasks.add_task(service.process_uploaded_file, result.job_id)
        
        return BatchUploadResponse(
            job_id=result.job_id,
            filename=file.filename,
            file_size=result.file_size,
            status="uploaded",
            message="File uploaded successfully, processing started"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{job_id}")
async def get_ingestion_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = IngestionService(db)
    status = await service.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status
