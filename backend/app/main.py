from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ETL Fast Processing API",
    description="Comprehensive ETL tool for data onboarding and processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "ETL Fast Processing API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
