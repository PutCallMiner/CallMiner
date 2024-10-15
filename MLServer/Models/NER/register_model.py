import mlflow
from model import NERModelWrapper

model_config = {
    "ner_model": "pl_core_news_md",
}

signature = mlflow.models.infer_signature(
    model_input=["text"],
    model_output=[["text"]],
)


if __name__ == "__main__":
    with mlflow.start_run():
        mlflow.pyfunc.log_model(
            registered_model_name="ner_model",
            artifact_path="model",
            python_model=NERModelWrapper(),
            signature=signature,
            model_config=model_config,
            pip_requirements="requirements.txt",
        )
