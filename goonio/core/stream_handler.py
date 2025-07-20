from fastapi import Request
from base64 import b64decode
from typing import Dict

from .logger import logger
import mediaflow_proxy.handlers as proxy_handlers
import mediaflow_proxy.utils.http_utils as proxy_utils

async def handle_stream(request: Request, scraper_prefix: str, encoded_url: str):
    """
    Handles the proxied streaming request using mediaflow-proxy.
    """
    try:
        # Decode the actual video URL from the base64 encoded path
        video_url = b64decode(encoded_url).decode()
        logger.log("STREAM", f"Received playback request for: {video_url}")

        # Define the headers we need to inject for this specific scraper
        custom_headers: Dict[str, str] = {}
        if scraper_prefix == "sxyprn":
            custom_headers["Referer"] = "https://sxyprn.net/"
        
        # Get the headers from the incoming request (from Stremio)
        proxy_request_headers = proxy_utils.get_proxy_headers(request)
        
        # Use mediaflow-proxy to handle the streaming
        # It will make a new request to `video_url`, adding our custom headers,
        # and stream the response back to Stremio.
        return await proxy_handlers.handle_stream_request(
            method=request.method,
            video_url=video_url,
            proxy_headers=proxy_request_headers,
            custom_headers=custom_headers,
        )

    except Exception as e:
        logger.error(f"Error handling stream for {encoded_url}: {e}")
        # In a real app, you might return a proper error response here
        return {"status": "error", "message": str(e)}
