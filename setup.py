from setuptools import setup


def local_scheme():
    """Skip the local version (eg. +xyz of 0.6.1.dev4+gdf99fe2)
    to be able to upload to Test PyPI"""
    def _local_scheme(version):
        return ""
    return {"local_scheme": _local_scheme}


setup(
    use_scm_version=local_scheme
)
