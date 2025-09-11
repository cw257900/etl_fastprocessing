from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.services.etl_config_service import ETLConfigService
import json
import os

router = APIRouter()

@router.get("/schemas")
async def list_config_schemas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ETLConfigService(db)
    return await service.list_schemas()

@router.get("/schemas/{schema_type}")
async def get_config_schema(
    schema_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ETLConfigService(db)
    return await service.get_schema(schema_type)

@router.put("/schemas/{schema_type}")
async def update_config_schema(
    schema_type: str,
    schema_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ETLConfigService(db)
    return await service.update_schema(schema_type, schema_data, current_user.id)

@router.post("/convert")
async def convert_etl_data(
    file: UploadFile = File(...),
    input_schema: str = "input_schema",
    output_schema: str = "output_schema", 
    processing_rules: str = "processing_rules",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ETLConfigService(db)
    return await service.process_etl_conversion(file, input_schema, output_schema, processing_rules, current_user.id)
