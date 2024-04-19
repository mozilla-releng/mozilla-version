import pytest

import mozilla_version


@pytest.mark.parametrize(
    "version_type",
    [
        "DeveditionVersion",
        "FirefoxVersion",
        "MavenVersion",
        "MobileVersion",
        "ThunderbirdVersion",
    ],
)
def test_(version_type):
    getattr(mozilla_version, version_type)
