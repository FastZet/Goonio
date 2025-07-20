from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse  # <-- NEW IMPORT
from typing import Optional

from ..core.config import settings
from ..core.logger import logger
from ..scrapers.manager import ScraperManager
from ..core.stream_handler import handle_stream

api_router = APIRouter()

# --- Landing Page Endpoint (NEW) ---
@api_router.get("/", response_class=HTMLResponse, tags=["General"])
async def get_root(request: Request):
    """
    Provides a simple landing page for the addon.
    """
    logger.log("API", "Root endpoint accessed.")
    # Get the full base URL from the request
    base_url = str(request.base_url)
    manifest_url = f"{base_url}manifest.json"
    
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{settings.ADDON_NAME}</title>
            <style>
                body {{ background-color: #1a1d20; color: #c9d1d9; font-family: sans-serif; text-align: center; padding: 40px; }}
                h1 {{ color: #ff4500; }}
                p {{ font-size: 1.1em; }}
                code {{ background-color: #2c313a; padding: 5px 10px; border-radius: 5px; font-family: monospace; }}
                a {{ color: #ff6a00; }}
            </style>
        </head>
        <body>
            <h1>🌶️ {settings.ADDON_NAME}</h1>
            <p>Your addon is running correctly.</p>
            <p>To install this addon in Stremio, use the following URL:</p>
            <p><code>{manifest_url}</code></p>
            <p><a href="stremio://{base_url.replace('https://','').replace('http://','')}manifest.json">Click here to install directly</a></p>
        </body>
    </html>
    """

# --- Manifest Endpoint ---
@api_router.get("/manifest.json")
async def get_manifest():
    """
    Provides the addon's manifest to Stremio.
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

# --- Playback Proxy Endpoint ---
@api_router.get("/playback/{scraper_prefix}/{encoded_url}.m3u8")
async def get_playback(request: Request, scraper_prefix: str, encoded_url: str):
    """
    This endpoint is called by Stremio to play the video.
    It uses our stream_handler to proxy the video content.
    """
    return await handle_stream(request, scraper_prefix, encoded_url)
