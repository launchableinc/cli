import requests
import os
import platform
import gzip
import copy
import types
import itertools
import logging
from launchable.version import __version__
from .logger import Logger, LOG_LEVEL_AUDIT

BASE_URL_KEY = "LAUNCHABLE_BASE_URL"
DEFAULT_BASE_URL = "https://api.mercury.launchableinc.com"


def get_base_url():
    return os.getenv(BASE_URL_KEY) or DEFAULT_BASE_URL


class LaunchableClient:
    def __init__(self, token: str, base_url: str = "", session: requests.Session = requests.Session(), test_runner: str = ""):
        self.base_url = base_url or get_base_url()
        self.session = session
        self.token = token
        self.test_runner = test_runner

    def request(self, method, path, **kwargs):
        headers = kwargs.pop("headers")
        url = self.base_url + path
        if 'timeout' not in kwargs:
            # (connection timeout, read timeout) in seconds
            kwargs['timeout'] = (5, 60)

        logger = Logger()
        try:
            if LOG_LEVEL_AUDIT >= logging.root.level:
                log_kwargs = copy.copy(kwargs)
                if any("gzip" in h for h in headers.values()) and "data" in log_kwargs:
                    data = log_kwargs.pop("data")
                    if isinstance(data, types.GeneratorType):
                        generator, _generator = itertools.tee(data)

                        log_kwargs["data"] = gzip.decompress(
                            b"".join(_generator)).decode()
                        kwargs["data"] = generator

                    elif isinstance(data, bytes):
                        log_kwargs["data"] = gzip.decompress(data).decode()

                logger.audit(
                    "send request method:{} path:{} headers:{} args:{}".format(method, path, headers, log_kwargs))

            response = self.session.request(
                method, url, headers={**headers, **self._headers()}, **kwargs)
            logger.debug(
                "received response status:{} message:{} headers:{}".format(
                    response.status_code, response.reason, response.headers)
            )
            return response
        except Exception as e:
            raise Exception("unable to post to %s" % url) from e

    def _headers(self):
        h = {
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(), platform.platform()),
            'Authorization': 'Bearer {}'.format(self.token),
        }

        if self.test_runner != "":
            h["launchable-test-runner"] = self.test_runner

        return h
