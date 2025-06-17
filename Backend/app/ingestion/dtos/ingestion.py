from pydantic import BaseModel, Field

class Ingestion(BaseModel):
    company_name: str = Field(..., description="The name of the company")
    company_website: str = Field(..., description="The website of the company")
    relevant_links_to_be_scraped: list[str] = Field(..., description="The relevant links to be scraped")

class WebsiteScrapeResult(BaseModel):
    url: str
    markdown: str
    description: str #ogDescription
    title: str #ogTitle

class IngestionData(BaseModel):
    content: str = Field(..., description="The actual text content")
    summarized_content: str = Field("", description="Summarized content of the chunk")
    vector_embedding: list[float] = Field(..., description="The embedding vector of the content")
    
    company_name: str = Field(..., description="From client API input")
    company_website: str = Field(..., description="From client API input")
    source_url: str = Field(..., description="The specific URL where this chunk was found")
    description: str = Field(..., description="The description of the website")
    content_type: str = Field(..., description="Categorization (e.g., 'FAQ', 'Project', 'Doctor Profile', 'Medical Department', 'General Info')")
    title: str = Field(..., description="Title or heading of the section this chunk belongs to")
    section: str = Field(..., description="Broader section or category within the source")
    
    metadata: dict = Field(..., description="A dictionary for use-case specific attributes")