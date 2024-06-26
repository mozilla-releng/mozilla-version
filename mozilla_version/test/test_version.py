from distutils.version import LooseVersion, StrictVersion

import pytest

from mozilla_version.errors import PatternNotMatchedError
from mozilla_version.version import BaseVersion, VersionType


@pytest.mark.parametrize(
    "major_number, minor_number, patch_number, expected_output_string",
    ((32, 0, None, "32.0"), (32, 0, 1, "32.0.1")),
)
def test_base_version_constructor_and_str(
    major_number, minor_number, patch_number, expected_output_string
):
    assert (
        str(
            BaseVersion(
                major_number=major_number,
                minor_number=minor_number,
                patch_number=patch_number,
            )
        )
        == expected_output_string
    )


@pytest.mark.parametrize(
    "major_number, minor_number, patch_number, expected_error_type",
    (
        (-1, 0, None, ValueError),
        (32, -1, None, ValueError),
        (32, 0, -1, ValueError),
        (2.2, 0, 0, ValueError),
        ("some string", 0, 0, ValueError),
    ),
)
def test_fail_base_version_constructor(
    major_number, minor_number, patch_number, expected_error_type
):
    with pytest.raises(expected_error_type):
        BaseVersion(
            major_number=major_number,
            minor_number=minor_number,
            patch_number=patch_number,
        )


def test_base_version_constructor_minimum_kwargs():
    assert str(BaseVersion(32, 0)) == "32.0"
    assert str(BaseVersion(32, 0, 1)) == "32.0.1"
    assert str(BaseVersion(32, 1, 0)) == "32.1.0"


@pytest.mark.parametrize(
    "version_string, expected_error_type",
    (
        ("32", PatternNotMatchedError),
        (".1", PatternNotMatchedError),
    ),
)
def test_base_version_raises_when_invalid_version_is_given(
    version_string, expected_error_type
):
    with pytest.raises(expected_error_type):
        BaseVersion.parse(version_string)


@pytest.mark.parametrize(
    "previous_version, next_version",
    (
        ("32.0", "33.0"),
        ("32.0", "32.1.0"),
        ("32.0", "32.0.1"),
        ("32.0.1", "33.0"),
        ("32.0.1", "32.1.0"),
        ("32.0.1", "32.0.2"),
        ("32.1.0", "33.0"),
        ("32.1.0", "32.2.0"),
        ("32.1.0", "32.1.1"),
        ("2.0", "10.0"),
        ("10.2.0", "10.10.0"),
        ("10.0.2", "10.0.10"),
        ("10.10.1", "10.10.10"),
    ),
)
def test_base_version_implements_lt_operator(previous_version, next_version):
    assert BaseVersion.parse(previous_version) < BaseVersion.parse(next_version)


@pytest.mark.parametrize("equivalent_version_string", ("32.0", "032.0", "32.00"))
def test_base_version_implements_eq_operator(equivalent_version_string):
    assert BaseVersion.parse("32.0") == BaseVersion.parse(equivalent_version_string)
    # raw strings are also converted
    assert BaseVersion.parse("32.0") == equivalent_version_string


@pytest.mark.parametrize(
    "wrong_type",
    (
        32,
        32.0,
        ("32", "0", "1"),
        ["32", "0", "1"],
        LooseVersion("32.0"),
        StrictVersion("32.0"),
    ),
)
def test_base_version_raises_eq_operator(wrong_type):
    with pytest.raises(ValueError):
        assert BaseVersion.parse("32.0") == wrong_type
    # AttributeError is raised by LooseVersion and StrictVersion
    with pytest.raises((ValueError, AttributeError)):
        assert wrong_type == BaseVersion.parse("32.0")


def test_base_version_implements_remaining_comparision_operators():
    assert BaseVersion.parse("32.0") <= BaseVersion.parse("32.0")
    assert BaseVersion.parse("32.0") <= BaseVersion.parse("33.0")

    assert BaseVersion.parse("33.0") >= BaseVersion.parse("32.0")
    assert BaseVersion.parse("33.0") >= BaseVersion.parse("33.0")

    assert BaseVersion.parse("33.0") > BaseVersion.parse("32.0")
    assert not BaseVersion.parse("33.0") > BaseVersion.parse("33.0")

    assert not BaseVersion.parse("32.0") < BaseVersion.parse("32.0")

    assert BaseVersion.parse("33.0") != BaseVersion.parse("32.0")


def test_base_version_hashable():
    hash(BaseVersion.parse("63.0"))


class _DummyVersion:
    def __init__(self, major_number):
        self.major_number = major_number


@pytest.mark.parametrize(
    "base_version, other, field, expected",
    (
        (
            BaseVersion(32, 0),
            BaseVersion(32, 0),
            "major_number",
            0,
        ),
        (
            BaseVersion(32, 0),
            BaseVersion(33, 0),
            "major_number",
            -1,
        ),
        (
            BaseVersion(32, 0),
            BaseVersion(31, 0),
            "major_number",
            1,
        ),
        (
            BaseVersion(32, 0),
            BaseVersion(32, 0, 1),
            "patch_number",
            -1,
        ),
        (
            BaseVersion(32, 0),
            _DummyVersion(32),
            "major_number",
            0,
        ),
        (
            BaseVersion(32, 0, 1),
            _DummyVersion(
                32
            ),  # No patch_number so we make sure AttributeError is raised
            "patch_number",
            1,
        ),
    ),
)
def test_base_version_substract_other_number_from_this_number(
    base_version, other, field, expected
):
    assert (
        base_version._substract_other_number_from_this_number(other, field) == expected
    )


@pytest.mark.parametrize(
    "version_string, field, expected",
    (
        ("0.9", "major_number", "1.0"),
        ("0.9.1", "major_number", "1.0.0"),
        ("32.0", "major_number", "33.0"),
        ("32.0.1", "major_number", "33.0.0"),
        ("32.0", "minor_number", "32.1.0"),
        ("32.0.1", "minor_number", "32.1.0"),
        ("32.0", "patch_number", "32.0.1"),
        ("32.0.1", "patch_number", "32.0.2"),
    ),
)
def test_base_version_bump(version_string, field, expected):
    version = BaseVersion.parse(version_string)
    assert str(version.bump(field)) == expected


def test_base_version_bump_raises():
    version = BaseVersion.parse("32.0")
    with pytest.raises(ValueError):
        version.bump("non_existing_number")


@pytest.mark.parametrize(
    "previous_version, next_version",
    (
        (VersionType.NIGHTLY, VersionType.AURORA_OR_DEVEDITION),
        (VersionType.NIGHTLY, VersionType.BETA),
        (VersionType.NIGHTLY, VersionType.RELEASE_CANDIDATE),
        (VersionType.NIGHTLY, VersionType.RELEASE),
        (VersionType.NIGHTLY, VersionType.ESR),
        (VersionType.AURORA_OR_DEVEDITION, VersionType.BETA),
        (VersionType.AURORA_OR_DEVEDITION, VersionType.RELEASE_CANDIDATE),
        (VersionType.AURORA_OR_DEVEDITION, VersionType.RELEASE),
        (VersionType.AURORA_OR_DEVEDITION, VersionType.ESR),
        (VersionType.BETA, VersionType.RELEASE_CANDIDATE),
        (VersionType.BETA, VersionType.RELEASE),
        (VersionType.BETA, VersionType.ESR),
        (VersionType.RELEASE_CANDIDATE, VersionType.RELEASE),
        (VersionType.RELEASE_CANDIDATE, VersionType.ESR),
        (VersionType.RELEASE, VersionType.ESR),
    ),
)
def test_version_type_implements_lt_operator(previous_version, next_version):
    assert previous_version < next_version


@pytest.mark.parametrize(
    "first, second",
    (
        (VersionType.NIGHTLY, VersionType.NIGHTLY),
        (VersionType.AURORA_OR_DEVEDITION, VersionType.AURORA_OR_DEVEDITION),
        (VersionType.BETA, VersionType.BETA),
        (VersionType.RELEASE, VersionType.RELEASE),
        (VersionType.RELEASE_CANDIDATE, VersionType.RELEASE_CANDIDATE),
        (VersionType.ESR, VersionType.ESR),
    ),
)
def test_version_type_implements_eq_operator(first, second):
    assert first == second


def test_version_type_implements_remaining_comparision_operators():
    assert VersionType.NIGHTLY <= VersionType.NIGHTLY
    assert VersionType.NIGHTLY <= VersionType.BETA

    assert VersionType.NIGHTLY >= VersionType.NIGHTLY
    assert VersionType.BETA >= VersionType.NIGHTLY

    assert not VersionType.NIGHTLY > VersionType.NIGHTLY
    assert VersionType.BETA > VersionType.NIGHTLY

    assert not VersionType.BETA < VersionType.NIGHTLY

    assert VersionType.NIGHTLY != VersionType.BETA


def test_version_type_compare():
    assert VersionType.NIGHTLY.compare(VersionType.NIGHTLY) == 0
    assert VersionType.NIGHTLY.compare(VersionType.BETA) < 0
    assert VersionType.BETA.compare(VersionType.NIGHTLY) > 0
