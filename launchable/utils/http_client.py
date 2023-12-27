import gzip
import json
import os
import platform
from typing import IO, BinaryIO, Dict, Optional, Tuple, Union

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore

from launchable.version import __version__

from .authentication import authentication_headers
from .env_keys import BASE_URL_KEY
from .gzipgen import compress as gzipgen_compress
from .logger import AUDIT_LOG_FORMAT, Logger

DEFAULT_BASE_URL = "https://api.mercury.launchableinc.com"

# (connect timeout, read timeout)
DEFAULT_TIMEOUT: Tuple[int, int] = (5, 60)
DEFAULT_GET_TIMEOUT: Tuple[int, int] = (5, 15)


def get_base_url():
    return os.getenv(BASE_URL_KEY) or DEFAULT_BASE_URL


class DryRunResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def raise_for_status(self):
        return

    def json(self):
        return self.payload


class _HttpClient:
    def __init__(self, base_url: str = "", session: Optional[Session] = None,
                 test_runner: Optional[str] = "", dry_run: bool = False):
        self.base_url = base_url or get_base_url()
        self.dry_run = dry_run

        if session is None:
            strategy = Retry(
                total=3,
                allowed_methods=["GET", "PUT", "PATCH", "DELETE"],
                status_forcelist=[429, 500, 502, 503, 504],
                backoff_factor=2
            )

            adapter = HTTPAdapter(max_retries=strategy)
            s = Session()
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            self.session = s
        else:
            self.session = session  # type: ignore

        self.test_runner = test_runner

    def request(
        self,
        method: str,
        path: str,
        payload: Optional[Union[Dict, BinaryIO]] = None,
        params: Optional[Dict] = None,
        timeout: Tuple[int, int] = DEFAULT_TIMEOUT,
        compress: bool = False,
        additional_headers: Optional[Dict] = None,
    ):
        url = _join_paths(self.base_url, path)

        if (timeout == DEFAULT_TIMEOUT and method.upper() == "GET"):
            timeout = DEFAULT_GET_TIMEOUT

        headers = self._headers(compress)
        if additional_headers:
            headers = {**headers, **additional_headers}

        Logger().audit(AUDIT_LOG_FORMAT.format("(DRY RUN) " if self.dry_run else "", method, url, headers, payload))

        if self.dry_run and method.upper() not in ["HEAD", "GET"]:
            return DryRunResponse(status_code=200, payload={
                "id": "dry-run-session",  # `record session` use this
                "testPaths": [],  # `split_subset` use this
                "rest": [],  # `split_subset` use this
            })

        data = _build_data(payload, compress)

        # the 'data' argument accepts generator. whenever we can potentially send a large amount of data,
        # we want to use generator to stream data
        response = self.session.request(method, url, headers=headers, timeout=timeout, data=data, params=params)
        Logger().debug(
            "received response status:{} message:{} headers:{}".format(response.status_code, response.reason,
                                                                       response.headers)
        )
        return response

    def _headers(self, compress):
        h = {
            "User-Agent": "Launchable/{} (Python {}, {})".format(
                __version__,
                platform.python_version(),
                platform.platform(),
            ),
            "Content-Type": "application/json"
        }

        if compress:
            h["Content-Encoding"] = "gzip"

        if self.test_runner != "":
            h["User-Agent"] = h["User-Agent"] + " TestRunner/{}".format(self.test_runner)

        return {**h, **authentication_headers()}


def _file_to_generator(f: IO, chunk_size=4096):
    """
    Returns a generator that reads from a given file-like object
    """
    while True:
        data = f.read(chunk_size)
        if not data:
            break
        yield data


def _build_data(payload: Optional[Union[BinaryIO, Dict]], compress: bool):
    if payload is None:
        return None
    if isinstance(payload, dict):
        encoded = json.dumps(payload).encode()
        if compress:
            return gzip.compress(encoded)
        else:
            return encoded
    else:
        # payload is BinaryIO
        if compress:
            # this produces a generator
            return gzipgen_compress(_file_to_generator(payload))
        else:
            return payload


def _join_paths(*components):
    return '/'.join([c.strip('/') for c in components])
