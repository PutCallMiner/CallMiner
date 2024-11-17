from azure.core.credentials import AzureSasCredential
from azure.storage.blob.aio import BlobServiceClient

from webapp.configs.globals import AZURE_BLOB_STORAGE_URL, AZURE_SAS_TOKEN


async def get_recording_file(client: BlobServiceClient, recording_name: str):
    container_client = client.get_container_client("audio-records")
    blob_client = container_client.get_blob_client(recording_name)
    blob = await blob_client.download_blob()
    return blob.readall()


class AzureBlobStorageContainerAsync:
    def __init__(
        self,
        container_name: str = "audio-records",
        account_url=AZURE_BLOB_STORAGE_URL,
        sas_token=AZURE_SAS_TOKEN,
    ):
        self.container_name = container_name
        self.account_url = account_url
        self.sas_token = AzureSasCredential(sas_token)

    async def __aenter__(self):
        self.blob_service_client = BlobServiceClient(
            account_url=self.account_url, credential=self.sas_token
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.blob_service_client.close()

    async def list_blobs(self):
        blob_list = []
        async for blob in self.container_client.list_blobs():
            blob_list.append(blob.name)
        return blob_list

    async def download_blob(self, blob_name: str) -> bytes:
        blob_client = self.container_client.get_blob_client(blob_name)
        stream = await blob_client.download_blob()
        data = await stream.readall()
        return data

    async def upload_blob(self, blob_name, data, **kwargs):
        blob_client = self.container_client.get_blob_client(blob_name)
        await blob_client.upload_blob(data, **kwargs)

    async def delete_blob(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        await blob_client.delete_blob()

    async def get_blob_properties(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        properties = await blob_client.get_blob_properties()
        return properties
