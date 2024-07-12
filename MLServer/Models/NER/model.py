import os
import mlflow.pyfunc
import spacy
import pandas as pd
import logging

from typing import List

logging.getLogger().setLevel(logging.INFO)


class NERModelWrapper(mlflow.pyfunc.PythonModel):

    def load_context(self, context):
        logging.info("Starting loading NER model context")
        ner_model_name = context.model_config["ner_model"]
        return_code = os.system(f"python -m spacy download {ner_model_name}")
        if return_code != 0:
            raise Exception(f"Failed to download model {ner_model_name}")
        self.ner = spacy.load(ner_model_name)
        logging.info("Loaded NER model context")

    def predict(self, context, model_input: pd.DataFrame) -> List[str]:
        logging.info("Starting NER inference")
        result = []
        i = 0
        for _, text in model_input.itertuples():
            text_copy = text
            doc_text = self.ner(text_copy)
            for ent in sorted(doc_text.ents, key=lambda x: x.end_char, reverse=True):
                text_copy = text_copy[:ent.start_char] + f"<{ent.label_}>{ent.text}</{ent.label_}>" + text_copy[ent.end_char:]
            result.append(text_copy)
            i += 1
            logging.info(f"Processed {i}/{len(model_input)} input records")
        logging.info("Finished NER inference")
        return result
