from ingestion.dtos.ingestion import Ingestion
from config.config import firecrawl_app, collection
from typing import JSON
from config.config import vo, embedding_model

class IngestionService:
    def ingest_data(self, ingestion: Ingestion):
        # Scrape multiple websites:
        batch_scrape_result = firecrawl_app.batch_scrape_urls(ingestion.relevant_links_to_be_scraped, formats=['markdown'])
        return batch_scrape_result
    

    def embed_text(self, text: str):
        """
        Returns a list of 1 embedding for the following input:
          1) Text
        """
        try:
          embedding_inputs = [text]
          result = vo.embed(embedding_inputs, model=embedding_model, input_type="query")
          embeddings = result.embeddings[0]
          return embeddings
        except Exception as e:
          print("Error in embedding model", str(e))
          return False

    def save_scraped_data(self, ingestion: Ingestion, scraped_data: JSON):
        # save the scraped data to the database
        collection.insert_many(scraped_data)