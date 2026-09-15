import httpx
import asyncio
from typing import Any, Dict, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class BaseHTTPClient:
    def __init__(self, base_url: str = "", timeout: float = 10.0, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    async def _request(self, method: str, url: str, **kwargs) -> Any:
        retries = 0
        while retries <= self.max_retries:
            try:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                # Retry on 5xx server errors or 429 rate limit
                if status in {429, 500, 502, 503, 504} and retries < self.max_retries:
                    wait_time = 2 ** retries
                    logger.warning(f"HTTPStatusError {status} from {url}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    continue
                # If not retrying or out of retries, raise HTTPException
                logger.error(f"HTTP error {status} calling {url}: {e.response.text}")
                raise HTTPException(status_code=502, detail=f"External API Error: {status} from {url}")
            except httpx.RequestError as e:
                # DNS, Timeout, or Connection issues
                if retries < self.max_retries:
                    wait_time = 2 ** retries
                    logger.warning(f"RequestError {e.__class__.__name__} calling {url}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    continue
                logger.error(f"Connection error calling {url}: {str(e)}")
                raise HTTPException(status_code=503, detail=f"External Service Unavailable: {str(e)}")

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        return await self._request("GET", url, params=params, headers=headers)
