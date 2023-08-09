
from typing import Dict, Optional, Tuple

from requests import HTTPError, Session, Timeout

from launchable.utils.http_client import _HttpClient, _join_paths
from launchable.utils.tracking import Tracking, TrackingClient  # type: ignore

from .authentication import get_org_workspace


class LaunchableClient:
    def __init__(self, tracking_client: Optional[TrackingClient] = None, base_url: str = "", session: Optional[Session] = None,
                 test_runner: Optional[str] = "", dry_run: bool = False):
        self.http_client = _HttpClient(
            base_url=base_url,
            session=session,
            test_runner=test_runner,
            dry_run=dry_run
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
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: Tuple[int, int] = (5, 60),
        compress: bool = False,
    ):
        path = _join_paths(
            "/intake/organizations/{}/workspaces/{}".format(self.organization, self.workspace),
            sub_path
        )

        try:
            response = self.http_client.request(
                method=method,
                path=path,
                payload=payload,
                params=params,
                timeout=timeout,
                compress=compress
            )
            return response
        except ConnectionError as e:
            if self.tracking_client:
                self.tracking_client.send_error_event(
                    event_name=Tracking.ErrorEvent.NETWORK_ERROR,
                    stack_trace=str(e),
                    organization=self.organization,
                    workspace=self.workspace,
                    api=sub_path,
                )
            raise e
        except Timeout as e:
            if self.tracking_client:
                self.tracking_client.send_error_event(
                    event_name=Tracking.ErrorEvent.TIMEOUT_ERROR,
                    stack_trace=str(e),
                    organization=self.organization,
                    workspace=self.workspace,
                    api=sub_path,
                )
            raise e
        except HTTPError as e:
            if self.tracking_client:
                self.tracking_client.send_error_event(
                    event_name=Tracking.ErrorEvent.UNEXPECTED_HTTP_STATUS_ERROR,
                    stack_trace=str(e),
                    organization=self.organization,
                    workspace=self.workspace,
                    api=sub_path,
                )
            raise e
        except Exception as e:
            if self.tracking_client:
                self.tracking_client.send_error_event(
                    event_name=Tracking.ErrorEvent.INTERNAL_SERVER_ERROR,
                    stack_trace=str(e),
                    organization=self.organization,
                    workspace=self.workspace,
                    api=sub_path,
                )
            raise e
