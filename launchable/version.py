from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("launchable")
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
