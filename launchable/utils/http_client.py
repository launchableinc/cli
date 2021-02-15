import requests
import os
import platform
from launchable.version import __version__


BASE_URL_KEY = "LAUNCHABLE_BASE_URL"
DEFAULT_BASE_URL = "https://api.mercury.launchableinc.com"


def get_base_url():
    return os.getenv(BASE_URL_KEY) or DEFAULT_BASE_URL


class LaunchableClient:
    def __init__(self, token: str, base_url: str = "", session: requests.Session = requests.Session()):
        self.base_url = base_url or get_base_url()
        self.session = session
        self.token = token

    def request(self, method, path, **kwargs):
        headers = kwargs.pop("headers")
        url = self.base_url + path
        if 'timeout' not in kwargs:
            # (connection timeout, read timeout) in seconds
            kwargs['timeout'] = (5, 60)

        try:
            return self.session.request(method, url, headers={**headers, **self._headers()}, **kwargs)
        except Exception as e:
            raise Exception("unable to post to %s" % url) from e

    def _headers(self):
        return {
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(), platform.platform()),
            'Authorization': 'Bearer {}'.format(self.token)
        }
