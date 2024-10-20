import io

from pydub import AudioSegment


def get_audio_duration(audio: bytes) -> int:
    """Calculate audio duration in miliseconds"""
    audio_seg = AudioSegment.from_file(io.BytesIO(audio))
    return len(audio_seg)
