# TODO: add cli-specific custom exceptions

class ParseSessionException(Exception):
    def __init__(
        self,
        session: str,
        message: str = "Wrong session format; session format is like 'builds/<build name>/test_sessions/<test session id>'.",
    ):
        self.session = session
        self.message = f"{message}: {self.session}"
        super().__init__(self.message)


class InvalidJUnitXMLException(Exception):
    def __init__(
        self,
        filename: str,
        message: str = "Invalid JUnit XML file format",
    ):
        self.filename = filename
        self.message = f"{message}: {filename}"
        super().__init__(self.message)
