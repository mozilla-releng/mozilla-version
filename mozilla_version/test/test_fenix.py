from mozilla_version.fenix import FenixVersion
from mozilla_version.mobile import MobileVersion


def test_fenix_version_redirects_to_mobile_version():
    assert FenixVersion == MobileVersion
