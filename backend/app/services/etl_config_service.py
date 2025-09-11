import os
import json
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.processing_job import ProcessingJob, JobStatus
from app.services.config_driven_converter import ConfigDrivenETLConverter
from app.services.lineage_service import DataLineageService
from app.core.config import settings
from datetime import datetime

class ETLConfigService:
    def __init__(self, db: Session):
        self.db = db
        self.lineage_service = DataLineageService(db)
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')

    async def list_schemas(self) -> Dict[str, Any]:
        schemas = {}
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                schema_type = filename.replace('.json', '')
                with open(os.path.join(self.config_dir, filename), 'r') as f:
                    schemas[schema_type] = json.load(f)
        return schemas

    async def get_schema(self, schema_type: str) -> Dict[str, Any]:
        file_path = os.path.join(self.config_dir, f"{schema_type}.json")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Schema {schema_type} not found")
        
        with open(file_path, 'r') as f:
            return json.load(f)

    async def update_schema(self, schema_type: str, schema_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        file_path = os.path.join(self.config_dir, f"{schema_type}.json")
        
        with open(file_path, 'w') as f:
            json.dump(schema_data, f, indent=2)
        
        return {"status": "success", "message": f"Schema {schema_type} updated successfully"}

    async def process_etl_conversion(self, file: UploadFile, input_schema: str, output_schema: str, processing_rules: str, user_id: int) -> Dict[str, Any]:
        os.makedirs(settings.upload_dir, exist_ok=True)
        file_path = os.path.join(settings.upload_dir, file.filename)
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        job = ProcessingJob(
            name=f"ETL Conversion - {file.filename}",
            description=f"ETL conversion using {input_schema} -> {output_schema}",
            status=JobStatus.PENDING,
            input_data={
                "file_path": file_path,
                "filename": file.filename,
                "input_schema": input_schema,
                "output_schema": output_schema,
                "processing_rules": processing_rules
            },
            created_by=user_id
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        try:
            input_schema_path = os.path.join(self.config_dir, f"{input_schema}.json")
            output_schema_path = os.path.join(self.config_dir, f"{output_schema}.json") 
            processing_rules_path = os.path.join(self.config_dir, f"{processing_rules}.json")
            
            converter = ConfigDrivenETLConverter(input_schema_path, output_schema_path, processing_rules_path)
            
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            output_df = converter.convert_data(file_path)
            
            output_path = file_path.replace('.dat', '_converted.csv').replace('.csv', '_converted.csv')
            converter.save_output(output_df, output_path, 'csv')
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.output_data = {
                "output_file": output_path,
                "records_processed": len(output_df),
                "conversion_summary": "ETL conversion completed successfully"
            }
            self.db.commit()

            return {
                "job_id": job.id,
                "status": "success",
                "records_processed": len(output_df),
                "output_file": output_path
            }

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise HTTPException(status_code=400, detail=str(e))
