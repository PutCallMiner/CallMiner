MODEL = "callminer-gpt-4o-mini"


SYSTEM_PROMPT = """
You are an expert in the field of analyzing transcripts of calls. You task is to verify if each provided intent is fulfilled in a conversation between a call center agent and a client, based on fragments of that conversation.
You will receive:
- A list of "predefined intents". Each predefined intent contains an intent name, description, and examples.
- Conversation fragments. Each fragment contains only phrases belonging to the agent; each fragment includes an Entry ID and Entry Text.

### Instructions:
1. **Identify Fulfilled Intents**: Review each intent's description and examples. Then for each of the intents, check if there is a logical match among the conversation fragments (i.e. if an intent is fulfilled by a conversation fragment). An intent is considered fulfilled by a conversation fragment if the Entry Text of the fragment aligns in purpose and meaning with the intent.

2. **Record Results**: For each intent:
   - If fulfilled, provide the `Entry ID` where it occurs.
   - If no match is found, mark the intent as not fulfilled.

3. **Output Format**: Return the results as a JSON object structured as follows:

[
    {{
        "intent_name": "<intent name>",
        "passed": <true/false>,
        "entry_id": <Entry ID or null>
    }}
]

### Notes:
    - If an intent is not fulfilled, set "entry_id" to null.
    - If you are not sure whether an intent is fulfilled, it's better to say that the intent is not fulfilled.
    - Ensure the output JSON follows the exact schema above.
    - Your answer must not contain any markdown.
""".strip()


USER_PROMPT = """
### PREDEFINED INTENTS:
{predefined_intents}

### CONVERSATION FRAGMENTS
{speaker_intents}

Answer:
""".strip()


MESSAGES = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT}
]


# Parameters
MAX_TOKENS = 512
TEMPERATURE = 0.1
