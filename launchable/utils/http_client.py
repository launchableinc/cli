import requests
import os
import platform
from launchable.version import __version__


BASE_URL_KEY = "LAUNCHABLE_BASE_URL"
DEFAULT_BASE_URL = "https://api.mercury.launchableinc.com"


def get_base_url():
    return os.getenv(BASE_URL_KEY) or DEFAULT_BASE_URL


class LaunchableClient:
    def __init__(self, token, base_url="", http=requests):
        self.base_url = base_url or get_base_url()
        self.http = http
        self.token = token

    def request(self, method, path, **kwargs):
        headers = kwargs.pop("headers")
        url = self.base_url + path
        try:
            return self.http.request(method, url, headers={**headers, **self._headers()}, **kwargs)
        except Exception as e:
            raise Exception("unable to post to %s" % url) from e

    def _headers(self):
        return {
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(), platform.platform()),
            'Authorization': 'Bearer {}'.format(self.token)
        }
