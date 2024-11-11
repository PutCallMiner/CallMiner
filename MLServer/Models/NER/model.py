import logging
import os

import mlflow.pyfunc.model
import pandas as pd
import spacy

logging.getLogger().setLevel(logging.INFO)


class NERModelWrapper(mlflow.pyfunc.model.PythonModel):
    def load_context(self, context):
        logging.info("Starting loading NER model context")
        ner_model_name = context.model_config["ner_model"]
        return_code = os.system(f"python -m spacy download {ner_model_name}")
        if return_code != 0:
            raise Exception(f"Failed to download model {ner_model_name}")
        self.ner = spacy.load(ner_model_name)
        logging.info("Loaded NER model context")

    def predict(self, context, model_inputs: pd.DataFrame):
        logging.info("Starting NER inference")
        result = []
        for _, text in model_inputs.itertuples():
            result.append(self.ner(text).to_json())
        return result
