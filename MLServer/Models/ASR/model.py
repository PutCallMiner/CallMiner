import io
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import mlflow.pyfunc  # type: ignore
import pandas as pd  # type: ignore
from pydub import AudioSegment  # type: ignore
from whisper_nemo_diarization import (
    DiarizationConfig,
    DiarizationParams,
    DiarizationPipeline,
    SentenceDict,
)

logging.getLogger().setLevel(logging.INFO)


class ASRModelWrapper(mlflow.pyfunc.PythonModel):
    def _write_audio_to_files(
        self, audios: List[bytes], temp_dir_path: Path
    ) -> List[str]:
        logging.info("Writing input audio to files")
        audio_names = []
        for i, audio_bytes in enumerate(audios):
            audio_segment: AudioSegment = AudioSegment.from_file(
                io.BytesIO(audio_bytes)
            )
            audio_name = f"audio_{i}"
            audio_segment.export(temp_dir_path / f"{audio_name}.wav", format="wav")
            audio_names.append(audio_name)
        return audio_names

    def _perform_asr(
        self,
        audio_names: List[str],
        diar_params: DiarizationParams,
        temp_dir_path: Path,
    ) -> List[List[SentenceDict]]:
        logging.info("Started ASR inference on written audio files")
        results = []
        for i, audio_name in enumerate(audio_names):
            audio_path = temp_dir_path / f"{audio_name}.wav"
            curr_result = self.pipeline.run(
                audio_path.absolute(), diar_params=diar_params
            )
            results.append(curr_result)
            logging.info(f"Processed {i+1}/{len(audio_names)} input records")
        logging.info("Finished ASR inference on written audio files data")
        return results

    def validate_model_config(self, model_config: Dict[str, str]):
        errors = []
        valid_whisper_models = [
            "tiny",
            "base",
            "medium",
            "large",
            "large-v2",
            "large-v3",
        ]
        whisper_model = model_config["whisper_model"]
        if whisper_model not in valid_whisper_models:
            errors.append(
                f"Invalid value '{whisper_model}' for 'whisper_model' in model_config"
            )
        if errors:
            raise ValueError("Invalid model_config:\n" + "\n".join(errors))

    def load_context(self, context):
        model_config: Dict[str, str] = context.model_config
        self.validate_model_config(model_config)

        diar_params = DiarizationConfig(
            whisper_model=model_config.get("whisper_model"),
            device=model_config.get("device", "cpu"),
        )
        self.pipeline = DiarizationPipeline(diar_config=diar_params)
        logging.info("Loaded model context")

    def predict(
        self,
        context,
        model_input: pd.DataFrame,
        params: Optional[mlflow.pyfunc.Dict[str, mlflow.pyfunc.Any]] = None,
    ):
        audios: List[bytes] = [in_audio for _, in_audio in model_input.itertuples()]
        if params is None:
            params = {}
        diar_params = DiarizationParams(
            num_speakers=params.get("num_speakers", None),
            beam_size=params.get("beam_size", None),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            audio_names = self._write_audio_to_files(audios, temp_dir_path)
            results = self._perform_asr(
                audio_names, diar_params=diar_params, temp_dir_path=temp_dir_path
            )

        return results
