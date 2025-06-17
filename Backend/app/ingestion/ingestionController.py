from fastapi import APIRouter
from ingestion.dtos.ingestion import Ingestion
from ingestion.ingestionService import ingestionService

router = APIRouter(prefix="/ingestion")

@router.post("/", tags=["ingestion"])
async def ingest_data(ingestion: Ingestion):
    return ingestionService.ingest_data(ingestion)

@router.post("/scrape-website", tags=["ingestion"])
async def scrape_website(ingestion: Ingestion):
    return ingestionService.ingest_data(ingestion)