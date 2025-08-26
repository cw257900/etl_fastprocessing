from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.data_source import DataSource
from app.models.user import User
from app.schemas.data_source import DataSourceCreate, DataSourceResponse, DataSourceUpdate
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=DataSourceResponse)
async def create_data_source(
    data_source: DataSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_data_source = DataSource(
        name=data_source.name,
        description=data_source.description,
        source_type=data_source.source_type,
        connection_config=data_source.connection_config,
        schema_config=data_source.schema_config,
        created_by=current_user.id
    )
    db.add(db_data_source)
    db.commit()
    db.refresh(db_data_source)
    
    return DataSourceResponse(
        id=db_data_source.id,
        name=db_data_source.name,
        description=db_data_source.description,
        source_type=db_data_source.source_type,
        connection_config=db_data_source.connection_config,
        schema_config=db_data_source.schema_config,
        is_active=db_data_source.is_active,
        created_at=db_data_source.created_at,
        updated_at=db_data_source.updated_at
    )

@router.get("/", response_model=List[DataSourceResponse])
async def list_data_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data_sources = db.query(DataSource).offset(skip).limit(limit).all()
    return [
        DataSourceResponse(
            id=ds.id,
            name=ds.name,
            description=ds.description,
            source_type=ds.source_type,
            connection_config=ds.connection_config,
            schema_config=ds.schema_config,
            is_active=ds.is_active,
            created_at=ds.created_at,
            updated_at=ds.updated_at
        )
        for ds in data_sources
    ]

@router.get("/{data_source_id}", response_model=DataSourceResponse)
async def get_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return DataSourceResponse(
        id=data_source.id,
        name=data_source.name,
        description=data_source.description,
        source_type=data_source.source_type,
        connection_config=data_source.connection_config,
        schema_config=data_source.schema_config,
        is_active=data_source.is_active,
        created_at=data_source.created_at,
        updated_at=data_source.updated_at
    )

@router.put("/{data_source_id}", response_model=DataSourceResponse)
async def update_data_source(
    data_source_id: int,
    data_source_update: DataSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    for field, value in data_source_update.dict(exclude_unset=True).items():
        setattr(data_source, field, value)
    
    db.commit()
    db.refresh(data_source)
    
    return DataSourceResponse(
        id=data_source.id,
        name=data_source.name,
        description=data_source.description,
        source_type=data_source.source_type,
        connection_config=data_source.connection_config,
        schema_config=data_source.schema_config,
        is_active=data_source.is_active,
        created_at=data_source.created_at,
        updated_at=data_source.updated_at
    )

@router.delete("/{data_source_id}")
async def delete_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    data_source.is_active = False
    db.commit()
    
    return {"message": "Data source deactivated successfully"}
