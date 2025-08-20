from .exceptions import ParseSessionException


def validate_session_format(session: str):
    # session format:
    # builds/<build name>/test_sessions/<test session id>
    if session.count("/") != 3:
        raise ParseSessionException(session=session)


def parse_session(session: str):
    validate_session_format(session)

    _, build_name, _, session_id = session.split("/")
    return build_name, session_id
