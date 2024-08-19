class RecordingAlreadyExistsError(Exception):
    def __init__(self, recording_url: str):
        msg = f"Recording with url '{recording_url}' already exists"
        super().__init__(msg)
        self.recording_url = recording_url
