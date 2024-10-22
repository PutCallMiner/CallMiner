import chromadb
from models.record import Recording

from webapp.configs.globals import CHROMADB_HOST, CHROMADB_PORT


async def run_conformity_check_task(recording: Recording):
    await delete_embeddings(recording_id=recording.id)
    await generate_agent_entries_embeddings(recording)
    intents = [
        {
            "intent": "Klient powinien zostać zachęcony przez agenta do polecenia biura innym",
            "examples": [
                "Czy może Pan polecić nasze biuro znajomym?",
                "W najnowszej promocji możecie Państwo zarobić pieniądze za polecenie nas innym",
                "Czy chce Pani wziąć udział w naszym programie poleceń?",
            ],
        },
        {
            "intent": "Agent powinen się przedstawić z imienia i nazwiska a także podać nazwę firmy",
            "examples": [
                "Dzień dobry, nazywam się Karol Jaworski dzwonię z firmy Eurotax",
                "Witam z tej strony Hanna Szewczyk firma Callminer w czym mogę pomóc",
            ],
        },
        {
            "intent": "Agent powinien potwierdzić tożsamość klienta",
            "examples": [
                "Czy rozmawiam z Panią Joanną?",
                "Dzień dobry czy mam przyjemność rozmawiać z Panem Grzegorzem Gibą?",
            ],
        },
    ]
    text = await retrieve_agent_embeddings_text(recording, intents)
    print(text)


async def generate_agent_entries_embeddings(recording: Recording):
    transcript = recording.transcript
    recording_id = recording.id
    agent_id = get_agent_speaker_id(recording.speaker_mapping)

    ids = []
    documents = []
    metadatas = []
    for i, entry in enumerate(transcript.entries):
        if entry.speaker == agent_id:
            ids.append(f"{recording_id}:{i}")
            documents.append(entry.text)
            metadatas.append({"recording_id": recording_id, "entry_id": i})

    await generate_embeddings(ids=ids, documents=documents, metadatas=metadatas)


async def generate_embeddings(
    ids: list[str], documents: list[str], metadatas: list[dict]
):
    client = await chromadb.AsyncHttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection = await client.get_or_create_collection("transcript_entries")
    await collection.add(ids, documents=documents, metadatas=metadatas)


async def delete_embeddings(recording_id: str):
    client = await chromadb.AsyncHttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection = await client.get_or_create_collection("transcript_entries")
    await collection.delete(where={"recording_id": recording_id})


def get_agent_speaker_id(speaker_mapping: dict[str, str]) -> int:
    for key, value in speaker_mapping.items():
        if value == "agent":
            return int(key.strip()[-1])


async def retrieve_agent_embeddings_text(recording: Recording, intents: list[dict]):
    client = await chromadb.AsyncHttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection = await client.get_or_create_collection("transcript_entries")

    result = {}

    for intent in intents:
        intent_examples = intent["examples"]

        for example in intent_examples:
            # Query ChromaDB using the intent example text directly
            query_result = await collection.query(
                query_texts=[example],  # Use the example text directly
                n_results=3,  # Get the 3 closest entries
            )

            # Process query results
            for doc, metadata in zip(
                query_result["documents"][0], query_result["metadatas"][0]
            ):
                entry_id = metadata["entry_id"]
                if entry_id not in result:
                    result[entry_id] = (
                        doc  # Store the document text using its unique entry_id
                    )

    return result
