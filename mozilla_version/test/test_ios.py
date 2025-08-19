import pytest

from mozilla_version.errors import PatternNotMatchedError
from mozilla_version.ios import MobileIosVersion


@pytest.mark.parametrize(
    "version_string, field, expected",
    (
        ("0.9", "major_number", "1.0"),
        ("0.9", "major_number", "1.0"),
        ("1.0", "patch_number", "1.0.1"),
        ("1.5", "minor_number", "1.6"),
        ("2.1", "major_number", "3.0"),
        ("2.0", "major_number", "3.0"),
        ("2.0", "minor_number", "2.1"),
        ("2.0", "patch_number", "2.0.1"),
        ("2.0.1", "patch_number", "2.0.2"),
        ("2.1", "patch_number", "2.1.1"),
        ("2.0b0", "beta_number", "2.0b1"),
        ("2.0b1", "beta_number", "2.0b2"),
        ("2.0b1", "patch_number", "2.0.1"),
    ),
)
def test_ios_version_bump(version_string, field, expected):
    version = MobileIosVersion.parse(version_string)
    assert str(version.bump(field)) == expected


@pytest.mark.parametrize(
    "version_string, expected_beta",
    (
        ("0.0b1", True),
        ("0.1b1", True),
        ("0.1", False),
        ("1.0", False),
        ("1.1", False),
        ("1.1b1", True),
        ("42.0b0", True),
        ("42.0b1", True),
        ("42.0", False),
    ),
)
def test_ios_version_beta(version_string, expected_beta):
    version = MobileIosVersion.parse(version_string)
    assert version.is_beta == expected_beta


@pytest.mark.parametrize(
    "version,other,expected_result",
    (
        ("139.0", "139.0", 0),
        ("139.0.1", "139.0", 1),
        ("139.0.2", "139.0.1", 1),
        ("139.0.1", "139.0.1", 0),
        ("139.0", "139.0.1", -1),
        ("139.0b1", "139.0.1", -1),
        ("139.1", "139.0", 1),
        ("139.1", "140.0", -1),
        ("139.0b0", "139.0b0", 0),
        ("139.0b1", "139.0b0", 1),
        ("139.0b0", "139.0b1", -1),
        ("139.0b1", "139.1", -1),
        ("139.2", "139.0b1", 2),
    ),
)
def test_ios_version_ordering(version, other, expected_result):
    version = MobileIosVersion.parse(version)
    other = MobileIosVersion.parse(other)

    assert version._compare(other) == expected_result


@pytest.mark.parametrize(
    "version,should_raise",
    (
        ("139.0", False),
        ("139.0.0", True),
        ("139.0.1", False),
        ("139.0.1b1", True),
        ("139.0.0b1", True),
        ("139.0b1", False),
    ),
)
def test_ios_validation(version, should_raise):
    if should_raise:
        with pytest.raises(PatternNotMatchedError):
            MobileIosVersion.parse(version)
    else:
        version_obj = MobileIosVersion.parse(version)
        assert version_obj is not None
