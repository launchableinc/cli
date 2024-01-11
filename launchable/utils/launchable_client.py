
from typing import BinaryIO, Dict, Optional, Tuple, Union

from requests import HTTPError, Session, Timeout

from launchable.utils.http_client import _HttpClient, _join_paths
from launchable.utils.tracking import Tracking, TrackingClient  # type: ignore

from ..app import Application
from .authentication import get_org_workspace


class LaunchableClient:
    def __init__(self, tracking_client: Optional[TrackingClient] = None, base_url: str = "", session: Optional[Session] = None,
                 test_runner: Optional[str] = "", app: Optional[Application] = None):
        self.http_client = _HttpClient(
            base_url=base_url,
            session=session,
            test_runner=test_runner,
            app=app
        )
        self.tracking_client = tracking_client
        self.organization, self.workspace = get_org_workspace()
        if self.organization is None or self.workspace is None:
            raise ValueError(
                "Could not identify a Launchable organization/workspace. "
                "Confirm that you set LAUNCHABLE_TOKEN "
                "(or LAUNCHABLE_ORGANIZATION and LAUNCHABLE_WORKSPACE) environment variable(s)\n"
                "See https://docs.launchableinc.com/getting-started#setting-your-api-key")

    def request(
        self,
        method: str,
        sub_path: str,
        payload: Optional[Union[Dict, BinaryIO]] = None,
        params: Optional[Dict] = None,
        timeout: Tuple[int, int] = (5, 60),
        compress: bool = False,
        additional_headers: Optional[Dict] = None,
    ):
        path = _join_paths(
            "/intake/organizations/{}/workspaces/{}".format(self.organization, self.workspace),
            sub_path
        )

        # report an error and bail out
        def track(event_name: Tracking.ErrorEvent, e: Exception):
            if self.tracking_client:
                self.tracking_client.send_error_event(
                    event_name=event_name,
                    stack_trace=str(e),
                    api=sub_path,
                )
            raise e

        try:
            response = self.http_client.request(
                method=method,
                path=path,
                payload=payload,
                params=params,
                timeout=timeout,
                compress=compress,
                additional_headers=additional_headers
            )
            return response
        except ConnectionError as e:
            track(Tracking.ErrorEvent.NETWORK_ERROR, e)
        except Timeout as e:
            track(Tracking.ErrorEvent.TIMEOUT_ERROR, e)
        except HTTPError as e:
            track(Tracking.ErrorEvent.UNEXPECTED_HTTP_STATUS_ERROR, e)
        except Exception as e:
            track(Tracking.ErrorEvent.INTERNAL_SERVER_ERROR, e)
