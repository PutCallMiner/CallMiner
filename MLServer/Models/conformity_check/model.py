MODEL = "callminer-gpt-4o-mini"

SYSTEM_PROMPT = """Your task is to verify if each provided intent is fulfilled in the client-agent conversation entries from a call center.
Use the intent descriptions and examples as guidelines for accurate assessment.
""".strip()

USER_PROMPT = """
You will receive a list of predefined intents to verify, each containing an intent name, description, and examples. Your task is to analyze a series of conversation fragments between a call center agent and a client, where each fragment contains only the agent's phrases. Each fragment includes an Entry ID and Entry Text.

### Instructions:
1. **Identify Fulfilled Intents**: Review each intent's description and examples, then check if there is a logical match within the Entry Text. An intent is considered fulfilled if it aligns in purpose and meaning with the Entry Text.
   
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
    - Ensure the output JSON follows the exact schema above.
    - Your answer must not contain any markdown.

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
MAX_TOKENS = 256
TEMPERATURE = 0.1
