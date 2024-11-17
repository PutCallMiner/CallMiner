from webapp.models.record import PyObjectId


class RecordingAlreadyExistsError(Exception):
    def __init__(self, blob_name: str):
        msg = f"Recording with name '{blob_name}' already exists"
        super().__init__(msg)
        self.blob_name = blob_name


class RecordingNotFoundError(Exception):
    def __init__(self, recording_id: PyObjectId):
        msg = f"Recording with id '{recording_id}' doesn't exist"
        super().__init__(msg)
        self.recording_id = recording_id


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


class ConformityCheckError(Exception):
    pass
