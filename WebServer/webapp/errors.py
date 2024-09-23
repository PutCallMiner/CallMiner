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


class ASRError(Exception):
    pass


class SummarizerError(Exception):
    pass


class TaskTimeoutError(Exception):
    def __init__(self, task_name: str, task_id: str):
        self.task_name = task_name
        self.task_id = task_id
        super().__init__(
            f"Celery task '{self.task_name}' (ID: {self.task_id}) timed out."
        )
