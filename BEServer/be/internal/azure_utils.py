import os
import logging

from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from urllib.parse import urlparse, ParseResult
from typing import Optional, List


logging.getLogger().setLevel(logging.INFO)


class BlobUrlParser:
    @staticmethod
    def parse(url: str) -> List[str]:
        """
        Parses the blob URL and returns a list containing the container and blob names.

        :param url: Blob URL to parse
        :return: List of container and blob names
        """
        parsed_url: ParseResult = urlparse(url)
        container_and_blob_names: List[str] = parsed_url.path.lstrip('/').split('/', 1)

        if len(container_and_blob_names) != 2:
            raise ValueError("Invalid URL format. Cannot determine container and blob names.")

        return container_and_blob_names


class AzureBlobDownloader:
    def __init__(self, blob_service_client: BlobServiceClient):
        """
        Initializes the AzureBlobDownloader with a blob service client.

        :param blob_service_client: The BlobServiceClient instance.
        """
        self.blob_service_client = blob_service_client

    def download_blob_from_url(self, url: str) -> Optional[bytes]:
        """
        Downloads a blob from Azure Blob Storage using a URL and returns the content as bytes.

        :param url: The URL of the blob to download.
        :return: The content of the blob as bytes, or None if an error occurs.
        """
        try:
            container_name, blob_name = BlobUrlParser.parse(url)

            container_client: ContainerClient = self.blob_service_client.get_container_client(container_name)
            blob_client: BlobClient = container_client.get_blob_client(blob_name)

            blob_content: bytes = blob_client.download_blob().readall()
            logging.info(f"Blob {blob_name} downloaded successfully.")
            return blob_content

        except Exception as e:
            logging.error(f'Exception occurred when downloading blob from URL: {url}. Error: {e}:')
            return None