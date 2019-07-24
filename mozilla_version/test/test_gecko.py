import pytest
import re

from distutils.version import StrictVersion, LooseVersion

import mozilla_version.gecko

from mozilla_version.errors import PatternNotMatchedError, TooManyTypesError, NoVersionTypeError
from mozilla_version.gecko import (
    GeckoVersion, FirefoxVersion, DeveditionVersion,
    ThunderbirdVersion, FennecVersion, GeckoSnapVersion,
)
from mozilla_version.test import does_not_raise


VALID_VERSIONS = {
    '32.0a1': 'nightly',
    '32.0a2': 'aurora_or_devedition',
    '32.0b2': 'beta',
    '32.0b10': 'beta',
    '32.0': 'release',
    '32.0.1': 'release',
    '32.0esr': 'esr',
    '32.0.1esr': 'esr',

    '1.0rc1': 'release_candidate',
    '1.0': 'release',
    '1.5': 'release',
    '1.5.0.1': 'release',
    '3.1b1': 'beta',
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
    32, 0, 0, None, None, False, False, False, PatternNotMatchedError
), (
    32, 0, None, 0, None, False, False, False, ValueError
), (
    32, 0, None, None, 0, False, False, False, ValueError
), (
    32, 0, 1, 1, None, False, False, False, PatternNotMatchedError
), (
    32, 0, 1, None, None, True, False, False, PatternNotMatchedError
), (
    32, 0, 1, None, None, False, True, False, PatternNotMatchedError
), (
    -1, 0, None, None, None, False, False, False, ValueError
), (
    32, -1, None, None, None, False, False, False, ValueError
), (
    32, 0, -1, None, None, False, False, False, ValueError
), (
    2.2, 0, 0, None, None, False, False, False, ValueError
), (
    'some string', 0, 0, None, None, False, False, False, ValueError
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


def test_firefox_version_constructor_minimum_kwargs():
    assert str(FirefoxVersion(32, 0)) == '32.0'
    assert str(FirefoxVersion(32, 0, 1)) == '32.0.1'
    assert str(FirefoxVersion(32, 1, 0)) == '32.1.0'
    assert str(FirefoxVersion(32, 0, 1, 1)) == '32.0.1build1'
    assert str(FirefoxVersion(32, 0, beta_number=1)) == '32.0b1'
    assert str(FirefoxVersion(32, 0, is_nightly=True)) == '32.0a1'
    assert str(FirefoxVersion(32, 0, is_aurora_or_devedition=True)) == '32.0a2'
    assert str(FirefoxVersion(32, 0, is_esr=True)) == '32.0esr'
    assert str(FirefoxVersion(32, 0, 1, is_esr=True)) == '32.0.1esr'

    assert str(FirefoxVersion(1, 0, release_candidate_number=1)) == '1.0rc1'
    assert str(FirefoxVersion(1, 5, 0, old_fourth_number=1)) == '1.5.0.1'


@pytest.mark.parametrize('version_string, ExpectedErrorType', (
    ('32', PatternNotMatchedError),
    ('32.b2', PatternNotMatchedError),
    ('.1', PatternNotMatchedError),
    ('32.0.0', PatternNotMatchedError),
    ('32.2', PatternNotMatchedError),
    ('32.02', PatternNotMatchedError),
    ('32.0a0', ValueError),
    ('32.0b0', ValueError),
    ('32.0.1a1', PatternNotMatchedError),
    ('32.0.1a2', PatternNotMatchedError),
    ('32.0.1b2', PatternNotMatchedError),
    ('32.0build0', ValueError),
    ('32.0a1a2', PatternNotMatchedError),
    ('32.0a1b2', PatternNotMatchedError),
    ('32.0b2esr', PatternNotMatchedError),
    ('32.0esrb2', PatternNotMatchedError),

    ('1.0.0b1', PatternNotMatchedError),
    ('1.0.0.0b1', ValueError),
    ('1.0.0.1b1', PatternNotMatchedError),
    ('1.0.0rc1', PatternNotMatchedError),
    ('1.0.0.0rc1', ValueError),
    ('1.0.0.1rc1', PatternNotMatchedError),
    ('1.5.0.0rc1', ValueError),
    ('1.5.0.1rc1', PatternNotMatchedError),
    ('1.5.1.1', PatternNotMatchedError),
    ('3.1.0b1', PatternNotMatchedError),
))
def test_firefox_version_raises_when_invalid_version_is_given(version_string, ExpectedErrorType):
    with pytest.raises(ExpectedErrorType):
        FirefoxVersion.parse(version_string)


def test_firefox_version_raises_multiple_error_messages():
    with pytest.raises(PatternNotMatchedError) as exc_info:
        FirefoxVersion.parse('5.0.0.1rc1')

    assert exc_info.value.args[0] == '''"5.0.0.1rc1" does not match the patterns:
 - The old fourth number cannot be defined starting Gecko 3
 - Release candidate number cannot be defined starting Gecko 5
 - Minor number and patch number cannot be both equal to 0'''


@pytest.mark.parametrize('version_string, expected_type', VALID_VERSIONS.items())
def test_firefox_version_is_of_a_defined_type(version_string, expected_type):
    release = FirefoxVersion.parse(version_string)
    assert getattr(release, 'is_{}'.format(expected_type))


@pytest.mark.parametrize('previous, next', (
    ('32.0', '33.0'),
    ('32.0', '32.1.0'),
    ('32.0', '32.0.1'),
    ('32.0build1', '32.0build2'),

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

    ('32.0a1', '32.0a2'),
    ('32.0a1', '32.0b1'),
    ('32.0a1', '32.0'),
    ('32.0a1', '32.0esr'),

    ('32.0a2', '32.0b1'),
    ('32.0a2', '32.0'),
    ('32.0a2', '32.0esr'),

    ('32.0b1', '32.0'),
    ('32.0b1', '32.0esr'),

    ('32.0', '32.0esr'),

    ('2.0', '10.0'),
    ('10.2.0', '10.10.0'),
    ('10.0.2', '10.0.10'),
    ('10.10.1', '10.10.10'),
    ('10.0build2', '10.0build10'),
    ('10.0b2', '10.0b10'),

    ('1.0rc1', '1.0rc2'),
    ('1.0rc1build1', '1.0rc1build2'),
    ('1.0rc1', '1.0'),
    ('1.5', '1.5.0.1'),
    ('3.5b4', '3.5rc2'),
    ('3.5b4', '3.5'),
    ('3.5rc2', '3.5'),
))
def test_firefox_version_implements_lt_operator(previous, next):
    assert FirefoxVersion.parse(previous) < FirefoxVersion.parse(next)


@pytest.mark.parametrize('equivalent_version_string', (
    '32.0', '032.0', '32.0build1', '32.0build01', '32.0-build1', '32.0build2',
))
def test_firefox_version_implements_eq_operator(equivalent_version_string):
    assert FirefoxVersion.parse('32.0') == FirefoxVersion.parse(equivalent_version_string)
    # raw strings are also converted
    assert FirefoxVersion.parse('32.0') == equivalent_version_string


@pytest.mark.parametrize('wrong_type', (
    32,
    32.0,
    ('32', '0', '1'),
    ['32', '0', '1'],
    LooseVersion('32.0'),
    StrictVersion('32.0'),
))
def test_firefox_version_raises_eq_operator(wrong_type):
    with pytest.raises(ValueError):
        assert FirefoxVersion.parse('32.0') == wrong_type
    # AttributeError is raised by LooseVersion and StrictVersion
    with pytest.raises((ValueError, AttributeError)):
        assert wrong_type == FirefoxVersion.parse('32.0')


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
(?P<major_number>\d+)\.(?P<minor_number>\d+)(\.(\d+))*
(?P<is_nightly>a1)?(?P<is_aurora_or_devedition>a2)?(b(?P<beta_number>\d+))?
(?P<is_esr>esr)?
""", re.VERBOSE)


@pytest.mark.parametrize('version_string', (
    '32.0a1a2', '32.0a1b2', '32.0b2esr'
))
def test_firefox_version_ensures_it_does_not_have_multiple_type(monkeypatch, version_string):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = FirefoxVersion._VALID_ENOUGH_VERSION_PATTERN
    FirefoxVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    with pytest.raises(TooManyTypesError):
        FirefoxVersion.parse(version_string)

    FirefoxVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern


def test_firefox_version_ensures_a_new_added_release_type_is_caught(monkeypatch):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = FirefoxVersion._VALID_ENOUGH_VERSION_PATTERN
    FirefoxVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    # And a broken type detection
    original_is_release = FirefoxVersion.is_release
    FirefoxVersion.is_release = False

    with pytest.raises(NoVersionTypeError):
        mozilla_version.gecko.FirefoxVersion.parse('32.0.0.0')

    FirefoxVersion.is_release = original_is_release
    FirefoxVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern


@pytest.mark.parametrize('version_string', (
    # Firefox released versions
    '1.0rc1', '1.0rc2',
    '1.5', '1.5rc1', '1.5rc2', '1.5rc3',
    '1.5.0.1',
    '1.5.0.10',
    '1.5.0.11',
    '1.5.0.12',
    '1.5.0.2',
    '1.5.0.3',
    '1.5.0.4',
    '1.5.0.5',
    '1.5.0.6',
    '1.5.0.7',
    '1.5.0.8',
    '1.5.0.9',

    '2.0rc1', '2.0rc2', '2.0rc3',
    '2.0.0.1',
    '2.0.0.3',
    '2.0.0.4',
    '2.0.0.5',
    '2.0.0.6',
    '2.0.0.7',
    '2.0.0.8',
    '2.0.0.9',
    '2.0.0.2',
    '2.0.0.10',
    '2.0.0.11',
    '2.0.0.12',
    '2.0.0.13',
    '2.0.0.14',
    '2.0.0.15',
    '2.0.0.16',
    '2.0.0.17',
    '2.0.0.18',
    '2.0.0.19',
    '2.0.0.20',

    '3.0rc1', '3.0rc2',
    '3.1b1',
    '3.1b2',
    '3.1b3',
    '3.5b4',
    '3.5', '3.5rc2', '3.5rc3',
    '3.6', '3.6rc1', '3.6rc2',
    '3.6b1',
    '3.6b2',
    '3.6b3',
    '3.6b4',
    '3.6b5',

    '4.0rc1', '4.0rc2',

    # Thunderbird released versions
    '1.0rc1',
    '1.5b1',
    '1.5b2',
    '1.5', '1.5rc1', '1.5rc2',
    '1.5.0.2',
    '1.5.0.4',
    '1.5.0.5',
    '1.5.0.7',
    '1.5.0.8',
    '1.5.0.9',
    '1.5.0.10',
    '1.5.0.12',
    '1.5.0.13',

    '2.0rc1',
    '2.0.0.4',
    '2.0.0.5',
    '2.0.0.6',
    '2.0.0.9',
    '2.0.0.12',
    '2.0.0.14',
    '2.0.0.16',
    '2.0.0.17',
    '2.0.0.18',
    '2.0.0.19',
    '2.0.0.21',
    '2.0.0.22',
    '2.0.0.23',
    '2.0.0.24',

    '3.0rc1', '3.0rc2',
    '3.1b1',
    '3.1', '3.1rc1', '3.1rc2',

    # Fennec released version
    '1.1b1',
    '1.1', '1.1rc1',

    '4.0rc1',
))
def test_gecko_version_supports_old_schemes(version_string):
    assert str(GeckoVersion.parse(version_string)) == version_string

@pytest.mark.parametrize('version_string', (
    '33.1', '33.1build1', '33.1build2', '33.1build3',
    '38.0.5b1', '38.0.5b1build1', '38.0.5b1build2',
    '38.0.5b2', '38.0.5b2build1',
    '38.0.5b3', '38.0.5b3build1',
))
def test_firefox_version_supports_released_edge_cases(version_string):
    assert str(FirefoxVersion.parse(version_string)) == version_string
    for Class in (DeveditionVersion, FennecVersion, ThunderbirdVersion):
        if Class == FennecVersion and version_string in ('33.1', '33.1build1', '33.1build2'):
            # These edge cases also exist in Fennec
            continue
        with pytest.raises(PatternNotMatchedError):
            Class.parse(version_string)


@pytest.mark.parametrize('version_string', (
    '54.0b11', '54.0b12', '55.0b1'
))
def test_devedition_version(version_string):
    DeveditionVersion.parse(version_string)


@pytest.mark.parametrize('version_string', (
    '53.0a1', '53.0b1', '54.0b10', '55.0', '55.0a1', '60.0esr'
))
def test_devedition_version_bails_on_wrong_version(version_string):
    with pytest.raises(PatternNotMatchedError):
        DeveditionVersion.parse(version_string)


@pytest.mark.parametrize('version_string', (
    '33.1', '33.1build1', '33.1build2',
    '38.0.5b4', '38.0.5b4build1'
))
def test_fennec_version_supports_released_edge_cases(version_string):
    assert str(FennecVersion.parse(version_string)) == version_string
    for Class in (FirefoxVersion, DeveditionVersion, ThunderbirdVersion):
        if Class == FirefoxVersion and version_string in ('33.1', '33.1build1', '33.1build2'):
            # These edge cases also exist in Firefox
            continue
        with pytest.raises(PatternNotMatchedError):
            Class.parse(version_string)


@pytest.mark.parametrize('version_string, expectation', (
    ('68.0a1', does_not_raise()),
    ('68.0b3', does_not_raise()),
    ('68.0b17', does_not_raise()),
    ('68.0', does_not_raise()),
    ('68.0.1', does_not_raise()),
    ('68.1a1', does_not_raise()),
    ('68.1b2', does_not_raise()),
    ('68.1.0', does_not_raise()),
    ('68.1', does_not_raise()),
    ('68.1b3', does_not_raise()),
    ('68.1.1', does_not_raise()),
    ('68.2a1', does_not_raise()),
    ('68.2b1', does_not_raise()),
    ('68.2', does_not_raise()),

    ('67.1', pytest.raises(PatternNotMatchedError)),
    ('68.0.1a1', pytest.raises(PatternNotMatchedError)),
    ('68.1a1b1', pytest.raises(PatternNotMatchedError)),
    ('68.0.1b1', pytest.raises(PatternNotMatchedError)),
    ('68.1.0a1', pytest.raises(PatternNotMatchedError)),
    ('68.1.0b1', pytest.raises(PatternNotMatchedError)),
    ('68.1.1a1', pytest.raises(PatternNotMatchedError)),
    ('68.1.1b2', pytest.raises(PatternNotMatchedError)),

    ('69.0a1', pytest.raises(PatternNotMatchedError)),
    ('69.0b3', pytest.raises(PatternNotMatchedError)),
    ('69.0', pytest.raises(PatternNotMatchedError)),
    ('69.0.1', pytest.raises(PatternNotMatchedError)),
    ('69.1', pytest.raises(PatternNotMatchedError)),

    ('70.0', pytest.raises(PatternNotMatchedError)),
))
def test_fennec_version_ends_at_68(version_string, expectation):
    with expectation:
        FennecVersion.parse(version_string)


@pytest.mark.parametrize('version_string', (
    '45.1b1', '45.1b1build1',
    '45.2', '45.2build1', '45.2build2',
    '45.2b1', '45.2b1build2',
))
def test_thunderbird_version_supports_released_edge_cases(version_string):
    assert str(ThunderbirdVersion.parse(version_string)) == version_string
    for Class in (FirefoxVersion, DeveditionVersion, FennecVersion):
        with pytest.raises(PatternNotMatchedError):
            Class.parse(version_string)


@pytest.mark.parametrize('version_string', (
    '63.0b7-1', '63.0b7-2',
    '62.0-1', '62.0-2',
    '60.2.1esr-1', '60.2.0esr-2',
    '60.0esr-1', '60.0esr-13',
    # TODO Bug 1451694: Figure out what nightlies version numbers looks like
))
def test_gecko_snap_version(version_string):
    GeckoSnapVersion.parse(version_string)


@pytest.mark.parametrize('version_string', (
    '32.0a2', '32.0esr1', '32.0-build1',
))
def test_gecko_snap_version_bails_on_wrong_version(version_string):
    with pytest.raises(PatternNotMatchedError):
        GeckoSnapVersion.parse(version_string)


def test_gecko_snap_version_implements_its_own_string():
    assert str(GeckoSnapVersion.parse('63.0b7-1')) == '63.0b7-1'


def test_gecko_version_hashable():
    """
    It is possible to hash `GeckoVersion`.
    """
    hash(GeckoVersion.parse('63.0'))
