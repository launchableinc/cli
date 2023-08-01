from enum import Enum
from typing import Dict, Any, Optional, Union

from launchable.utils.http_client import LaunchableClient
from launchable.version import __version__


class Tracking:
    # General events
    class Event(Enum):
        SHALLOW_CLONE = 'shallow_clone'  # this event is an example

    # Error events
    class ExceptionEvent(Enum):
        UNKNOWN_ERROR = 'UNKNOWN_ERROR'
        INTERNAL_CLI_ERROR = 'INTERNAL_CLI_ERROR'
        # Errors related to requests package
        NETWORK_ERROR = 'NETWORK_ERROR'
        TIMEOUT_ERROR = 'TIMEOUT_ERROR'
        INTERNAL_ERROR = 'INTERNAL_ERROR'
        UNEXPECTED_HTTP_STATUS_ERROR = 'UNEXPECTED_HTTP_STATUS_ERROR'

    class Command(Enum):
        VERIFY = 'VERIFY'
        RECORD_TESTS = 'RECORD_TESTS'
        RECORD_BUILD = 'RECORD_BUILD'
        RECORD_SESSION = 'RECORD_SESSION'
        SUBSET = 'SUBSET'


class TrackingClient:
    def __init__(self, http_client: LaunchableClient) -> None:
        self.http_client = http_client

    def send_event(
        self,
        command: Tracking.Command,
        event_name: Union[Tracking.Event, Tracking.ExceptionEvent],
        organization: str = "",
        workspace: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        if metadata is None:
            metadata = {}
        metadata["organization"] = organization
        metadata["workspace"] = workspace
        self.post_payload(
            command=command,
            event_name=event_name,
            metadata=metadata,
        )

    def send_error_event(
        self,
        command: Tracking.Command,
        event_name: Union[Tracking.Event, Tracking.ExceptionEvent],
        stack_trace: str,
        organization: str = "",
        workspace: str = "",
        api: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        if metadata is None:
            metadata = {}
        metadata["stackTrace"] = stack_trace
        metadata["organization"] = organization
        metadata["workspace"] = workspace
        metadata["api"] = api
        self.post_payload(
            command=command,
            event_name=event_name,
            metadata=metadata,
        )

    def post_payload(
        self,
        command: Tracking.Command,
        event_name: Union[Tracking.Event, Tracking.ExceptionEvent],
        metadata: Dict[str, Any]
    ):
        payload = {
            "command": command.value,
            "eventName": event_name.value,
            "cliVersion": __version__,
            "metadata": metadata,
        }
        try:
            self.http_client.request('post', 'cli_tracking', payload=payload, base_path='/intake')
        except Exception:
            pass
