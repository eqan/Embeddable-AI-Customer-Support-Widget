from pydantic import BaseModel, Field

class Ingestion(BaseModel):
    company_name: str = Field(..., description="The name of the company")
    company_website: str = Field(..., description="The website of the company")
    relevant_links_to_be_scraped: list[str] = Field(..., description="The relevant links to be scraped")