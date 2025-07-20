from fastapi import APIRouter
from typing import Optional

from ..core.config import settings
from ..core.logger import logger

# We will create the ScraperManager in the next steps.
# For now, we are defining how the router will use it.
from ..scrapers.manager import ScraperManager

api_router = APIRouter()

# --- Manifest Endpoint ---
@api_router.get("/manifest.json")
async def get_manifest():
    """
    Provides the addon's manifest to Stremio.
    This describes the addon's capabilities, resources, and catalogs.
    """
    logger.log("API", "Manifest requested.")
    return {
        "id": settings.ADDON_ID,
        "version": settings.ADDON_VERSION,
        "name": settings.ADDON_NAME,
        "description": settings.ADDON_DESCRIPTION,
        "logo": settings.ADDON_LOGO,
        "background": settings.ADDON_BACKGROUND,
        "resources": ["catalog", "stream"],
        "types": ["movie", "series"], # Using movie/series types for broad compatibility
        "catalogs": [
            {
                "type": "movie", # Use 'movie' type for scenes
                "id": "goonio-sxyprn",
                "name": "SXYPRN",
                "extra": [{"name": "search", "isRequired": True}],
            }
        ],
        "behaviorHints": {
            "adult": True, # Mark the addon as containing adult content
            "configurable": False,
            "configurationRequired": False,
        }
    }

# --- Catalog Endpoint ---
@api_router.get("/catalog/{type}/{id}/{extra}.json")
async def get_catalog(type: str, id: str, extra: Optional[str] = None):
    """
    Provides the list of content (metas) to Stremio, primarily for search.
    """
    extra_props = dict(part.split("=") for part in extra.split("&"))
    query = extra_props.get("search", "")

    logger.log("API", f"Catalog requested for '{id}' with search query: '{query}'")

    if not query:
        return {"metas": []}

    scraper_manager = ScraperManager()
    
    # We will implement the scraping logic in the next steps
    metas = await scraper_manager.scrape_catalog(id, query)

    return {"metas": metas}

# --- Stream Endpoint ---
@api_router.get("/stream/{type}/{id}.json")
async def get_streams(type: str, id: str):
    """
    Provides the streaming links for a selected item.
    """
    logger.log("API", f"Streams requested for ID: {id}")

    scraper_manager = ScraperManager()

    # We will implement the stream scraping logic in the next steps
    streams = await scraper_manager.scrape_streams(id)
    
    return {"streams": streams}
