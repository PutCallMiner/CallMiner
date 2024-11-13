import httpx
from fastapi import status

from webapp.errors import BlobDownloadError


async def download_azure_blob(blob_url: str, sas_token: str) -> bytes:
    """Downloads a blob from Azure using a SAS token"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{blob_url}?{sas_token}")
    if resp.status_code != status.HTTP_200_OK:
        raise BlobDownloadError(blob_url)
    downloaded_bytes = resp.content
    return downloaded_bytes


async def stream_azure_blob(blob_url: str, sas_token: str):
    """Streams a blob from Azure using a SAS token"""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", f"{blob_url}?{sas_token}") as resp:
            if resp.status_code != status.HTTP_200_OK:
                raise BlobDownloadError(blob_url)
            async for chunk in resp.aiter_bytes():
                yield chunk
