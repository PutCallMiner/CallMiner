from webapp.models.record import PyObjectId


class RecordingAlreadyExistsError(Exception):
    def __init__(self, recording_url: str):
        msg = f"Recording with url '{recording_url}' already exists"
        super().__init__(msg)
        self.recording_url = recording_url


class RecordingNotFoundError(Exception):
    def __init__(self, recording_id: PyObjectId):
        msg = f"Recording with id '{recording_id}' doesn't exist"
        super().__init__(msg)
        self.recording_id = recording_id


class BlobDownloadError(Exception):
    def __init__(self, url: str):
        msg = f"Could not download blob at URL '{url}'"
        super().__init__(msg)
        self.url = url


class AnalysisInProgressError(Exception):
    def __init__(self, recording_id: PyObjectId):
        msg = f"Analysis on recording {recording_id} is already in progress"
        super().__init__(msg)
        self.recording_id = recording_id


class ASRError(Exception):
    pass


class SummarizerError(Exception):
    pass


class NERError(Exception):
    pass


class SpeakerClassifierError(Exception):
    pass
