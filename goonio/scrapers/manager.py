import asyncio
from typing import List, Dict

from ..core.logger import logger

# We import the specific scraper functions we will create next.
# This structure makes it easy to add more scrapers in the future.
from . import sxyprn

class ScraperManager:
    """
    Manages and delegates scraping tasks to the appropriate scraper module.
    """
    def __init__(self):
        # A dictionary mapping catalog IDs to their respective scraper modules.
        # This makes the manager easily extensible.
        self.scrapers = {
            "goonio-sxyprn": sxyprn,
        }
        logger.log("SCRAPER", f"ScraperManager initialized with providers: {list(self.scrapers.keys())}")

    async def scrape_catalog(self, catalog_id: str, query: str) -> List[Dict]:
        """
        Scrapes a catalog for a given search query.

        Args:
            catalog_id: The ID of the catalog to scrape (e.g., 'goonio-sxyprn').
            query: The user's search term.

        Returns:
            A list of Stremio meta objects.
        """
        scraper = self.scrapers.get(catalog_id)
        if not scraper:
            logger.warning(f"No scraper found for catalog ID: {catalog_id}")
            return []
        
        # Calls the 'search' function within the appropriate scraper module.
        return await scraper.search(query)

    async def scrape_streams(self, item_id: str) -> List[Dict]:
        """
        Scrapes stream links for a given item ID.

        Args:
            item_id: The unique ID of the item (e.g., 'sxyprn_post/687269d1165a7').

        Returns:
            A list of Stremio stream objects.
        """
        # The item_id is prefixed with the scraper's name to know where to route the request.
        # e.g., "sxyprn_post/687269d1165a7"
        scraper_prefix, real_id = item_id.split("_", 1)
        
        # The catalog ID is derived from the prefix.
        catalog_id = f"goonio-{scraper_prefix}"
        
        scraper = self.scrapers.get(catalog_id)
        if not scraper:
            logger.warning(f"No scraper found for item ID prefix: {scraper_prefix}")
            return []

        # Calls the 'get_streams' function within the appropriate scraper module.
        return await scraper.get_streams(real_id)
