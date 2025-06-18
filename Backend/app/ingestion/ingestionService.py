from ingestion.dtos.ingestion import Ingestion
from config.config import firecrawl_app, vo, settings
from ingestion.dtos.ingestion import WebsiteScrapeResult, SearchDTO
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
            # print(result)
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
        def process_data(item: WebsiteScrapeResult):
            """Handle a single WebsiteScrapeResult (or compatible dict)."""
            # Allow both pydantic objects *and* plain dicts so the function is robust
            markdown = getattr(item, "markdown", None) or item.get("markdown")
            description = getattr(item, "description", None) or item.get("description", "")
            title = getattr(item, "title", None) or item.get("title", "")
            url = getattr(item, "url", None) or item.get("url", "")
            print("This was the item", item)

            prompt = load_prompt("data-generation-for-ingestion")
            prompt = prompt.replace("{markdown}", markdown or "")
            prompt = prompt.replace("{description}", description)
            prompt = prompt.replace("{title}", title)
            prompt = prompt.replace("{url}", url or "")
            # print("Prompt", prompt)

            response = self.deep_seek_api_call(prompt)
            # The model usually returns a JSON string. Remove any markdown code fences and parse it.
            content_str = response.get('choices')[0].get('message').get('content', "")
            print("Content",content_str)
            # Strip common markdown JSON fences if present
            if content_str.strip().startswith("```"):
                content_str = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", content_str.strip())

            try:
                parsed = json.loads(content_str)
                parsed['source_url'] = url
                parsed['company_name'] = ingestion.company_name
                parsed['company_website'] = ingestion.company_website
                parsed['specific_metadata'] = json.dumps(parsed['specific_metadata'])
                print("Parsed", parsed)
                return parsed
            except json.JSONDecodeError as e:
                # Log & fall back to raw string to avoid crashing the whole ingestion pipeline
                print(f"[generate_data_for_ingestion] JSON decode error: {e}. Returning raw content.")
                return content_str

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_data, list_of_data))
        print("Results", results)
        generated_data.extend(results)
        return generated_data

    def ingest_data(self, ingestion: Ingestion):
        # batch_scrape_result = self.scrape_websites(ingestion)
        # cleaned_data = self.firecrawl_cleaner(ingestion, batch_scrape_result)
        cleaned_data: [WebsiteScrapeResult] = [
    {
        "url": "https://merch.crumbl.com/collections/home",
        "markdown": "[Skip to content](https://merch.crumbl.com/collections/home#MainContent)\n\n![](https://merch.crumbl.com/cdn/shop/files/hero3.jpg?v=1747954637&width=2160)\n\n![](https://merch.crumbl.com/cdn/shop/files/mobileArtboard_2.jpg?v=1747954768&width=720)\n\n# The\n\n# Father's Day\n\n# Merch Drop\n\n# is Live!\n\n**Order your Father's Day merch by Jun 4 and get it in time for the celebrations!**\n\n[View the Collection](https://merch.crumbl.com/collections/fathers-day)\n\n## What's New\n\nWhat's New\n\n[![Crumbl Dad Things Socks](https://merch.crumbl.com/cdn/shop/files/Father_sDaySocks_Green_OverheadAerialCompressed.jpg?v=1748032046&width=4320)![Crumbl Dad Things Socks](https://merch.crumbl.com/cdn/shop/files/Father_sDaySocks_Green_ToeDetailCompressed.jpg?v=1748032046&width=4320)](https://merch.crumbl.com/products/dad-crew-socks?variant=46472741486828 \"Go to Crumbl Dad Things Socks\")\n\n### [Crumbl Dad Things Socks](https://merch.crumbl.com/products/dad-crew-socks?variant=46472741486828 \"Go to Crumbl Dad Things Socks\")new\n\nRegular price$10.00\n\n[![Crumbl Trail Snapback](https://merch.crumbl.com/cdn/shop/files/Father_sDayHat_OverheadAerialCompressed.jpg?v=1747940175&width=4320)![Crumbl Trail Snapback](https://merch.crumbl.com/cdn/shop/files/FathersDayMerch_Hat_2_1x1Compressed_53a14057-6422-4764-90c3-22ca31b2a6ef.jpg?v=1747952056&width=1800)](https://merch.crumbl.com/products/crumbl-trail-snapback?variant=46472736145644 \"Go to Crumbl Trail Snapback\")\n\n### [Crumbl Trail Snapback](https://merch.crumbl.com/products/crumbl-trail-snapback?variant=46472736145644 \"Go to Crumbl Trail Snapback\")new\n\nRegular price$25.00\n\n[![Mom Club Crewneck](https://merch.crumbl.com/cdn/shop/files/Dandy_Mother_sDaySweater_OverheadAerialCompressed.png?v=1745876779&width=3600)![Mom Club Crewneck](https://merch.crumbl.com/cdn/shop/files/Dandy_MothersDayMerch_Sweatshirt_3Compressed.jpg?v=1745876779&width=3600)](https://merch.crumbl.com/products/crumbl-mom-crewneck?variant=46358447063276 \"Go to Mom Club Crewneck\")\n\n### [Mom Club Crewneck](https://merch.crumbl.com/products/crumbl-mom-crewneck?variant=46358447063276 \"Go to Mom Club Crewneck\")Ltd. Editionnew\n\nRegular price$70.00\n\n[![Pink Comfort Slippers](https://merch.crumbl.com/cdn/shop/files/PinkCrumblSlippers_OverheadAerial.png?v=1744225945&width=4320)![Pink Comfort Slippers](https://merch.crumbl.com/cdn/shop/files/MothersDayMerch_Slippers_1Compressed.jpg?v=1745252674&width=4320)](https://merch.crumbl.com/products/slippers?variant=46352000221420 \"Go to Pink Comfort Slippers\")\n\n### [Pink Comfort Slippers](https://merch.crumbl.com/products/slippers?variant=46352000221420 \"Go to Pink Comfort Slippers\")new\n\nRegular price$15.00\n\n[![Crumbl Lapel Pin Set](https://merch.crumbl.com/cdn/shop/files/DessertLapelPinSet_OverheadAerial.png?v=1743178219&width=4320)](https://merch.crumbl.com/products/crumbl-lapel-pin-set?variant=46284888441068 \"Go to Crumbl Lapel Pin Set\")\n\n### [Crumbl Lapel Pin Set](https://merch.crumbl.com/products/crumbl-lapel-pin-set?variant=46284888441068 \"Go to Crumbl Lapel Pin Set\")new\n\nRegular price$18.00\n\n[![Pastel Comfort Lounge Shorts](https://merch.crumbl.com/cdn/shop/files/IvoryPastelSweatSet_OverheadAerial_ShortsCompressed.jpg?v=1749758607&width=4320)![Pastel Comfort Lounge Shorts](https://merch.crumbl.com/cdn/shop/files/SpringMerch_IvorySweatSet_2Compressed.jpg?v=1749758607&width=4320)](https://merch.crumbl.com/products/spring-shorts?variant=46270657495276 \"Go to Pastel Comfort Lounge Shorts\")\n\n### [Pastel Comfort Lounge Shorts](https://merch.crumbl.com/products/spring-shorts?variant=46270657495276 \"Go to Pastel Comfort Lounge Shorts\")Ltd. Editionnew\n\nRegular price$35.00\n\n[![Pastel Comfort Crewneck](https://merch.crumbl.com/cdn/shop/files/NeonPurplePulloverCrewneck_OverheadAerial_Compressed.jpg?v=1749758660&width=4320)![Pastel Comfort Crewneck](https://merch.crumbl.com/cdn/shop/files/SpringMerch_NeonPurpleCrewneck_2Compressed.jpg?v=1749758660&width=4320)](https://merch.crumbl.com/products/pastel-comfort-crewneck?variant=46270629806316 \"Go to Pastel Comfort Crewneck\")\n\n### [Pastel Comfort Crewneck](https://merch.crumbl.com/products/pastel-comfort-crewneck?variant=46270629806316 \"Go to Pastel Comfort Crewneck\")Ltd. Editionnew\n\nRegular price$40.00\n\n[![Apron & Oven Mitt Set](https://merch.crumbl.com/cdn/shop/files/Apron_OvenMittSet_OverheadAerial.png?v=1743118240&width=4320)![Apron & Oven Mitt Set](https://merch.crumbl.com/cdn/shop/files/Apron_OverheadAerial.png?v=1743118240&width=4320)](https://merch.crumbl.com/products/apron-oven-mitt-set?variant=46239284855020 \"Go to Apron & Oven Mitt Set\")\n\n### [Apron & Oven Mitt Set](https://merch.crumbl.com/products/apron-oven-mitt-set?variant=46239284855020 \"Go to Apron & Oven Mitt Set\")new\n\nRegular price$45.00\n\n[Shop All](https://merch.crumbl.com/collections/all-merch)\n\n## All Merch\n\n[![Crumbl Dad Things Socks](https://merch.crumbl.com/cdn/shop/files/Father_sDaySocks_Green_OverheadAerialCompressed.jpg?v=1748032046&width=4320)![Crumbl Dad Things Socks](https://merch.crumbl.com/cdn/shop/files/Father_sDaySocks_Green_ToeDetailCompressed.jpg?v=1748032046&width=4320)](https://merch.crumbl.com/products/dad-crew-socks?variant=46472741486828 \"Go to Crumbl Dad Things Socks\")\n\n### [Crumbl Dad Things Socks](https://merch.crumbl.com/products/dad-crew-socks?variant=46472741486828 \"Go to Crumbl Dad Things Socks\")new\n\nRegular price$10.00\n\n[![Crumbl Trail Snapback](https://merch.crumbl.com/cdn/shop/files/Father_sDayHat_OverheadAerialCompressed.jpg?v=1747940175&width=4320)![Crumbl Trail Snapback](https://merch.crumbl.com/cdn/shop/files/FathersDayMerch_Hat_2_1x1Compressed_53a14057-6422-4764-90c3-22ca31b2a6ef.jpg?v=1747952056&width=1800)](https://merch.crumbl.com/products/crumbl-trail-snapback?variant=46472736145644 \"Go to Crumbl Trail Snapback\")\n\n### [Crumbl Trail Snapback](https://merch.crumbl.com/products/crumbl-trail-snapback?variant=46472736145644 \"Go to Crumbl Trail Snapback\")new\n\nRegular price$25.00\n\n[![Dadcrew Tee](https://merch.crumbl.com/cdn/shop/files/Father_sDayLongSleeve_OverheadAerialCompressed.jpg?v=1747941010)![Dadcrew Tee](https://merch.crumbl.com/cdn/shop/files/FathersDayMerch_Shirt_4_1x1Compressed.jpg?v=1747941010&width=2160)](https://merch.crumbl.com/products/crumbl-dad-crew-long-sleeve?variant=46472708686060 \"Go to Dadcrew Tee\")\n\n### [Dadcrew Tee](https://merch.crumbl.com/products/crumbl-dad-crew-long-sleeve?variant=46472708686060 \"Go to Dadcrew Tee\")Ltd. EditionnewSold out\n\nRegular price$30.00\n\n[![Mom Club Crewneck](https://merch.crumbl.com/cdn/shop/files/Dandy_Mother_sDaySweater_OverheadAerialCompressed.png?v=1745876779&width=3600)![Mom Club Crewneck](https://merch.crumbl.com/cdn/shop/files/Dandy_MothersDayMerch_Sweatshirt_3Compressed.jpg?v=1745876779&width=3600)](https://merch.crumbl.com/products/crumbl-mom-crewneck?variant=46358447063276 \"Go to Mom Club Crewneck\")\n\n### [Mom Club Crewneck](https://merch.crumbl.com/products/crumbl-mom-crewneck?variant=46358447063276 \"Go to Mom Club Crewneck\")Ltd. Editionnew\n\nRegular price$70.00\n\n[![Pink Comfort Slippers](https://merch.crumbl.com/cdn/shop/files/PinkCrumblSlippers_OverheadAerial.png?v=1744225945&width=4320)![Pink Comfort Slippers](https://merch.crumbl.com/cdn/shop/files/MothersDayMerch_Slippers_1Compressed.jpg?v=1745252674&width=4320)](https://merch.crumbl.com/products/slippers?variant=46352000221420 \"Go to Pink Comfort Slippers\")\n\n### [Pink Comfort Slippers](https://merch.crumbl.com/products/slippers?variant=46352000221420 \"Go to Pink Comfort Slippers\")new\n\nRegular price$15.00\n\n[![Crumbl Lapel Pin Set](https://merch.crumbl.com/cdn/shop/files/DessertLapelPinSet_OverheadAerial.png?v=1743178219&width=4320)](https://merch.crumbl.com/products/crumbl-lapel-pin-set?variant=46284888441068 \"Go to Crumbl Lapel Pin Set\")\n\n### [Crumbl Lapel Pin Set](https://merch.crumbl.com/products/crumbl-lapel-pin-set?variant=46284888441068 \"Go to Crumbl Lapel Pin Set\")new\n\nRegular price$18.00\n\n[![Pastel Comfort Lounge Shorts](https://merch.crumbl.com/cdn/shop/files/IvoryPastelSweatSet_OverheadAerial_ShortsCompressed.jpg?v=1749758607&width=4320)![Pastel Comfort Lounge Shorts](https://merch.crumbl.com/cdn/shop/files/SpringMerch_IvorySweatSet_2Compressed.jpg?v=1749758607&width=4320)](https://merch.crumbl.com/products/spring-shorts?variant=46270657495276 \"Go to Pastel Comfort Lounge Shorts\")\n\n### [Pastel Comfort Lounge Shorts](https://merch.crumbl.com/products/spring-shorts?variant=46270657495276 \"Go to Pastel Comfort Lounge Shorts\")Ltd. Editionnew\n\nRegular price$35.00\n\n[![Pastel Comfort Crewneck](https://merch.crumbl.com/cdn/shop/files/NeonPurplePulloverCrewneck_OverheadAerial_Compressed.jpg?v=1749758660&width=4320)![Pastel Comfort Crewneck](https://merch.crumbl.com/cdn/shop/files/SpringMerch_NeonPurpleCrewneck_2Compressed.jpg?v=1749758660&width=4320)](https://merch.crumbl.com/products/pastel-comfort-crewneck?variant=46270629806316 \"Go to Pastel Comfort Crewneck\")\n\n### [Pastel Comfort Crewneck](https://merch.crumbl.com/products/pastel-comfort-crewneck?variant=46270629806316 \"Go to Pastel Comfort Crewneck\")Ltd. Editionnew\n\nRegular price$40.00\n\n[![Apron & Oven Mitt Set](https://merch.crumbl.com/cdn/shop/files/Apron_OvenMittSet_OverheadAerial.png?v=1743118240&width=4320)![Apron & Oven Mitt Set](https://merch.crumbl.com/cdn/shop/files/Apron_OverheadAerial.png?v=1743118240&width=4320)](https://merch.crumbl.com/products/apron-oven-mitt-set?variant=46239284855020 \"Go to Apron & Oven Mitt Set\")\n\n### [Apron & Oven Mitt Set](https://merch.crumbl.com/products/apron-oven-mitt-set?variant=46239284855020 \"Go to Apron & Oven Mitt Set\")new\n\nRegular price$45.00\n\n[![Pink Insulated Water Bottle](https://merch.crumbl.com/cdn/shop/files/NILLABEAN_20ozPinkWideMouthTumbler_OverheadAerial.jpg?v=1741717585&width=4320)![Pink Insulated Water Bottle](https://merch.crumbl.com/cdn/shop/files/SpringMerch_Waterbottle_1.png?v=1743102348&width=4320)](https://merch.crumbl.com/products/pink-double-wall-bottle-20oz?variant=46239276466412 \"Go to Pink Insulated Water Bottle\")\n\n### [Pink Insulated Water Bottle](https://merch.crumbl.com/products/pink-double-wall-bottle-20oz?variant=46239276466412 \"Go to Pink Insulated Water Bottle\")new\n\nRegular price$25.00\n\n[![Crumbl Everyday Backpack](https://merch.crumbl.com/cdn/shop/files/CreamEverydayBackpack_OverheadAerial_Front.png?v=1743091040&width=4320)![Crumbl Everyday Backpack](https://merch.crumbl.com/cdn/shop/files/SpringMerch_Backpack_1_Compressed.jpg?v=1743096086&width=4320)](https://merch.crumbl.com/products/crumbl-everyday-backpack?variant=46239273418988 \"Go to Crumbl Everyday Backpack\")\n\n### [Crumbl Everyday Backpack](https://merch.crumbl.com/products/crumbl-everyday-backpack?variant=46239273418988 \"Go to Crumbl Everyday Backpack\")new\n\nRegular price$40.00\n\n[![Insulated Crumblr](https://merch.crumbl.com/cdn/shop/files/40ozPinkCrumblHydrowaveTumbler_OverheadAerial.png?v=1743189298&width=4320)](https://merch.crumbl.com/products/insulated-crumblr-2-0?variant=46239270732012 \"Go to Insulated Crumblr\")\n\n### [Insulated Crumblr](https://merch.crumbl.com/products/insulated-crumblr-2-0?variant=46239270732012 \"Go to Insulated Crumblr\")new\n\nRegular price$35.00\n\n[![Crumbl Dessert Keychains](https://merch.crumbl.com/cdn/shop/files/DessertKeychainsGroupShot_OverheadAerial_WithoutCrumblBox.png?v=1744926372&width=4320)![Crumbl Dessert Keychains](https://merch.crumbl.com/cdn/shop/files/PinkSugarCookieKeychain_OverheadAerial_1.png?v=1744926386&width=4320)](https://merch.crumbl.com/products/crumbl-dessert-keychains?variant=46239233245420 \"Go to Crumbl Dessert Keychains\")\n\n### [Crumbl Dessert Keychains](https://merch.crumbl.com/products/crumbl-dessert-keychains?variant=46239233245420 \"Go to Crumbl Dessert Keychains\")\n\nRegular price$5.00\n\n[![Crumbl® Minky Couture® Blanket](https://merch.crumbl.com/cdn/shop/files/CrumblPinkMinkyBlanketAdult_1.png?v=1743106365&width=4320)![Crumbl® Minky Couture® Blanket](https://merch.crumbl.com/cdn/shop/files/CrumblPinkMinkyBlanketAdult_2.png?v=1743106364&width=4320)](https://merch.crumbl.com/products/crumbl-minky-couture-blanket?variant=46138914537708 \"Go to Crumbl® Minky Couture® Blanket\")\n\n### [Crumbl® Minky Couture® Blanket](https://merch.crumbl.com/products/crumbl-minky-couture-blanket?variant=46138914537708 \"Go to Crumbl® Minky Couture® Blanket\")\n\nRegular price$150.00\n\n[![Crumbl Pink Box Keychain](https://merch.crumbl.com/cdn/shop/files/CrumblPinkBoxKeychain_OverheadAerial_1.png?v=1744926305&width=4320)](https://merch.crumbl.com/products/crumbl-pink-box-key-chain?variant=45969445126380 \"Go to Crumbl Pink Box Keychain\")\n\n### [Crumbl Pink Box Keychain](https://merch.crumbl.com/products/crumbl-pink-box-key-chain?variant=45969445126380 \"Go to Crumbl Pink Box Keychain\")\n\nRegular price$5.00\n\nLoad more\n\n![](https://merch.crumbl.com/cdn/shop/files/motto-desktop.svg?v=1727990909&width=1440)\n\n![](https://merch.crumbl.com/cdn/shop/files/motto-mobile.svg?v=1727991003&width=720)\n\nYour cart0\n\n## Nothin' Here\n\nYour cart is currently empty [Start Shopping](https://merch.crumbl.com/collections/all-merch)\n\n- Choosing a selection results in a full page refresh.\n\n[iframe](https://merch.crumbl.com/wpm@0a4b528bw2defb8a1pb18962c6m9f7ddb6c/custom/web-pixel-shopify-custom-pixel@0420/sandbox/modern/collections/home)",
        "description": "Official Crumbl branded merchandise.",
        "title": "Home"
    },
    {
        "url": "https://crumblcookies.com",
        "markdown": "Menu\n\n[Crumbl Cookies logo](https://crumblcookies.com/)\n\nOrder Now\n\n![Real Ingredients, Real Flavor.](https://crumblcookies.com/quality=80/https://crumbl.video/6a1efefd-d787-4a08-b4aa-b61d03744c0b_Real-Ingredients_Carousel_Backgrounds_Tablet.png)\n\nReal Ingredients, Real Flavor.\n\nReal eggs, butter, sugar, flour, and house-made jams—because flavor starts with the basics.\n\n[Order Now](https://crumblcookies.com/order)\n\n[Order Now](https://crumblcookies.com/order)\n\n![Real Ingredients, Real Flavor.](https://crumblcookies.com/quality=80/https://crumbl.video/6a1efefd-d787-4a08-b4aa-b61d03744c0b_Real-Ingredients_Carousel_Backgrounds_Tablet.png)\n\nReal Ingredients, Real Flavor.\n\nReal eggs, butter, sugar, flour, and house-made jams—because flavor starts with the basics.\n\n[Order Now](https://crumblcookies.com/order)\n\n[Order Now](https://crumblcookies.com/order)\n\n![Real Ingredients, Real Flavor.](https://crumblcookies.com/quality=80/https://crumbl.video/6a1efefd-d787-4a08-b4aa-b61d03744c0b_Real-Ingredients_Carousel_Backgrounds_Tablet.png)\n\nReal Ingredients, Real Flavor.\n\nReal eggs, butter, sugar, flour, and house-made jams—because flavor starts with the basics.\n\n[Order Now](https://crumblcookies.com/order)\n\nWeek of Jun 16 - 21\n\n# National flavors\n\n![Semi-Sweet Chocolate Chunk Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/c0fefd97-a4c9-4559-a40b-2642cce87e4e_SemiSweetChocolateChunk_FlyingAerial_TECH.png)![Semi-Sweet Chocolate Chunk Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/c0fefd97-a4c9-4559-a40b-2642cce87e4e_SemiSweetChocolateChunk_FlyingAerial_TECH.png)\n\nSemi-Sweet Chocolate Chunk Cookie\n\nChocolate chip, but make it chunky—a delicious cookie filled with irresistible semi-sweet chocolate chunks and a sprinkle of flaky sea salt.\n\n[Learn More](https://crumblcookies.com/profiles/d9b3b3b0-da5c-11e9-96bb-0360932294c2:Cookie) [Learn More](https://crumblcookies.com/profiles/d9b3b3b0-da5c-11e9-96bb-0360932294c2:Cookie) [Order Now](https://crumblcookies.com/order)\n\n![Peanut Butter Cup Skillet Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/612f2b22-3ef9-4e38-ba04-0d55c1734d11_PeanutButterCupSkilletCookie_FlyingAerial_TECH.png)![Peanut Butter Cup Skillet Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/612f2b22-3ef9-4e38-ba04-0d55c1734d11_PeanutButterCupSkilletCookie_FlyingAerial_TECH.png)\n\nPeanut Butter Cup Skillet Cookie\n\nft. REESE'S\n\nA peanut butter cookie topped with Peanut Butter Cup mousse, drizzled with melted milk chocolate, and topped with more Peanut Butter Cup pieces.\n\nREESE'S trademark and trade dress are used under license.\n\n[Learn More](https://crumblcookies.com/profiles/231037b0-247e-11f0-a47e-fbed13200f5b:Cookies) [Learn More](https://crumblcookies.com/profiles/231037b0-247e-11f0-a47e-fbed13200f5b:Cookies) [Order Now](https://crumblcookies.com/order)\n\n![Berry Trifle Cake Cup](https://crumblcookies.com/quality=80/https://crumbl.video/6bd80a0f-12cb-492b-af3c-88729b87f649_BerryTrifleCakeCupDessert_FlyingAerial_TECH.png)![Berry Trifle Cake Cup](https://crumblcookies.com/quality=80/https://crumbl.video/6bd80a0f-12cb-492b-af3c-88729b87f649_BerryTrifleCakeCupDessert_FlyingAerial_TECH.png)\n\nBerry Trifle Cake Cup\n\nLayers of light vanilla cake, vanilla pudding, and house-made mixed berry jam served in a cup. Not available in mini sizes.\n\n[Learn More](https://crumblcookies.com/profiles/1ee47550-f2c2-11ee-9aa3-bd908a3c12d6:Cookies) [Learn More](https://crumblcookies.com/profiles/1ee47550-f2c2-11ee-9aa3-bd908a3c12d6:Cookies) [Order Now](https://crumblcookies.com/order)\n\n![Wedding Cake Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/68fb6e40-cbce-42ff-b3ee-80b599c0104e_028773bf-8e5e-4951-9e3a-68c7d8a5ab46_WeddingCake_FlyingAerial_TECHcopy.png)![Wedding Cake Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/68fb6e40-cbce-42ff-b3ee-80b599c0104e_028773bf-8e5e-4951-9e3a-68c7d8a5ab46_WeddingCake_FlyingAerial_TECHcopy.png)\n\nWedding Cake Cookie\n\nA warm vanilla bean sugar cookie topped with an elegant swirl of vanilla and raspberry cream cheese frosting and a light crunch of white chocolate pearls.\n\n[Learn More](https://crumblcookies.com/profiles/fc218880-9aa9-11ed-94b9-1bc2ba8cde95:Cookies) [Learn More](https://crumblcookies.com/profiles/fc218880-9aa9-11ed-94b9-1bc2ba8cde95:Cookies) [Order Now](https://crumblcookies.com/order)\n\n![Chocolate Toffee Cake Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/77220bfa-be93-4f17-be90-6ffe17692cbf_ChocolateToffeeCakeCookieftHeath_FlyingAerial_TECH.png)![Chocolate Toffee Cake Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/77220bfa-be93-4f17-be90-6ffe17692cbf_ChocolateToffeeCakeCookieftHeath_FlyingAerial_TECH.png)\n\nChocolate Toffee Cake Cookie\n\nft. HEATH\n\nA gooey chocolate cake-inspired cookie layered with fluffy whipped cream, milky caramel glaze, and crunchy HEATH pieces.\n\nHEATH trademark and trade dress are used under license.\n\n[Learn More](https://crumblcookies.com/profiles/cc859cb0-8b38-11eb-b0be-91d63f6228e5:Cookie) [Learn More](https://crumblcookies.com/profiles/cc859cb0-8b38-11eb-b0be-91d63f6228e5:Cookie) [Order Now](https://crumblcookies.com/order)\n\n![Cinnamon Roll Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/75a24315-652a-483a-aa55-c32ca3336692_CinnamonRoll_FlyingAerial_TECH.png)![Cinnamon Roll Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/75a24315-652a-483a-aa55-c32ca3336692_CinnamonRoll_FlyingAerial_TECH.png)\n\nCinnamon Roll Cookie\n\nA vanilla sugar cookie topped with cinnamon streusel and swirled with vanilla cream cheese frosting.\n\n[Learn More](https://crumblcookies.com/profiles/3e4ed270-da51-11e9-a868-cd4091f7bd01:Cookie) [Learn More](https://crumblcookies.com/profiles/3e4ed270-da51-11e9-a868-cd4091f7bd01:Cookie) [Order Now](https://crumblcookies.com/order)\n\n![Triple Chocolate Chip Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/26f37ba0-365a-465a-b61c-69354bd2dc1e_TripleChocolateChip_FlyingAerial_TECH.png)![Triple Chocolate Chip Cookie](https://crumblcookies.com/quality=80/https://crumbl.video/26f37ba0-365a-465a-b61c-69354bd2dc1e_TripleChocolateChip_FlyingAerial_TECH.png)\n\nTriple Chocolate Chip Cookie\n\nA chocolate cookie packed with semi-sweet chunks, creamy white chips, and milk chocolate chips.\n\n[Learn More](https://crumblcookies.com/profiles/4bf6c930-ee24-11eb-9dee-7d292570e9db:Cookie) [Learn More](https://crumblcookies.com/profiles/4bf6c930-ee24-11eb-9dee-7d292570e9db:Cookie) [Order Now](https://crumblcookies.com/order)",
        "description": "The best desserts in the world. Fresh and gourmet desserts for takeout, delivery, or pick-up. Made fresh daily. Unique and trendy flavors weekly.",
        "title": "Crumbl - Freshly Baked Cookies & Desserts"
    }
]
        generated_data = self.generate_data_for_ingestion(cleaned_data, ingestion)
        # print("Generated Data", generated_data)
        data = self.embed_inputs(generated_data)
        return data
    
    def embed_inputs(self, array_of_data: [WebsiteScrapeResult]):
        data_for_pinecone = []
        for data in array_of_data:
            print("Data", data)
            url = getattr(data, "source_url", None) or data.get("source_url")
            title = getattr(data, "title", None) or data.get("title")
            section = getattr(data, "section", None) or data.get("section")
            content_type = getattr(data, "content_type", None) or data.get("content_type")
            summarized_content = getattr(data, "summarized_content", None) or data.get("summarized_content")
            _data = {
                "id": url,
                "values": self.embed_text(f"{title} {section} {content_type} {summarized_content}"),
                "metadata": data
            }
            # print("Data Value", _data)
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

    def scrape_and_ingest_data(self, ingestion: Ingestion):
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

    def search_in_pinecone(self, search_dto: SearchDTO) -> dict:
        try:
            print("I'm here at embedding")
            embedding = self.embed_text(search_dto.query)
            results = None
            if embedding:
                results = index.query(
                    namespace=settings.pinecone_index_name,
                    vector=embedding,
                    top_k=search_dto.top_k,
                    include_metadata=True,
                    filter={
                        "company_website": {"$eq": search_dto.company_website}
                    }
                )
            else:
               results = index.search(
                    namespace=settings.pinecone_index_name,
                    query={
                        "inputs":{
                                "text": search_dto.query,
                        },
                        "top_k": search_dto.top_k,
                        "filter": {
                                "company_website": search_dto.company_website
                        },
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