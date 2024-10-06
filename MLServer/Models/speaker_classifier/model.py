MODEL = "callminer-gpt-4o-mini"

SYSTEM_PROMPT = """Your task is to accurately identify the roles of the speakers in a conversation based on a given short transcription.
The goal is to determine which speaker is the call center agent and which one is the client.
""".strip()

USER_PROMPT = """
You will be provided with a transcript of a conversation between a call center agent and a client. Your task is to classify the speakers and output the result in JSON format.

- The **agent** is the person representing the call center or company, providing assistance, information, or services.
- The **client** is the person seeking help, making inquiries, or receiving support from the agent.

The expected format is a single line containing JSON object like: 
{{"speaker 0": "agent", "speaker 1": "client"}} or 
{{"speaker 0": "client", "speaker 1": "agent"}} 
depending on the correct assignment of roles.

Transcript for role classification:
{transcript}
Answer: 
""".strip()

MESSAGES = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT}
]

# Parameters
MAX_TOKENS = 100
TEMPERATURE = 0.1
