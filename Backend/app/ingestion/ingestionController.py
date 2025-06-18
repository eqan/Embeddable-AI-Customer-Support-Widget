from fastapi import APIRouter
from ingestion.dtos.ingestion import Ingestion, SearchDTO
from ingestion.ingestionService import ingestionService

router = APIRouter(prefix="/ingestion")

@router.post("/", tags=["ingestion"])
async def ingest_data(ingestion: Ingestion):
    return ingestionService.ingest_data(ingestion)

@router.post("/scrape-website", tags=["ingestion"])
async def scrape_website(ingestion: Ingestion):
    return ingestionService.scrape_and_ingest_data(ingestion)

@router.get("/search", tags=["ingestion"])
async def search_in_pinecone(searchDTO: SearchDTO):
    return ingestionService.search_in_pinecone(searchDTO)