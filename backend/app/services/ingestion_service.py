import os
import json
import aiofiles
from typing import Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.processing_job import ProcessingJob, JobStatus
from app.models.data_source import DataSource
from app.schemas.ingestion import DataIngestionRequest, SwiftMessageRequest
from app.services.schema_detection_service import SchemaDetectionService
from app.services.lineage_service import DataLineageService
from app.core.config import settings

class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.schema_service = SchemaDetectionService(db)
        self.lineage_service = DataLineageService(db)
        
        os.makedirs(settings.upload_dir, exist_ok=True)

    async def process_api_data(self, request: DataIngestionRequest, user_id: int):
        data_source = self.db.query(DataSource).filter(DataSource.id == request.source_id).first()
        if not data_source:
            raise ValueError("Data source not found")

        job = ProcessingJob(
            name=f"API Ingestion - {data_source.name}",
            description="Data ingestion via API endpoint",
            source_id=request.source_id,
            status=JobStatus.PENDING,
            input_data=request.data,
            created_by=user_id
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        await self.lineage_service.track_data_ingestion(
            source_id=request.source_id,
            job_id=job.id,
            metadata={
                "ingestion_type": "api",
                "data_size": len(str(request.data)),
                "metadata": request.metadata
            }
        )

        detected_schema = await self.schema_service.detect_schema(
            data=request.data,
            source_type="json",
            source_id=request.source_id
        )

        return job

    async def process_swift_message(self, request: SwiftMessageRequest, user_id: int):
        job = ProcessingJob(
            name=f"Swift Message - {request.message_type}",
            description=f"Swift message processing from {request.sender} to {request.receiver}",
            status=JobStatus.PENDING,
            input_data={
                "message_type": request.message_type,
                "message_content": request.message_content,
                "sender": request.sender,
                "receiver": request.receiver,
                "metadata": request.metadata
            },
            created_by=user_id
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        await self.lineage_service.track_data_ingestion(
            source_id=None,
            job_id=job.id,
            metadata={
                "ingestion_type": "swift",
                "message_type": request.message_type,
                "sender": request.sender,
                "receiver": request.receiver
            }
        )

        parsed_message = await self._parse_swift_message(request.message_content, request.message_type)
        
        detected_schema = await self.schema_service.detect_schema(
            data=parsed_message,
            source_type="swift",
            source_id=None
        )

        return job

    async def process_batch_file(self, file: UploadFile, source_id: int, user_id: int):
        if file.size > settings.max_file_size:
            raise ValueError(f"File size exceeds maximum allowed size of {settings.max_file_size} bytes")

        file_path = os.path.join(settings.upload_dir, f"{file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        job = ProcessingJob(
            name=f"Batch Upload - {file.filename}",
            description=f"Batch file processing for {file.filename}",
            source_id=source_id,
            status=JobStatus.PENDING,
            input_data={
                "file_path": file_path,
                "filename": file.filename,
                "file_size": file.size,
                "content_type": file.content_type
            },
            created_by=user_id
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        await self.lineage_service.track_data_ingestion(
            source_id=source_id,
            job_id=job.id,
            metadata={
                "ingestion_type": "batch",
                "filename": file.filename,
                "file_size": file.size,
                "content_type": file.content_type
            }
        )

        return job

    async def process_uploaded_file(self, job_id: int):
        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return

        try:
            job.status = JobStatus.RUNNING
            self.db.commit()

            file_path = job.input_data.get("file_path")
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.csv':
                data = await self._process_csv_file(file_path)
            elif file_extension in ['.json']:
                data = await self._process_json_file(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                data = await self._process_excel_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            detected_schema = await self.schema_service.detect_schema(
                data=data,
                source_type=file_extension[1:],
                source_id=job.source_id
            )

            job.status = JobStatus.COMPLETED
            job.output_data = {"processed_data": data, "schema": detected_schema.schema_data}
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
        
        self.db.commit()

    async def get_job_status(self, job_id: int):
        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return None
        
        return {
            "job_id": job.id,
            "status": job.status,
            "name": job.name,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message
        }

    async def _parse_swift_message(self, message_content: str, message_type: str) -> Dict[str, Any]:
        parsed = {
            "message_type": message_type,
            "raw_content": message_content,
            "fields": {}
        }
        
        lines = message_content.split('\n')
        for line in lines:
            if line.startswith(':'):
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    field_code = parts[1]
                    field_value = parts[2]
                    parsed["fields"][field_code] = field_value
        
        return parsed

    async def _process_csv_file(self, file_path: str) -> Dict[str, Any]:
        import pandas as pd
        df = pd.read_csv(file_path)
        return {
            "columns": df.columns.tolist(),
            "data": df.to_dict('records'),
            "row_count": len(df)
        }

    async def _process_json_file(self, file_path: str) -> Dict[str, Any]:
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            return json.loads(content)

    async def _process_excel_file(self, file_path: str) -> Dict[str, Any]:
        import pandas as pd
        df = pd.read_excel(file_path)
        return {
            "columns": df.columns.tolist(),
            "data": df.to_dict('records'),
            "row_count": len(df)
        }
