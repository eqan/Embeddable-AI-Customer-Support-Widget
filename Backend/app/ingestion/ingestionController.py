from fastapi import APIRouter
from ingestion.dtos.ingestion import Ingestion
from ingestion.ingestionService import ingestionService

router = APIRouter()

@router.post("/ingestion")
async def ingest_data(ingestion: Ingestion):
    return ingestionService.ingest_data(ingestion)