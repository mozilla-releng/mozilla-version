import pytest
import re

import mozilla_version.firefox

from mozilla_version.errors import InvalidVersionError, TooManyTypesError, NoVersionTypeError
from mozilla_version.firefox import FirefoxVersion


VALID_VERSIONS = {
    '32.0a1': 'nightly',
    '32.0a2': 'aurora_or_devedition',
    '32.0b2': 'beta',
    '32.0b10': 'beta',
    '32.0': 'release',
    '32.0.1': 'release',
    '32.0esr': 'esr',
    '32.0.1esr': 'esr',
}


@pytest.mark.parametrize('major_number, minor_number, patch_number, beta_number, build_number, is_nightly, is_aurora_or_devedition, is_esr, expected_output_string', ((
    32, 0, None, None, None, False, False, False, '32.0'
), (
    32, 0, 1, None, None, False, False, False, '32.0.1'
), (
    32, 0, None, 3, None, False, False, False, '32.0b3'
), (
    32, 0, None, None, 10, False, False, False, '32.0build10'
), (
    32, 0, None, None, None, True, False, False, '32.0a1'
), (
    32, 0, None, None, None, False, True, False, '32.0a2'
), (
    32, 0, None, None, None, False, False, True, '32.0esr'
), (
    32, 0, 1, None, None, False, False, True, '32.0.1esr'
)))
def test_firefox_version_constructor_and_str(major_number, minor_number, patch_number, beta_number, build_number, is_nightly, is_aurora_or_devedition, is_esr, expected_output_string):
    assert str(FirefoxVersion(
        major_number=major_number,
        minor_number=minor_number,
        patch_number=patch_number,
        beta_number=beta_number,
        build_number=build_number,
        is_nightly=is_nightly,
        is_aurora_or_devedition=is_aurora_or_devedition,
        is_esr=is_esr
    )) == expected_output_string


@pytest.mark.parametrize('major_number, minor_number, patch_number, beta_number, build_number, is_nightly, is_aurora_or_devedition, is_esr, ExpectedErrorType', ((
    32, 0, None, 1, None, True, False, False, TooManyTypesError
), (
    32, 0, None, 1, None, False, True, False, TooManyTypesError
), (
    32, 0, None, 1, None, False, False, True, TooManyTypesError
), (
    32, 0, None, None, None, True, True, False, TooManyTypesError
), (
    32, 0, None, None, None, True, False, True, TooManyTypesError
), (
    32, 0, None, None, None, False, True, True, TooManyTypesError
), (
    32, 0, None, None, None, True, True, True, TooManyTypesError
), (
    32, 0, 0, None, None, False, False, False, InvalidVersionError
), (
    32, 0, None, 0, None, False, False, False, ValueError
), (
    32, 0, None, None, 0, False, False, False, ValueError
), (
    32, 0, 1, 1, None, False, False, False, InvalidVersionError
), (
    32, 0, 1, None, None, True, False, False, InvalidVersionError
), (
    32, 0, 1, None, None, False, True, False, InvalidVersionError
)))
def test_fail_firefox_version_constructor(major_number, minor_number, patch_number, beta_number, build_number, is_nightly, is_aurora_or_devedition, is_esr, ExpectedErrorType):
    with pytest.raises(ExpectedErrorType):
        FirefoxVersion(
            major_number=major_number,
            minor_number=minor_number,
            patch_number=patch_number,
            beta_number=beta_number,
            build_number=build_number,
            is_nightly=is_nightly,
            is_aurora_or_devedition=is_aurora_or_devedition,
            is_esr=is_esr
        )


@pytest.mark.parametrize('version_string', (
    '32', '32.b2', '.1', '32.2', '32.02', '32.0a1a2', '32.0a1b2', '32.0b2esr', '32.0esrb2',
))
def test_firefox_version_raises_when_invalid_version_is_given(version_string):
    with pytest.raises(InvalidVersionError):
        FirefoxVersion.parse(version_string)


@pytest.mark.parametrize('version_string, expected_type', VALID_VERSIONS.items())
def test_firefox_version_is_of_a_defined_type(version_string, expected_type):
    release = FirefoxVersion.parse(version_string)
    assert getattr(release, 'is_{}'.format(expected_type))


@pytest.mark.parametrize('previous, next', (
    ('32.0', '33.0'),
    ('32.0', '32.1.0'),
    ('32.0', '32.0.1'),
    ('32.0build1', '32.0build2'),

    ('32.0a1', '32.0'),
    ('32.0a2', '32.0'),
    ('32.0b1', '32.0'),

    ('32.0.1', '33.0'),
    ('32.0.1', '32.1.0'),
    ('32.0.1', '32.0.2'),
    ('32.0.1build1', '32.0.1build2'),

    ('32.1.0', '33.0'),
    ('32.1.0', '32.2.0'),
    ('32.1.0', '32.1.1'),
    ('32.1.0build1', '32.1.0build2'),

    ('32.0b1', '33.0b1'),
    ('32.0b1', '32.0b2'),
    ('32.0b1build1', '32.0b1build2'),

    ('2.0', '10.0'),
    ('10.2.0', '10.10.0'),
    ('10.0.2', '10.0.10'),
    ('10.10.1', '10.10.10'),
    ('10.0build2', '10.0build10'),
    ('10.0b2', '10.0b10'),
))
def test_firefox_version_implements_lt_operator(previous, next):
    assert FirefoxVersion.parse(previous) < FirefoxVersion.parse(next)


@pytest.mark.parametrize('equivalent_version_string', (
    '32.0', '032.0', '32.0build1', '32.0build01', '32.0build2', '32.0esr',
))
def test_firefox_version_implements_eq_operator(equivalent_version_string):
    assert FirefoxVersion.parse('32.0') == FirefoxVersion.parse(equivalent_version_string)


def test_firefox_version_implements_remaining_comparision_operators():
    assert FirefoxVersion.parse('32.0') <= FirefoxVersion.parse('32.0')
    assert FirefoxVersion.parse('32.0') <= FirefoxVersion.parse('33.0')

    assert FirefoxVersion.parse('33.0') >= FirefoxVersion.parse('32.0')
    assert FirefoxVersion.parse('33.0') >= FirefoxVersion.parse('33.0')

    assert FirefoxVersion.parse('33.0') > FirefoxVersion.parse('32.0')
    assert not FirefoxVersion.parse('33.0') > FirefoxVersion.parse('33.0')

    assert not FirefoxVersion.parse('32.0') < FirefoxVersion.parse('32.0')

    assert FirefoxVersion.parse('33.0') != FirefoxVersion.parse('32.0')


@pytest.mark.parametrize('version_string, expected_output', (
    ('32.0', '32.0'),
    ('032.0', '32.0'),
    ('32.0build1', '32.0build1'),
    ('32.0build01', '32.0build1'),
    ('32.0.1', '32.0.1'),
    ('32.0a1', '32.0a1'),
    ('32.0a2', '32.0a2'),
    ('32.0b1', '32.0b1'),
    ('32.0b01', '32.0b1'),
    ('32.0esr', '32.0esr'),
    ('32.0.1esr', '32.0.1esr'),
))
def test_firefox_version_implements_str_operator(version_string, expected_output):
    assert str(FirefoxVersion.parse(version_string)) == expected_output


_SUPER_PERMISSIVE_PATTERN = re.compile(r"""
(?P<major_number>\d+)\.(?P<zero_minor_number>\d+)(\.(\d+))*
(?P<is_nightly>a1)?(?P<is_aurora_or_devedition>a2)?(b(?P<beta_number>\d+))?
(?P<is_two_digit_esr>esr)?(?P<is_three_digit_esr>esr)?
""", re.VERBOSE)


@pytest.mark.parametrize('version_string', (
    '32.0a1a2', '32.0a1b2', '32.0b2esr'
))
def test_firefox_version_ensures_it_does_not_have_multiple_type(monkeypatch, version_string):
    # Let's make sure the sanity checks detect a broken regular expression
    monkeypatch.setattr(
        mozilla_version.firefox, '_VALID_VERSION_PATTERN', _SUPER_PERMISSIVE_PATTERN
    )

    with pytest.raises(TooManyTypesError):
        FirefoxVersion.parse(version_string)


def test_firefox_version_ensures_a_new_added_release_type_is_caught(monkeypatch):
    # Let's make sure the sanity checks detect a broken regular expression
    monkeypatch.setattr(
        mozilla_version.firefox, '_VALID_VERSION_PATTERN', _SUPER_PERMISSIVE_PATTERN
    )
    # And a broken type detection
    FirefoxVersion.is_release = False

    with pytest.raises(NoVersionTypeError):
        mozilla_version.firefox.FirefoxVersion.parse('32.0.0.0')
