from fastapi import APIRouter, Request
from typing import Optional

from ..core.config import settings
from ..core.logger import logger
from ..scrapers.manager import ScraperManager
from ..core.stream_handler import handle_stream  # <-- IMPORT THE NEW HANDLER

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
        "types": ["movie", "series"],
        "catalogs": [
            {
                "type": "movie",
                "id": "goonio-sxyprn",
                "name": "SXYPRN",
                "extra": [{"name": "search", "isRequired": True}],
            }
        ],
        "behaviorHints": {
            "adult": True,
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
    streams = await scraper_manager.scrape_streams(id)
    
    return {"streams": streams}

# --- Playback Proxy Endpoint (NEW) ---
@api_router.get("/playback/{scraper_prefix}/{encoded_url}.m3u8")
async def get_playback(request: Request, scraper_prefix: str, encoded_url: str):
    """
    This endpoint is called by Stremio to play the video.
    It uses our stream_handler to proxy the video content.
    """
    return await handle_stream(request, scraper_prefix, encoded_url)
