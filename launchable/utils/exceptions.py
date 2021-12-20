# TODO: add cli-specific custom exceptions

class ParseSessionException(Exception):
    def __init__(
        self,
        session: str,
        message: str = "Wrong session format; session format must be 'builds/<build name>/test_sessions/<test session id>'.",
    ):
        super().__init__(message)
        self.session = session
