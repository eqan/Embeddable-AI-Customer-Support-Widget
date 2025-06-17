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
    
    def generate_data_for_ingestion(self, list_of_data: [WebsiteScrapeResult]):
        generated_data = []
        print(list_of_data)
        def process_data(data: WebsiteScrapeResult):
            prompt = load_prompt("data-generation-for-ingestion")
            prompt = prompt.replace("{markdown}", data.markdown)
            prompt = prompt.replace("{description}", data.description)
            prompt = prompt.replace("{title}", data.title)
            prompt = prompt.replace("{url}", data.url)
            response = self.deep_seek_api_call(prompt)
            # The model usually returns a JSON string. Remove any markdown code fences and parse it.
            content_str = response.get('choices')[0].get('message').get('content', "")
            # Strip common markdown JSON fences if present
            if content_str.strip().startswith("```"):
                content_str = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", content_str.strip())

            try:
                return json.loads(content_str)
            except json.JSONDecodeError as e:
                # Log & fall back to raw string to avoid crashing the whole ingestion pipeline
                print(f"[generate_data_for_ingestion] JSON decode error: {e}. Returning raw content.")
                return content_str

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_data, list_of_data))

        generated_data.extend(results)
        return generated_data

    def ingest_data(self, ingestion: Ingestion):
        # batch_scrape_result = self.scrape_websites(ingestion)
        # cleaned_data = self.firecrawl_cleaner(ingestion, batch_scrape_result)
        # generated_data = self.generate_data_for_ingestion(cleaned_data)
        generated_data: [WebsiteScrapeResult] = [
    {
        "summarized_content": "Crumbl Cookies offers a variety of freshly baked, gourmet cookies and desserts with unique and trendy flavors that change weekly. The menu for the week of June 16-21 features national flavors, including the Semi-Sweet Chocolate Chunk Cookie, Peanut Butter Cup Skillet Cookie (featuring REESE'S), Berry Trifle Cake Cup, Wedding Cake Cookie, Chocolate Toffee Cake Cookie (featuring HEATH), Cinnamon Roll Cookie, and Triple Chocolate Chip Cookie. Each item is described with its key ingredients and flavors, emphasizing real ingredients like eggs, butter, sugar, and house-made jams. The desserts are available for takeout, delivery, or pick-up, made fresh daily.",
        "cleaned_content": "# Crumbl Cookies Menu - Week of June 16-21\n\n## National Flavors\n\n### Semi-Sweet Chocolate Chunk Cookie\nA delicious cookie filled with irresistible semi-sweet chocolate chunks and a sprinkle of flaky sea salt.\n\n### Peanut Butter Cup Skillet Cookie (ft. REESE'S)\nA peanut butter cookie topped with Peanut Butter Cup mousse, drizzled with melted milk chocolate, and topped with more Peanut Butter Cup pieces.\n\n### Berry Trifle Cake Cup\nLayers of light vanilla cake, vanilla pudding, and house-made mixed berry jam served in a cup. Not available in mini sizes.\n\n### Wedding Cake Cookie\nA warm vanilla bean sugar cookie topped with an elegant swirl of vanilla and raspberry cream cheese frosting and a light crunch of white chocolate pearls.\n\n### Chocolate Toffee Cake Cookie (ft. HEATH)\nA gooey chocolate cake-inspired cookie layered with fluffy whipped cream, milky caramel glaze, and crunchy HEATH pieces.\n\n### Cinnamon Roll Cookie\nA vanilla sugar cookie topped with cinnamon streusel and swirled with vanilla cream cheese frosting.\n\n### Triple Chocolate Chip Cookie\nA chocolate cookie packed with semi-sweet chunks, creamy white chips, and milk chocolate chips.\n\nAll desserts are made with real ingredients like eggs, butter, sugar, and house-made jams, ensuring fresh and flavorful treats daily.",
        "content_type": "Menu",
        "metadata": {
            "flavors": [
                "Semi-Sweet Chocolate Chunk Cookie",
                "Peanut Butter Cup Skillet Cookie",
                "Berry Trifle Cake Cup",
                "Wedding Cake Cookie",
                "Chocolate Toffee Cake Cookie",
                "Cinnamon Roll Cookie",
                "Triple Chocolate Chip Cookie"
            ],
            "availability": "Week of June 16-21",
            "ingredients": [
                "real eggs",
                "butter",
                "sugar",
                "flour",
                "house-made jams"
            ],
            "brand_collaborations": [
                "REESE'S",
                "HEATH"
            ]
        },
        "title": "Crumbl Cookies Menu - National Flavors",
        "section": "Bakery Menu"
    },
    {
        "summarized_content": "The Crumbl merchandise homepage features a Father's Day collection, highlighting new products like Crumbl Dad Things Socks, Crumbl Trail Snapback, and Mom Club Crewneck. The page emphasizes limited-time offers, such as ordering by June 4 to receive items in time for Father's Day celebrations. Additional featured items include Pink Comfort Slippers, Crumbl Lapel Pin Set, and Pastel Comfort Lounge Shorts. The 'All Merch' section showcases a broader range of products, from apparel to accessories like the Insulated Crumblr and Crumbl Dessert Keychains. The page is designed to promote seasonal and limited-edition merchandise.",
        "cleaned_content": "# The Father’s Day Merch Drop is Live!\n\n**Order your Father’s Day merch by Jun 4 and get it in time for the celebrations!**\n\n[View the Collection](https://merch.crumbl.com/collections/fathers-day)\n\n## What's New\n\n### Crumbl Dad Things Socks\nRegular price: $10.00\n\n### Crumbl Trail Snapback\nRegular price: $25.00\n\n### Mom Club Crewneck\nRegular price: $70.00\n\n### Pink Comfort Slippers\nRegular price: $15.00\n\n### Crumbl Lapel Pin Set\nRegular price: $18.00\n\n### Pastel Comfort Lounge Shorts\nRegular price: $35.00\n\n### Pastel Comfort Crewneck\nRegular price: $40.00\n\n### Apron & Oven Mitt Set\nRegular price: $45.00\n\n## All Merch\n\n### Crumbl Dad Things Socks\nRegular price: $10.00\n\n### Crumbl Trail Snapback\nRegular price: $25.00\n\n### Dadcrew Tee\nRegular price: $30.00 (Sold out)\n\n### Mom Club Crewneck\nRegular price: $70.00\n\n### Pink Comfort Slippers\nRegular price: $15.00\n\n### Crumbl Lapel Pin Set\nRegular price: $18.00\n\n### Pastel Comfort Lounge Shorts\nRegular price: $35.00\n\n### Pastel Comfort Crewneck\nRegular price: $40.00\n\n### Apron & Oven Mitt Set\nRegular price: $45.00\n\n### Pink Insulated Water Bottle\nRegular price: $25.00\n\n### Crumbl Everyday Backpack\nRegular price: $40.00\n\n### Insulated Crumblr\nRegular price: $35.00\n\n### Crumbl Dessert Keychains\nRegular price: $5.00\n\n### Crumbl® Minky Couture® Blanket\nRegular price: $150.00\n\n### Crumbl Pink Box Keychain\nRegular price: $5.00",
        "content_type": "Product Collection",
        "metadata": {
            "keywords": [
                "Father's Day",
                "merchandise",
                "limited edition",
                "seasonal"
            ],
            "products": [
                "Crumbl Dad Things Socks",
                "Crumbl Trail Snapback",
                "Mom Club Crewneck",
                "Pink Comfort Slippers",
                "Crumbl Lapel Pin Set",
                "Pastel Comfort Lounge Shorts",
                "Pastel Comfort Crewneck",
                "Apron & Oven Mitt Set",
                "Pink Insulated Water Bottle",
                "Crumbl Everyday Backpack",
                "Insulated Crumblr",
                "Crumbl Dessert Keychains",
                "Crumbl® Minky Couture® Blanket",
                "Crumbl Pink Box Keychain"
            ]
        },
        "title": "Father’s Day Merch Drop",
        "section": "Bakery Merchandise"
    }
]
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