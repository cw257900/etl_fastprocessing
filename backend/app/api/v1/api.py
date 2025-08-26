from fastapi import APIRouter
from app.api.v1.endpoints import auth, data_sources, ingestion, processing, workflow, lineage, exceptions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(processing.router, prefix="/processing", tags=["processing"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
api_router.include_router(lineage.router, prefix="/lineage", tags=["lineage"])
api_router.include_router(exceptions.router, prefix="/exceptions", tags=["exceptions"])
