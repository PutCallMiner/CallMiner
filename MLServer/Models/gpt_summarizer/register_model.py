import mlflow
import openai
from model import MAX_TOKENS, MESSAGES, MODEL, TEMPERATURE

if __name__ == "__main__":
    with mlflow.start_run():
        mlflow.openai.log_model(
            model=MODEL,
            registered_model_name="gpt_summarizer",
            task=openai.chat.completions,
            artifact_path="model",
            messages=MESSAGES,
            pip_requirements="requirements.txt",
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
