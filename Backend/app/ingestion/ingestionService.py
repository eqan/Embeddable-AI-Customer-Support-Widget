from ingestion.dtos.ingestion import Ingestion
from config.config import firecrawl_app, vo, settings
from ingestion.dtos.ingestion import WebsiteScrapeResult

class IngestionService:
    def scrape_websites(self, ingestion: Ingestion):
        batch_scrape_result = firecrawl_app.batch_scrape_urls(
            ingestion.relevant_links_to_be_scraped, formats=["markdown"]
        )

        # Convert to a plain dict if Firecrawl returns a Pydantic model (e.g., CrawlStatusResponse)
        if hasattr(batch_scrape_result, "model_dump"):
            batch_scrape_result = batch_scrape_result.model_dump()
        elif hasattr(batch_scrape_result, "dict"):
            batch_scrape_result = batch_scrape_result.dict()

        print(batch_scrape_result)
        return batch_scrape_result
    
    def firecrawl_cleaner(self, ingestion: Ingestion, batch_scrape_result: any):
        cleaned_data = []
        data = batch_scrape_result.get('data', [])

        for result, url in zip(data, ingestion.relevant_links_to_be_scraped):
            # Each `result` is a dict returned by Firecrawl for a single URL scrape
            # We only keep entries that contain markdown content.
            markdown = result.get("markdown")
            if not markdown:
                continue

            # Firecrawl nests most meta-tags under "metadata"
            metadata = result.get("metadata", {}) if isinstance(result, dict) else {}

            # Prefer OpenGraph tags, fall back to generic keys if missing
            description = (
                metadata.get("ogDescription")
                or metadata.get("description")
                or result.get("description", "")
            )

            title = (
                metadata.get("ogTitle")
                or metadata.get("title")
                or result.get("title", "")
            )
            
            url = (metadata.get("ogUrl") or metadata.get("url") or result.get("url", ""))

            cleaned_data.append(
                WebsiteScrapeResult(
                    url=url,
                    markdown=markdown,
                    description=description or "",
                    title=title or "",
                )
            )
        return cleaned_data

    def ingest_data(self, ingestion: Ingestion):
        batch_scrape_result = self.scrape_websites(ingestion)
        cleaned_data = self.firecrawl_cleaner(ingestion, batch_scrape_result)
        print(cleaned_data)
        return cleaned_data

    def embed_text(self, text: str):
        """
        Returns a list of 1 embedding for the following input:
          1) Text
        """
        try:
          embedding_inputs = [text]
          result = vo.embed(embedding_inputs, model=settings.embedding_model, input_type="query")
          embeddings = result.embeddings[0]
          return embeddings
        except Exception as e:
          print("Error in embedding model", str(e))
          return False

    def save_scraped_data(self, ingestion: Ingestion, scraped_data: dict):
        # save the scraped data to the database
        # collection.insert_many(scraped_data)
        return None

# Create a shared instance that can be imported elsewhere (e.g. the controller)
ingestionService = IngestionService()