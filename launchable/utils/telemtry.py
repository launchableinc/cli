from enum import Enum
from typing import Optional
from requests import Session
from typing import Dict, Any

from launchable.utils.http_client import LaunchableClient


class Telemetry:
    # General events
    class Event(Enum):
        SHALLOW_CLONE = 'shallow_clone'  # this event is an example

    # Error events
    class ExceptionEvent(Enum):
        UNKNOWN_ERROR = 'unknownError'
        INTERNAL_CLI_ERROR = 'internalCliError'
        # Errors related to requests package
        NETWORK_ERROR = 'networkError'
        TIMEOUT_ERROR = 'timeoutError'
        INTERNAL_ERROR = 'internalError'
        UNEXPECTED_HTTP_STATUS_ERROR = 'unexpectedHttpStatusError'

    class Command(Enum):
        VERIFY = 'verify'
        TESTS = 'tests'
        BUILD = 'build'
        SESSION = 'session'
        SUBSET = 'subset'


class TelemetryClient:
    def __init__(self, http_client: LaunchableClient) -> None:
        self.http_client = http_client

    def send_error_event(
        self,
        command: Telemetry.Command,
        event_name: Telemetry.Event | Telemetry.ExceptionEvent,
        stack_trace: str,
        organization: str = "",
        workspace: str = "",
        api: str = "",
        metadata: Dict[str, Any] = {}
    ):
        metadata["stacktrace"] = stack_trace
        if organization:
            metadata["organization"] = organization
        if workspace:
            metadata["workspace"] = workspace
        if api:
            metadata["api"] = api
        payload = {
            "command": command.value,
            "eventName": event_name.value,
            "metadata": metadata,
        }
        try:
            self.http_client.request('post', 'tracking', payload=payload, base_path='/intake')
        except Exception as e:
            pass
