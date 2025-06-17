from ingestion.dtos.ingestion import Ingestion
from config.config import firecrawl_app, vo, settings
from ingestion.dtos.ingestion import WebsiteScrapeResult
from prompts.load_prompt import load_prompt
import concurrent.futures
import json
import re
from fastapi import HTTPException
from config.config import index
import ast

class IngestionService:
    def scrape_websites(self, ingestion: Ingestion) -> any:
        batch_scrape_result = firecrawl_app.batch_scrape_urls(
            ingestion.relevant_links_to_be_scraped, formats=["markdown"]
        )

        # Convert to a plain dict if Firecrawl returns a Pydantic model (e.g., CrawlStatusResponse)
        if hasattr(batch_scrape_result, "model_dump"):
            batch_scrape_result = batch_scrape_result.model_dump()
        elif hasattr(batch_scrape_result, "dict"):
            batch_scrape_result = batch_scrape_result.dict()

        return batch_scrape_result
    
    def firecrawl_cleaner(self, ingestion: Ingestion, batch_scrape_result: any) -> [WebsiteScrapeResult]:
        cleaned_data = []
        data = batch_scrape_result.get('data', [])
        for result, url in zip(data, ingestion.relevant_links_to_be_scraped):
            print(result)
            # Each `result` is a dict returned by Firecrawl for a single URL scrape
            # We only keep entries that contain markdown content.
            markdown = result.get('markdown')
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

    def deep_seek_api_call(self, prompt: str):
            import requests

            url = "https://api.deepseek.com/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.reasoning_model_api_key}"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": prompt},
                ],
                "stream": False
            }
            response = requests.post(url, headers=headers, json=data)
            return response.json()
    
    def generate_data_for_ingestion(self, list_of_data: [WebsiteScrapeResult], ingestion: Ingestion):
        generated_data = []
        print(list_of_data)
        def process_data(data: WebsiteScrapeResult, ingestion: Ingestion):
            url = data.url
            company_name = ingestion.company_name
            company_website = ingestion.company_website
            prompt = load_prompt("data-generation-for-ingestion")
            prompt = prompt.replace("{markdown}", data.markdown)
            prompt = prompt.replace("{description}", data.description)
            prompt = prompt.replace("{title}", data.title)
            prompt = prompt.replace("{url}", url)
            response = self.deep_seek_api_call(prompt)
            # The model usually returns a JSON string. Remove any markdown code fences and parse it.
            content_str = response.get('choices')[0].get('message').get('content', "")
            # Strip common markdown JSON fences if present
            if content_str.strip().startswith("```"):
                content_str = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", content_str.strip())

            try:
                data = json.loads(content_str)
                data['source_url'] = url
                data['company_name'] = company_name
                data['company_website'] = company_website

                return data
            except json.JSONDecodeError as e:
                # Log & fall back to raw string to avoid crashing the whole ingestion pipeline
                print(f"[generate_data_for_ingestion] JSON decode error: {e}. Returning raw content.")
                return content_str

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_data, list_of_data, ingestion))

        generated_data.extend(results)
        return generated_data

    def ingest_data(self, ingestion: Ingestion):
        batch_scrape_result = self.scrape_websites(ingestion)
        cleaned_data = self.firecrawl_cleaner(ingestion, batch_scrape_result)
        generated_data = self.generate_data_for_ingestion(cleaned_data, ingestion)
        data = self.embed_inputs(generated_data)
        return data
    
    def embed_inputs(self, array_of_data: [WebsiteScrapeResult]):
        data_for_pinecone = []
        for data in array_of_data:
            _data = {
                "id": data.url,
                "values": self.embed_text(f"{data['title']} {data['section']} {data['content_type']} {data['summarized_content']}"),
                "metadata": data
            }
            data_for_pinecone.append(_data)
        return data_for_pinecone

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
        generated_data = self.ingest_data(ingestion)
        self.upsert_in_pinecone(generated_data)
        return generated_data

    def upsert_in_pinecone(self, data: dict):
        try:
            index.upsert(
                vectors=data,
                namespace=settings.pinecone_index_name
            )
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_all_record_ids_from_pinecone(self) -> list:
        ids_list = []
        for ids in index.list(namespace=settings.pinecone_index_name):
            for id in ids:
                ids_list.append(id)
        return ids_list

    def search_in_pinecone(self, query: str, top_k: int = 3) -> dict:
        try:
            print("I'm here at embedding")
            embedding = self.embed_text(query)
            results = None
            if embedding:
                results = index.query(
                    namespace=settings.pinecone_index_name,
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True
                )
            else:
               results = index.search(
                    namespace=settings.pinecone_index_name,
                    query={
                        "inputs":{
                                "text": query,
                        },
                        "top_k": top_k,
                        "include_metadata": True
                    }
                ) 
            # Convert the string to a Python dictionary:
            python_dict = ast.literal_eval(str(results))
            # Serialize the Python dictionary to JSON format:
            return python_dict
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# Create a shared instance that can be imported elsewhere (e.g. the controller)
ingestionService = IngestionService()