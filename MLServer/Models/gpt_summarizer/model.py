MODEL = "callminer-gpt-35-turbo"

PROMPT = """
Generate a concise summary of the following conversation, ensuring that the summary is presented in the same language as the original dialogue. The summary should capture the key points, decisions made, and any actions to be taken, reflecting the tone and context of the conversation accurately.
Conversation:
{conversation}

Summary:
""".strip()

MESSAGES = [
    {"role": "user", "content": PROMPT}
]

# Parameters
MAX_TOKENS = 500
TEMPERATURE = 0.5