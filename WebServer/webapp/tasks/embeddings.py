import chromadb

from webapp.configs.globals import CHROMADB_HOST, CHROMADB_PORT
from webapp.models.record import PyObjectId
from webapp.models.transcript import Transcript


async def run_generate_embeddings_task(
    transcript: Transcript, recording_id: PyObjectId
):
    ids = []
    documents = []
    metadatas = []
    for i, entry in enumerate(transcript.entries):
        ids.append(f"{recording_id}:{i}")
        documents.append(entry.text)
        metadatas.append({"recording_id": recording_id, "speaker": entry.speaker})

    client = await chromadb.AsyncHttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection = await client.get_or_create_collection("transcript_entries")
    await collection.add(ids, documents=documents, metadatas=metadatas)
