import pytest
import requests

from mozilla_version import (
    DeveditionVersion,
    FirefoxVersion,
    MobileVersion,
    ThunderbirdVersion,
)
from mozilla_version.gecko import FennecVersion
from mozilla_version.test.integration import skip_network_tests_by_default

_VERSION_CLASS_PER_PRODUCT = {
    "devedition": DeveditionVersion,
    "fenix": MobileVersion,
    "fennec": FennecVersion,
    "firefox": FirefoxVersion,
    "thunderbird": ThunderbirdVersion,
}


def _fetch_product_details():
    url = "https://product-details.mozilla.org/1.0/all.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise RuntimeError("Failed to fetch testing data")


def get_all_shipped_versions():
    product_details_data = _fetch_product_details()
    all_releases = product_details_data["releases"].keys()
    all_products_and_versions = (
        (release.split("-")[0], "-".join(release.split("-")[1:]))
        for release in all_releases
    )
    return (
        (_VERSION_CLASS_PER_PRODUCT[product.lower()], version)
        for product, version in all_products_and_versions
    )


@skip_network_tests_by_default
@pytest.mark.parametrize("version_class, version", get_all_shipped_versions())
def test_parse_all_shipped_version_in_product_details(version_class, version):
    version_class.parse(version)
