from webapp.models.analysis import AnalyzeParams, ASRParams

EUROTAX_PARAMS = AnalyzeParams(
    asr=ASRParams(
        language="pl",
        num_speakers=2,
        whisper_prompt=None,
    )
)
