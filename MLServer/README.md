# MLServer
- [Prerequisites](#prerequisites)
- [Start the Server](#start-the-server)
- [API Documentation](#api-documentation)
  - [Named Entity Recognition (NER)](#named-entity-recognition-ner)
  - [GPT Summarizer](#gpt-summarizer)
_________________________________________________________
### Prerequisites
_________________________________________________________
- Python >=3.9
- Docker and Docker Compose
- Bash shell
_________________________________________________________
### Start the server
_________________________________________________________
Follow these steps to start the ML Server:
1. **Create `.env` file with Environment Variables**:
- You can find required Environment Variables in `.env_example` 

2. **Start Server**:
``docker-compose up --build -d``
_________________________________________________________
### API Documentation

_________________________________________________________
### Automatic Speech Recognition and Speaker Diarization (ASR + Diarization)
- **URL:** `/invocations`
- **HTTP Method:** `POST`
- **Request Headers:**
  - `Content-Type: application/json`

**Request Example:**
```bash
curl -X POST server-url/invocations -H "Content-Type: application/json" -H "charset: utf-8" --data '{"dataframe_records": ["Your audio file binary, base64 encoded and utf-8 decoded"], "params": {"language": "pl", "batch_size": 0, "suppress_numerals": false, "no_stem": true}}'
```

**Request Body:**
```json
{
  "instances": ["Your audio file binary, base64 encoded and utf-8 decoded"],
  "params": {
    "language": "pl",
    "whisper_prompt": null,
    "num_speakers": 2,
  }
}
```

**Response Example:**
```json
{
  "predictions": [
    [
      {
        "speaker_id": 0,
        "text": "Speaker 0 text here."
      },
      {
        "speaker_id": 1,
        "text": "Speaker 1 text here."
      },
      {
        "speaker_id": 0,
        "text": "Speaker 0 text here."
      }
    ]
  ]
}
```
_________________________________________________________
#### Named Entity Recognition (NER)
The Named Entity Recognition (NER) endpoint classifies entities within a given text.
- **URL:** `/invocations`
- **HTTP Method:** `POST`
- **Request Headers:**
  - `Content-Type: application/json`

**Request Example:**
```bash
curl -X POST server-url/invocations -H "Content-Type: application/json" --data '{"instances": ["Your text here"]}'

```

**Request Body:**
```bash
{
  "instances": ["Your text here"]
}
```

**Response Example:**
```json
{
  "predictions": ["Predicted text with entities wrapped in markers"]
}
```
**Entity Markers:**
Entities in the predicted text are enclosed in specific tags:
* `<LOC>LOCATION</LOC>`: Indicates a location entity.
* `<MISC>NAMED ENTITY</MISC>`: Indicates a miscellaneous named entity.
* `<ORG>ORGANIZATION</ORG>`: Indicates an organization entity.
* `<PER>PERSON</PER>`: Indicates a person entity.
_________________________________________________________
#### GPT Summarizer
The GPT Summarizer endpoint processes conversations and returns a summarized version.
- **URL:** `/invocations`
- **HTTP Method:** `POST`
- **Request Headers:**
  - `Content-Type: application/json`

**Request Example:**
```bash
curl -X POST server-url/invocations -H "Content-Type: application/json" --data '{"instances": [{"conversation": "Your conversation goes here"}]}'
```

**Request Body:**
```bash
{
  "instances": [
    {
      "conversation": ["Your conversation goes here"]
    }
  ]
}
```

**Response Example:**
```json
{
  "predictions": ["Summarized Conversation"]
}
```

#### Speaker Classifier
The Speaker Classifier endpoint processes conversations and returns a JSON containing a mapping of speaker IDs and their roles.
- **URL:** `/invocations`
- **HTTP Method:** `POST`
- **Request Headers:**
  - `Content-Type: application/json`

**Request Example:**
```bash
curl -X POST server-url/invocations -H "Content-Type: application/json" --data '{"instances": [{"conversation": "Your conversation goes here"}]}'
```

**Request Body:**
```bash
{
  "instances": [
    {
      "conversation": ["Your conversation goes here"]
    }
  ]
}
```

**Response Example:**
```json
{
  "predictions": ["{'speaker 0': 'agent', 'speaker 1': 'client'}"]
}
```
