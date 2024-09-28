from pathlib import Path

import mlflow  # type: ignore
import mlflow.pyfunc  # type: ignore
from model import ASRModelWrapper

model_config = {"whisper_model": "base", "device": "cpu"}

params = {
    "language": "pl",
    "whisper_prompt": "This is a prompt, but it can be None",
    "num_speakers": 2,
}

signature = mlflow.models.infer_signature(
    model_input=[bytes()],
    model_output=[
        [
            {
                "speaker": 0,
                "start_time": 786,
                "end_time": 2546,
                "text": "Siema, mam in imię Nikita.",
            },
            {
                "speaker": 1,
                "start_time": 3050,
                "end_time": 4689,
                "text": "O, hejka, mam na imię Adam.",
            },
        ]
    ],
    params=params,
)

with mlflow.start_run():
    curr_dir = Path(__file__).parent
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=ASRModelWrapper(),
        signature=signature,
        pip_requirements=str(curr_dir / "requirements.txt"),
        registered_model_name="asr_model",
        code_path=[str(curr_dir / "whisper_nemo_diarization.py")],
    )
