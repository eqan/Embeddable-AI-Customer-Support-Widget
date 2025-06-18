from fastapi import APIRouter
from ingestion.dtos.ingestion import Ingestion, SearchDTO
from ingestion.ingestionService import ingestion_service
from fastapi import Depends 
from users.usersService import users_service
from config.config import limiter
from fastapi import Request

router = APIRouter(prefix="/ingestion")

@router.post("/scrape-website", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
@limiter.limit("5/minute")
async def scrape_website(ingestion: Ingestion, request: Request):
    """
    This endpoint scrapes, purifies and ingests data into the system through the relevant urls provided.

    Request Body:
    - ingestion: Ingestion (required)
        - company_name: The name of the company whose data is to be scraped and ingested.
        - company_website: The official website of the company, which serves as a primary source for scraping.
        - relevant_links_to_be_scraped: A list of URLs that are relevant for data scraping, which may include pages other than the main website.

    Dependencies:
    - JWT token verification is required to access this endpoint.

    Rate Limiting:
    - This endpoint is limited to 5 requests per minute.
    """
    return ingestion_service.scrape_and_ingest_data(ingestion)

@router.get("/search", tags=["ingestion"], dependencies=[Depends(users_service.verify_jwt_token)])
@limiter.limit("5/second")
async def search_in_pinecone(searchDTO: SearchDTO, request: Request):
    """
    This endpoint allows searching within the Pinecone VectorDB using the provided search criteria.

    Request Query Parameters:
    - searchDTO: SearchDTO (required)
        - query: The search query string to be used for finding relevant content.
        - company_website: The website of the company to narrow down the search context.
        - top_k: The number of top results to return from the search, default is 3.

    Dependencies:
    - JWT token verification is required to access this endpoint.

    Rate Limiting:
    - This endpoint is limited to 5 requests per second.
    """
    return ingestion_service.search_in_pinecone(searchDTO)