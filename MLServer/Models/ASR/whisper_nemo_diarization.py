# Original code taken from: https://colab.research.google.com/drive/1X5XTiob6irFq8NJM831S0ADwz5_wIS-r#scrollTo=si9d95bmi4dd

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict

import wget  # type: ignore
import whisperx  # type: ignore
from deepmultilingualpunctuation import PunctuationModel  # type: ignore
from nemo.collections.asr.models.msdd_models import ClusteringDiarizer  # type: ignore
from omegaconf import OmegaConf
from openai import NOT_GIVEN, AzureOpenAI
from whisperx.alignment import SingleWordSegment  # type: ignore

AZURE_API_KEY = os.environ["AZURE_API_KEY"]
AZURE_API_VERSION = os.environ["AZURE_API_VERSION"]
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_WHISPER_ENDPOINT = os.environ["AZURE_WHISPER_ENDPOINT"]
ALIGN_MODEL_DEVICE = "cpu"


class TranscribeSegment(TypedDict):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class TranscribeResults(TypedDict):
    text: str
    segments: list[TranscribeSegment]
    language: str


class WordDict(TypedDict):
    word: str
    start_time: int
    end_time: int
    speaker: int


class SentenceDict(TypedDict):
    speaker: int
    start_time: int
    end_time: int
    text: str


WordAnchorOptionType = Literal["start", "mid", "end"]


def _get_word_ts_anchor(start: int, end: int, option: WordAnchorOptionType = "start"):
    if option == "end":
        return end
    elif option == "mid":
        return (start + end) / 2
    return start


def _get_words_speaker_mapping(
    wrd_ts: list[SingleWordSegment],
    spk_ts: list[tuple[int, int, int]],
    word_anchor_option: WordAnchorOptionType = "start",
) -> list[WordDict]:
    s, e, sp = spk_ts[0]
    wrd_pos, turn_idx = 0, 0
    wrd_spk_mapping = []
    for wrd_dict in wrd_ts:
        ws, we, wrd = (
            int(wrd_dict["start"] * 1000),
            int(wrd_dict["end"] * 1000),
            wrd_dict["word"],
        )
        wrd_pos = _get_word_ts_anchor(ws, we, word_anchor_option)
        while wrd_pos > float(e):
            turn_idx += 1
            turn_idx = min(turn_idx, len(spk_ts) - 1)
            s, e, sp = spk_ts[turn_idx]
        wrd_spk_mapping.append(
            WordDict(word=wrd, start_time=ws, end_time=we, speaker=sp)
        )
    return wrd_spk_mapping


SENTENCE_ENDING_PUNCTUATIONS = ".?!"


def _get_first_word_idx_of_sentence(
    word_idx: int, word_list: list[str], speaker_list: list[int], max_words: int
):
    def is_word_sentence_end(x: int):
        return x >= 0 and word_list[x][-1] in SENTENCE_ENDING_PUNCTUATIONS

    left_idx = word_idx
    while (
        left_idx > 0
        and word_idx - left_idx < max_words
        and speaker_list[left_idx - 1] == speaker_list[left_idx]
        and not is_word_sentence_end(left_idx - 1)
    ):
        left_idx -= 1

    return left_idx if left_idx == 0 or is_word_sentence_end(left_idx - 1) else -1


def _get_last_word_idx_of_sentence(word_idx: int, word_list: list[str], max_words: int):
    def is_word_sentence_end(x: int):
        return x >= 0 and word_list[x][-1] in SENTENCE_ENDING_PUNCTUATIONS

    right_idx = word_idx
    while (
        right_idx < len(word_list)
        and right_idx - word_idx < max_words
        and not is_word_sentence_end(right_idx)
    ):
        right_idx += 1

    return (
        right_idx
        if right_idx == len(word_list) - 1 or is_word_sentence_end(right_idx)
        else -1
    )


def _get_realigned_ws_mapping_with_punctuation(
    word_speaker_mapping: list[WordDict], max_words_in_sentence: int = 50
) -> list[WordDict]:
    def is_word_sentence_end(x):
        return (
            x >= 0
            and word_speaker_mapping[x]["word"][-1] in SENTENCE_ENDING_PUNCTUATIONS
        )

    wsp_len = len(word_speaker_mapping)

    words_list: list[str] = []
    speaker_list: list[int] = []
    for k, line_dict in enumerate(word_speaker_mapping):
        word, speaker = line_dict["word"], line_dict["speaker"]
        words_list.append(word)
        speaker_list.append(speaker)

    k = 0
    while k < len(word_speaker_mapping):
        line_dict = word_speaker_mapping[k]
        if (
            k < wsp_len - 1
            and speaker_list[k] != speaker_list[k + 1]
            and not is_word_sentence_end(k)
        ):
            left_idx = _get_first_word_idx_of_sentence(
                k, words_list, speaker_list, max_words_in_sentence
            )
            right_idx = (
                _get_last_word_idx_of_sentence(
                    k, words_list, max_words_in_sentence - k + left_idx - 1
                )
                if left_idx > -1
                else -1
            )
            if min(left_idx, right_idx) == -1:
                k += 1
                continue

            spk_labels = speaker_list[left_idx : right_idx + 1]
            mod_speaker = max(set(spk_labels), key=spk_labels.count)
            if spk_labels.count(mod_speaker) < len(spk_labels) // 2:
                k += 1
                continue

            speaker_list[left_idx : right_idx + 1] = [mod_speaker] * (
                right_idx - left_idx + 1
            )
            k = right_idx

        k += 1

    k, realigned_list = 0, []
    while k < len(word_speaker_mapping):
        line_dict = word_speaker_mapping[k].copy()
        line_dict["speaker"] = speaker_list[k]
        realigned_list.append(line_dict)
        k += 1

    return realigned_list


def _get_sentences_speaker_mapping(
    word_speaker_mapping: list[WordDict], spk_ts: list[tuple[int, int, int]]
) -> list[SentenceDict]:
    s, e, spk = spk_ts[0]
    prev_spk = spk

    snts = []
    snt = SentenceDict(speaker=spk, start_time=s, end_time=e, text="")

    for wrd_dict in word_speaker_mapping:
        wrd, spk = wrd_dict["word"], wrd_dict["speaker"]
        s, e = wrd_dict["start_time"], wrd_dict["end_time"]
        if spk != prev_spk:
            snts.append(snt)
            snt = SentenceDict(
                speaker=spk,
                start_time=s,
                end_time=e,
                text="",
            )
        else:
            snt["end_time"] = e
        snt["text"] += wrd + " "
        prev_spk = spk

    snts.append(snt)
    return snts


@dataclass
class DiarizationParams:
    language: str | None = None
    whisper_prompt: str | None = None
    num_speakers: int | None = None


class DiarizationPipeline:
    def __init__(self, results_dir: str | None = None):
        self.temp_dir = None
        if results_dir is None:
            self.temp_dir = tempfile.TemporaryDirectory()
            self.results_dir = Path(self.temp_dir.name)
        else:
            self.results_dir = Path(results_dir)

    def _transcribe(
        self, audio: Path, diar_params: DiarizationParams
    ) -> TranscribeResults:
        client = AzureOpenAI(
            api_key=AZURE_API_KEY,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

        result = client.audio.transcriptions.create(
            file=open(audio, "rb"),
            model=AZURE_WHISPER_ENDPOINT,
            response_format="verbose_json",
            language=diar_params.language
            if diar_params.language is not None
            else NOT_GIVEN,
            prompt=diar_params.whisper_prompt
            if diar_params.whisper_prompt is not None
            else NOT_GIVEN,
        )

        assert (
            result.model_extra is not None
        ), "Azure whisper didn't return verbose response!"

        return TranscribeResults(
            text=result.text,
            segments=result.model_extra["segments"],
            language=diar_params.language
            if diar_params.language is not None
            else result.model_extra["language"],
        )

    def _align(
        self, audio: Path, transcribe_results: TranscribeResults
    ):  # -> AlignResults:
        # WhisperX results in better word timestamps by using wav2vec based forced alignment.
        alignment_model, metadata = whisperx.load_align_model(
            language_code=transcribe_results["language"], device=ALIGN_MODEL_DEVICE
        )
        result_aligned = whisperx.align(
            transcribe_results["segments"],
            alignment_model,
            metadata,
            str(audio),
            ALIGN_MODEL_DEVICE,
        )
        del alignment_model
        return result_aligned

    def _diarize(
        self, audio: Path, rttm_filepath: Path, diar_params: DiarizationParams
    ):
        diarize_manifest = {
            "audio_filepath": str(audio),
            "offset": 0,
            "duration": None,
            "label": "infer",
            "text": "-",
            "num_speakers": diar_params.num_speakers,
            "rttm_filepath": str(rttm_filepath),
            "uniq_id": "",
        }

        manifest_path = self.results_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            f.write(json.dumps(diarize_manifest))

        MODEL_CONFIG_PATH = Path(os.getcwd()) / "diar_infer_telephonic.yaml"
        if not MODEL_CONFIG_PATH.exists():
            config_url = "https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/diar_infer_telephonic.yaml"
            MODEL_CONFIG_PATH = wget.download(config_url, os.getcwd())

        config = OmegaConf.load(MODEL_CONFIG_PATH)

        config.diarizer.manifest_filepath = str(manifest_path)
        config.diarizer.out_dir = str(self.results_dir / "diarized")

        model = ClusteringDiarizer(cfg=config)
        model.diarize()
        del model

    def _punctuate(
        self, rttm_filepath: Path, word_ts: list[SingleWordSegment]
    ) -> list[SentenceDict]:
        # Reading timestamps <> Speaker Labels mapping
        speaker_ts = []
        with open(rttm_filepath, "r") as f:
            lines = f.readlines()
            for line in lines:
                line_list = line.split(" ")
                s = int(float(line_list[5]) * 1000)
                e = s + int(float(line_list[8]) * 1000)
                speaker_ts.append((s, e, int(line_list[11].split("_")[-1])))

        wsm = _get_words_speaker_mapping(word_ts, speaker_ts, "start")

        punct_model = PunctuationModel()
        words_list = list(map(lambda x: x["word"], wsm))
        labeled_words: list[tuple[str, str, float]] = punct_model.predict(words_list)

        # Whisper already punctuates the text in most of the case, so we'll give priority
        # to its puntuation marks over PunctuationModel results.

        ENDING_PUNCTS = ".?!"
        MODEL_PUNCTS = ".,;:!?"

        # We don't want to punctuate U.S.A. with a period. Right?
        def is_acronym(x: str):
            return re.fullmatch(r"\b(?:[a-zA-Z]\.){2,}", x) is not None

        for word_dict, labeled_tuple in zip(wsm, labeled_words):
            word = word_dict["word"]
            if (
                word
                and labeled_tuple[1] in ENDING_PUNCTS
                and (word[-1] not in MODEL_PUNCTS or is_acronym(word))
            ):
                word += labeled_tuple[1]
                if word.endswith(".."):
                    word = word.rstrip(".")
                word_dict["word"] = word

        wsm = _get_realigned_ws_mapping_with_punctuation(wsm)
        ssm = _get_sentences_speaker_mapping(wsm, speaker_ts)

        del punct_model
        return ssm

    def run(
        self, audio: str | Path, diar_params: DiarizationParams | None = None
    ) -> list[SentenceDict]:
        audio = Path(audio)
        if diar_params is None:
            diar_params = DiarizationParams()
        transcribe_results = self._transcribe(audio, diar_params)
        result_aligned = self._align(audio, transcribe_results)

        word_ts = result_aligned["word_segments"]
        # NOTE: this filling in of missing "start"/"end" is just patchwork solution and may be incorrect
        for i, word_dict in enumerate(word_ts):
            if "start" not in word_dict.keys():
                if i == 0:
                    word_dict["start"] = result_aligned["segments"][0]["start"]
                else:
                    word_dict["start"] = word_ts[i - 1]["end"]
            if "end" not in word_dict.keys():
                if i == len(word_ts):
                    word_dict["end"] = result_aligned["segments"][-1]["end"]
                else:
                    word_dict["end"] = word_ts[i + 1]["start"]

        rttm_filepath = (
            self.results_dir / "diarized" / "pred_rttms" / f"{audio.stem}.rttm"
        )
        self._diarize(audio, rttm_filepath, diar_params)

        ssm = self._punctuate(rttm_filepath, word_ts)
        return ssm


## Example usage
if __name__ == "__main__":
    pipeline = DiarizationPipeline()
    diar_params = DiarizationParams(
        language="pl", num_speakers=None, whisper_prompt=None
    )

    transcript = pipeline.run(
        Path(__file__).parent / "POL_M_023_Irek.mp3",
        diar_params=diar_params,
    )
    print(transcript)
