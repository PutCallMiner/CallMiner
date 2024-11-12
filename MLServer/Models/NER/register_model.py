import mlflow
import mlflow.models
from model import NERModelWrapper

model_config = {
    "ner_model": "pl_core_news_lg",
}

signature = mlflow.models.infer_signature(
    model_input=["text"],
    model_output=[
        {
            "text": "Poznań",
            "ents": [{"start": 0, "end": 6, "label": "placeName"}],
            "sents": [{"start": 0, "end": 6}],
            "tokens": [
                {
                    "id": 0,
                    "start": 0,
                    "end": 6,
                    "tag": "SUBST",
                    "pos": "PROPN",
                    "morph": "Animacy=Inan|Case=Nom|Gender=Masc|Number=Sing",
                    "lemma": "Poznań",
                    "dep": "ROOT",
                    "head": 0,
                }
            ],
        }
    ],
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
