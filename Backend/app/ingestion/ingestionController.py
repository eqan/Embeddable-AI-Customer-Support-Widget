from fastapi import APIRouter
from ingestion.dtos.ingestion import Ingestion, SearchDTO
from ingestion.ingestionService import ingestion_service
from fastapi import Depends 
from users.usersService import users_service
from config.config import limiter
from fastapi import Request

router = APIRouter(prefix="/ingestion")

@router.post("/", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
@limiter.limit("5/minute")
async def ingest_data(ingestion: Ingestion, request: Request):
    return ingestion_service.ingest_data(ingestion)

@router.post("/scrape-website", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
@limiter.limit("5/minute")
async def scrape_website(ingestion: Ingestion, request: Request):
    return ingestion_service.scrape_and_ingest_data(ingestion)

@router.get("/search", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
@limiter.limit("5/second")
async def search_in_pinecone(searchDTO: SearchDTO, request: Request):
    return ingestion_service.search_in_pinecone(searchDTO)