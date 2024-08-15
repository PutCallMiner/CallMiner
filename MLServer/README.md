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
