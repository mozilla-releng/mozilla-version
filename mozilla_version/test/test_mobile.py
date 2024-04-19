import re
from distutils.version import LooseVersion, StrictVersion

import pytest

import mozilla_version.gecko
from mozilla_version.errors import (
    NoVersionTypeError,
    PatternNotMatchedError,
    TooManyTypesError,
)
from mozilla_version.mobile import MobileVersion

VALID_VERSIONS = {
    "0.3.0-rc.1": "release_candidate",
    "1.0.0": "release",
    "1.0.0-rc.1": "release_candidate",
    "1.0.0-rc.2": "release_candidate",
    "1.0.1": "release",
    "1.0.1-rc.1": "release_candidate",
    "1.1.0": "release",
    "1.1.0-rc.1": "release_candidate",
    "1.1.0-rc.2": "release_candidate",
    "1.2.0": "release",
    "1.2.0-rc.1": "release_candidate",
    "1.2.0-rc.2": "release_candidate",
    "1.3.0": "release",
    "1.3.0-rc.1": "release_candidate",
    "1.3.0-rc.2": "release_candidate",
    "1.3.0-rc.3": "release_candidate",
    "2.2.0-rc.1": "release_candidate",
    "3.0.0-beta.2": "beta",
    "3.0.0-beta.3": "beta",
    "3.0.0": "release",
    "104.0a1": "nightly",
    "104.0b2": "beta",
    "104.0": "release",
    "104.0.0": "release",
    "104.0.1": "release",
    "109.0": "release",
}


@pytest.mark.parametrize(
    "major_number, minor_number, patch_number, beta_number, rc_number, \
expected_output_string",
    (
        (3, 0, 0, None, None, "3.0.0"),
        (3, 0, 1, None, None, "3.0.1"),
        (3, 0, 0, 3, None, "3.0.0-beta.3"),
        (103, 0, 0, 3, None, "103.0.0-beta.3"),
        (104, 0, None, 3, None, "104.0b3"),
        (3, 0, 0, None, 3, "3.0.0-rc.3"),
    ),
)
def test_mobile_version_constructor_and_str(
    major_number,
    minor_number,
    patch_number,
    beta_number,
    rc_number,
    expected_output_string,
):
    assert (
        str(
            MobileVersion(
                major_number=major_number,
                minor_number=minor_number,
                patch_number=patch_number,
                beta_number=beta_number,
                release_candidate_number=rc_number,
            )
        )
        == expected_output_string
    )


@pytest.mark.parametrize(
    "major_number, minor_number, patch_number, beta_number, rc_number, \
expected_error_type",
    (
        (3, 0, 0, 1, 1, TooManyTypesError),
        (3, 0, 0, 0, None, ValueError),
        (3, 0, None, None, None, PatternNotMatchedError),
        (3, 0, 0, None, 0, ValueError),
        (-1, 0, 0, None, None, ValueError),
        (3, -1, 0, None, None, ValueError),
        (3, 0, -1, None, None, ValueError),
        (2.2, 0, 0, None, None, ValueError),
        ("some string", 0, 0, None, None, ValueError),
    ),
)
def test_fail_mobile_version_constructor(
    major_number,
    minor_number,
    patch_number,
    beta_number,
    rc_number,
    expected_error_type,
):
    with pytest.raises(expected_error_type):
        MobileVersion(
            major_number=major_number,
            minor_number=minor_number,
            patch_number=patch_number,
            beta_number=beta_number,
            release_candidate_number=rc_number,
        )


def test_mobile_version_constructor_minimum_kwargs():
    assert str(MobileVersion(3, 0, 1)) == "3.0.1"
    assert str(MobileVersion(3, 1, 0)) == "3.1.0"
    assert str(MobileVersion(3, 0, 0, beta_number=1)) == "3.0.0-beta.1"

    assert str(MobileVersion(1, 0, 0, release_candidate_number=1)) == "1.0.0-rc.1"


@pytest.mark.parametrize(
    "version_string, expected_error_type",
    (
        ("1.0.0b1", PatternNotMatchedError),
        ("1.0.0.0b1", ValueError),
        ("1.0.0.1b1", PatternNotMatchedError),
        ("1.0.0rc1", PatternNotMatchedError),
        ("1.0.0.0rc1", ValueError),
        ("1.0.0.1rc1", PatternNotMatchedError),
        ("1.5.0.0rc1", ValueError),
        ("1.5.0.1rc1", PatternNotMatchedError),
        ("1.5.1.1", PatternNotMatchedError),
        ("3.1.0b1", PatternNotMatchedError),
        ("31.0b2esr", PatternNotMatchedError),
        ("31.0esrb2", PatternNotMatchedError),
        ("32", PatternNotMatchedError),
        ("32.b2", PatternNotMatchedError),
        (".1", PatternNotMatchedError),
        ("32.0a0", ValueError),
        ("32.0b0", ValueError),
        ("32.0.1a1", PatternNotMatchedError),
        ("32.0.1a2", PatternNotMatchedError),
        ("32.0.1b2", PatternNotMatchedError),
        ("32.0build0", ValueError),
        ("32.0a1a2", PatternNotMatchedError),
        ("32.0a1b2", PatternNotMatchedError),
        ("55.0a2", PatternNotMatchedError),
        ("56.0a2", PatternNotMatchedError),
        ("104.0a2", PatternNotMatchedError),
        ("104.0.0-beta.1", PatternNotMatchedError),
        ("104.0-beta.1", PatternNotMatchedError),
        ("104.0.0-rc.1", PatternNotMatchedError),
        ("104.1", PatternNotMatchedError),
        ("109.0.0", PatternNotMatchedError),
    ),
)
def test_mobile_version_raises_when_invalid_version_is_given(
    version_string, expected_error_type
):
    with pytest.raises(expected_error_type):
        MobileVersion.parse(version_string)


@pytest.mark.parametrize("version_string, expected_type", VALID_VERSIONS.items())
def test_mobile_version_is_of_a_defined_type(version_string, expected_type):
    release = MobileVersion.parse(version_string)
    assert getattr(release, f"is_{expected_type}")


@pytest.mark.parametrize(
    "previous, next",
    (
        ("2.0.0", "3.0.0"),
        ("2.0.0", "3.1.0"),
        ("2.0.0", "3.0.1"),
        ("2.0.1", "3.0.0"),
        ("2.0.1", "2.1.0"),
        ("2.0.1", "2.0.2"),
        ("2.1.0", "3.0.0"),
        ("2.1.0", "2.2.0"),
        ("2.1.0", "2.1.1"),
        ("2.0.0-beta.1", "3.0.0-beta.1"),
        ("2.0.0-beta.1", "2.0.0-beta.2"),
        ("2.0.0-beta.1", "2.0.0"),
        ("1.0.0-rc.1", "1.0.0-rc.2"),
        ("1.0.0-rc.1", "1.0.0"),
        ("3.5.0-beta.4", "3.5.0-rc.2"),
        ("3.5.0-beta.4", "3.5.0"),
        ("3.5.0-rc.2", "3.5.0"),
        ("3.5.0-rc.2", "3.5.0-rc.3"),
    ),
)
def test_mobile_version_implements_lt_operator(previous, next):
    assert MobileVersion.parse(previous) < MobileVersion.parse(next)


@pytest.mark.parametrize(
    "equivalent_version_string",
    (
        "3.00.0",
        "03.0.0",
        "3.0.0",
    ),
)
def test_mobile_version_implements_eq_operator(equivalent_version_string):
    assert MobileVersion.parse("3.0.0") == MobileVersion.parse(
        equivalent_version_string
    )
    # raw strings are also converted
    assert MobileVersion.parse("3.0.0") == equivalent_version_string


@pytest.mark.parametrize(
    "equivalent_version_string",
    (
        "3.00.0-beta.1",
        "03.0.0-beta.1",
        "3.0.0-beta.1",
    ),
)
def test_mobile_beta_version_implements_eq_operator(equivalent_version_string):
    assert MobileVersion.parse("3.0.0-beta.1") == MobileVersion.parse(
        equivalent_version_string
    )
    # raw strings are also converted
    assert MobileVersion.parse("3.0.0-beta.1") == equivalent_version_string


@pytest.mark.parametrize(
    "equivalent_version_string",
    (
        "3.00.0-rc.1",
        "03.0.0-rc.1",
        "3.0.0-rc.01",
    ),
)
def test_mobile_rc_version_implements_eq_operator(equivalent_version_string):
    assert MobileVersion.parse("3.0.0-rc.1") == MobileVersion.parse(
        equivalent_version_string
    )
    # raw strings are also converted
    assert MobileVersion.parse("3.0.0-rc.1") == equivalent_version_string


@pytest.mark.parametrize(
    "wrong_type",
    (
        3,
        3.0,
        ("3", "0", "1"),
        ["3", "0", "1"],
        LooseVersion("3.0.0"),
        StrictVersion("3.0.0"),
    ),
)
def test_mobile_version_raises_eq_operator(wrong_type):
    with pytest.raises(ValueError):
        assert MobileVersion.parse("3.0.0") == wrong_type
    # AttributeError is raised by LooseVersion and StrictVersion
    with pytest.raises((ValueError, AttributeError)):
        assert wrong_type == MobileVersion.parse("3.0.0")


def test_mobile_version_implements_remaining_comparision_operators():
    assert MobileVersion.parse("2.0.0") <= MobileVersion.parse("2.0.0")
    assert MobileVersion.parse("2.0.0") <= MobileVersion.parse("3.0.0")

    assert MobileVersion.parse("3.0.0") >= MobileVersion.parse("2.0.0")
    assert MobileVersion.parse("3.0.0") >= MobileVersion.parse("3.0.0")

    assert MobileVersion.parse("3.0.0") > MobileVersion.parse("2.0.0")
    assert not MobileVersion.parse("3.0.0") > MobileVersion.parse("3.0.0")

    assert not MobileVersion.parse("2.0.0") < MobileVersion.parse("2.0.0")

    assert MobileVersion.parse("3.0.0") != MobileVersion.parse("2.0.0")


@pytest.mark.parametrize(
    "version_string, expected_output",
    (
        ("2.0.0", "2.0.0"),
        ("02.0.0", "2.0.0"),
        ("2.0.1", "2.0.1"),
        ("2.0.0-rc.1", "2.0.0-rc.1"),
        ("2.0.0-rc.2", "2.0.0-rc.2"),
        ("2.0.0-rc.02", "2.0.0-rc.2"),
        ("2.0.0-beta.1", "2.0.0-beta.1"),
        ("2.0.0-beta.01", "2.0.0-beta.1"),
        ("104.0", "104.0"),
        ("0104.0", "104.0"),
        ("104.0build1", "104.0build1"),
        ("104.0build01", "104.0build1"),
        ("104.0.1", "104.0.1"),
        ("104.0a1", "104.0a1"),
        ("104.0b1", "104.0b1"),
        ("104.0b01", "104.0b1"),
    ),
)
def test_mobile_version_implements_str_operator(version_string, expected_output):
    assert str(MobileVersion.parse(version_string)) == expected_output


@pytest.mark.parametrize(
    "version_string, field, expected",
    (
        ("0.9.0", "major_number", "1.0.0"),
        ("0.9.1", "major_number", "1.0.0"),
        ("1.0.0-beta.1", "beta_number", "1.0.0-beta.2"),
        ("1.0.0-rc.1", "release_candidate_number", "1.0.0-rc.2"),
        ("1.0.0", "patch_number", "1.0.1"),
        ("1.5.0", "minor_number", "1.6.0"),
        ("1.5.1", "minor_number", "1.6.0"),
        ("2.0.0-rc.1", "release_candidate_number", "2.0.0-rc.2"),
        ("2.0.0", "major_number", "3.0.0"),
        ("2.0.1", "major_number", "3.0.0"),
        ("2.0.0-rc.2", "major_number", "3.0.0"),
        ("2.0.0-beta.1", "major_number", "3.0.0-beta.1"),
        ("2.0.0", "major_number", "3.0.0"),
        ("2.0.1", "major_number", "3.0.0"),
        ("2.0.0", "minor_number", "2.1.0"),
        ("2.0.1", "minor_number", "2.1.0"),
        ("2.0.0", "patch_number", "2.0.1"),
        ("2.0.1", "patch_number", "2.0.2"),
        ("2.0.0-beta.1", "beta_number", "2.0.0-beta.2"),
        ("103.0.0-beta.1", "major_number", "104.0b1"),
        ("103.0.0-rc.2", "major_number", "104.0"),
        ("103.0.0", "major_number", "104.0"),
        ("104.0a1", "major_number", "105.0a1"),
        ("104.0b2", "major_number", "105.0b1"),
        ("104.0", "major_number", "105.0"),
        ("104.0", "minor_number", "104.1.0"),
        ("104.0.1", "minor_number", "104.1.0"),
        ("104.0", "patch_number", "104.0.1"),
        ("104.0.1", "patch_number", "104.0.2"),
        ("104.0b1", "beta_number", "104.0b2"),
        ("104.0build1", "build_number", "104.0build2"),
        ("104.0b1build1", "build_number", "104.0b1build2"),
    ),
)
def test_mobile_version_bump(version_string, field, expected):
    version = MobileVersion.parse(version_string)
    assert str(version.bump(field)) == expected


@pytest.mark.parametrize(
    "version_string, field", (("2.0.0-beta.1", "release_candidate_number"),)
)
def test_mobile_version_bump_raises(version_string, field):
    version = MobileVersion.parse(version_string)
    with pytest.raises(ValueError):
        version.bump(field)


_SUPER_PERMISSIVE_PATTERN = re.compile(
    r"""
^(?P<major_number>\d+)\.(?P<minor_number>\d+)(\.(?P<patch_number>\d+))?
(-beta\.(?P<beta_number>\d+))?(-rc\.(?P<release_candidate_number>\d+))?
""",
    re.VERBOSE,
)


@pytest.mark.parametrize("version_string", ("2.0.0-beta.1-rc.2",))
def test_mobile_version_ensures_it_does_not_have_multiple_type(
    monkeypatch, version_string
):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = MobileVersion._VALID_ENOUGH_VERSION_PATTERN
    MobileVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    with pytest.raises(TooManyTypesError):
        MobileVersion.parse(version_string)

    MobileVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern


def test_mobile_version_ensures_a_new_added_release_type_is_caught(monkeypatch):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = MobileVersion._VALID_ENOUGH_VERSION_PATTERN
    MobileVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    # And a broken type detection
    original_is_release = MobileVersion.is_release
    MobileVersion.is_release = False

    with pytest.raises(NoVersionTypeError):
        mozilla_version.mobile.MobileVersion.parse("2.0.0")

    MobileVersion.is_release = original_is_release
    MobileVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern
