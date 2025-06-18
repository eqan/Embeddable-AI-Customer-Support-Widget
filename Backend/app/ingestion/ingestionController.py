from fastapi import APIRouter
from ingestion.dtos.ingestion import Ingestion, SearchDTO
from ingestion.ingestionService import ingestion_service
from fastapi import Depends
from users.usersService import users_service

router = APIRouter(prefix="/ingestion")

@router.post("/", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
async def ingest_data(ingestion: Ingestion):
    return ingestion_service.ingest_data(ingestion)

@router.post("/scrape-website", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
async def scrape_website(ingestion: Ingestion):
    return ingestion_service.scrape_and_ingest_data(ingestion)

@router.get("/search", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
async def search_in_pinecone(searchDTO: SearchDTO):
    return ingestion_service.search_in_pinecone(searchDTO)