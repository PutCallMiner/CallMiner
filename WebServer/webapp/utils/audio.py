import io

from pydub import AudioSegment


def get_audio_duration(audio: bytes) -> float:
    """Calculate audio duration in seconds"""
    audio_seg = AudioSegment.from_file(io.BytesIO(audio))
    return len(audio_seg) / 1000.0
