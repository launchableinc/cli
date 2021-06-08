import json
import gzip
import requests
import os
import platform
from launchable.version import __version__
from .authentication import get_org_workspace, authentication_headers
from .logger import Logger, AUDIT_LOG_FORMAT
from .env_keys import BASE_URL_KEY


DEFAULT_BASE_URL = "https://api.mercury.launchableinc.com"


def get_base_url():
    return os.getenv(BASE_URL_KEY) or DEFAULT_BASE_URL


class LaunchableClient:
    def __init__(self, base_url: str = "", session: requests.Session = requests.Session(), test_runner: str = ""):
        self.base_url = base_url or get_base_url()
        self.session = session
        self.test_runner = test_runner

        self.organization, self.workspace = get_org_workspace()
        if self.organization is None or self.workspace is None:
            raise ValueError("Organization/workspace cannot be empty")

    def request(self, method, sub_path, payload=None, timeout=(5, 60), compress=False):
        url = _join_paths(self.base_url, "/intake/organizations/{}/workspaces/{}".format(self.organization, self.workspace), sub_path)

        headers = self._headers(compress)

        Logger().audit(AUDIT_LOG_FORMAT.format("post", url, headers, payload))

        data = _build_data(payload, compress)

        try:
            response = self.session.request(method, url, headers=headers, timeout=timeout, data=data)
            Logger().debug(
                "received response status:{} message:{} headers:{}".format(
                    response.status_code, response.reason, response.headers)
            )
            return response
        except Exception as e:
            raise Exception("unable to post to %s" % url) from e

    def _headers(self, compress):
        h = {
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(),
                                                                 platform.platform()),
            "Content-Type": "application/json"
        }

        if compress:
            h["Content-Encoding"] = "gzip"

        if self.test_runner != "":
            h["launchable-test-runner"] = self.test_runner

        return {**h, **authentication_headers()}


def _build_data(payload, compress):
    if payload is None:
        return None

    encoded = json.dumps(payload).encode()
    if compress:
        return gzip.compress(encoded)

    return encoded


def _join_paths(*components):
    return '/'.join([c.strip('/') for c in components])
