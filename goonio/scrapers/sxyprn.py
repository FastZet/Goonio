import aiohttp
import re
from base64 import b64encode
from bs4 import BeautifulSoup
from typing import List, Dict

from ..core.logger import logger

# The base URL for all requests to sxyprn.net
BASE_URL = "https://sxyprn.net"

async def search(query: str) -> List[Dict]:
    """
    Searches sxyprn.net for a given query and returns Stremio meta objects.
    """
    # --- THIS IS THE CORRECTED LINE ---
    search_url = f"{BASE_URL}/{query.replace(' ', '-')}"
    
    metas = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response.raise_for_status() # Raise an exception for bad status codes
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Find all video containers on the search results page
                video_items = soup.find_all('div', class_='thumb-pad')

                for item in video_items:
                    a_tag = item.find('a', href=True)
                    img_tag = item.find('img', src=True)
                    title_tag = item.find('p', class_='thumb-title')

                    if not a_tag or not img_tag or not title_tag:
                        continue
                    
                    # The path now comes from the href, which is correct
                    path = a_tag['href'].replace(BASE_URL, '').lstrip('/')
                    item_id = f"sxyprn_{path}" # Prefix for routing in the manager
                    
                    metas.append({
                        "id": item_id,
                        "type": "movie", # We treat all scenes as "movies" for Stremio
                        "name": title_tag.text.strip(),
                        "poster": img_tag['src'],
                        "posterShape": "landscape"
                    })
        
        logger.log("SCRAPER", f"SXYPRN: Found {len(metas)} results for query '{query}'")
        return metas

    except Exception as e:
        logger.error(f"SXYPRN: Error during search for '{query}': {e}")
        return []


async def get_streams(item_id: str) -> List[Dict]:
    """
    Fetches stream URLs for a given sxyprn item ID.
    """
    video_url = f"{BASE_URL}/{item_id}"
    streams = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                response.raise_for_status()
                html = await response.text()
                
                match = re.search(r'source src="([^"]+\.m3u8)"', html)
                
                if match:
                    m3u8_url = match.group(1)
                    
                    encoded_url = b64encode(m3u8_url.encode()).decode()
                    
                    # We are using a relative URL here, which is fine for Stremio.
                    proxy_url = f"/playback/sxyprn/{encoded_url}.m3u8"
                    
                    streams.append({
                        "name": "SXYPRN",
                        "title": "Auto Quality",
                        "url": proxy_url,
                    })
                    logger.log("SCRAPER", f"SXYPRN: Found stream for {item_id}")
                else:
                    logger.warning(f"SXYPRN: No m3u8 URL found on page: {video_url}")

        return streams

    except Exception as e:
        logger.error(f"SXYPRN: Error getting streams for {item_id}: {e}")
        return []
