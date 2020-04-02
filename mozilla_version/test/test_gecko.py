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
    '31.0esr': 'esr',
    '31.0.1esr': 'esr',

    '32.0a1': 'nightly',
    '32.0a2': 'aurora_or_devedition',
    '32.0b2': 'beta',
    '32.0b10': 'beta',
    '32.0': 'release',
    '32.0.1': 'release',

    '54.0a2': 'aurora_or_devedition',   # Last Aurora

    '1.0rc1': 'release_candidate',
    '1.0': 'release',
    '1.5': 'release',
    '1.5.0.1': 'release',
    '3.1b1': 'beta',
}


@pytest.mark.parametrize('major_number, minor_number, patch_number, beta_number, build_number, is_nightly, is_aurora_or_devedition, is_esr, expected_output_string', ((
    31, 0, None, None, None, False, False, True, '31.0esr'
), (
    31, 0, 1, None, None, False, False, True, '31.0.1esr'
), (
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
)))
def test_gecko_version_constructor_and_str(major_number, minor_number, patch_number, beta_number, build_number, is_nightly, is_aurora_or_devedition, is_esr, expected_output_string):
    assert str(GeckoVersion(
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
def test_fail_gecko_version_constructor(major_number, minor_number, patch_number, beta_number, build_number, is_nightly, is_aurora_or_devedition, is_esr, ExpectedErrorType):
    with pytest.raises(ExpectedErrorType):
        GeckoVersion(
            major_number=major_number,
            minor_number=minor_number,
            patch_number=patch_number,
            beta_number=beta_number,
            build_number=build_number,
            is_nightly=is_nightly,
            is_aurora_or_devedition=is_aurora_or_devedition,
            is_esr=is_esr
        )


def test_gecko_version_constructor_minimum_kwargs():
    assert str(GeckoVersion(31, 0, is_esr=True)) == '31.0esr'
    assert str(GeckoVersion(31, 0, 1, is_esr=True)) == '31.0.1esr'

    assert str(GeckoVersion(32, 0)) == '32.0'
    assert str(GeckoVersion(32, 0, 1)) == '32.0.1'
    assert str(GeckoVersion(32, 1, 0)) == '32.1.0'
    assert str(GeckoVersion(32, 0, 1, 1)) == '32.0.1build1'
    assert str(GeckoVersion(32, 0, beta_number=1)) == '32.0b1'
    assert str(GeckoVersion(32, 0, is_nightly=True)) == '32.0a1'
    assert str(GeckoVersion(32, 0, is_aurora_or_devedition=True)) == '32.0a2'

    assert str(GeckoVersion(1, 0, release_candidate_number=1)) == '1.0rc1'
    assert str(GeckoVersion(1, 5, 0, old_fourth_number=1)) == '1.5.0.1'


@pytest.mark.parametrize('version_string, ExpectedErrorType', (
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

    ('31.0b2esr', PatternNotMatchedError),
    ('31.0esrb2', PatternNotMatchedError),

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

    ('55.0a2', PatternNotMatchedError),
    ('56.0a2', PatternNotMatchedError),

    # It might be the next ESR number, we don't know this for a fact, yet
    ('76.0esr', PatternNotMatchedError),
))
def test_gecko_version_raises_when_invalid_version_is_given(version_string, ExpectedErrorType):
    with pytest.raises(ExpectedErrorType):
        GeckoVersion.parse(version_string)


def test_gecko_version_raises_multiple_error_messages():
    with pytest.raises(PatternNotMatchedError) as exc_info:
        GeckoVersion.parse('5.0.0.1rc1')

    assert exc_info.value.args[0] == '''"5.0.0.1rc1" does not match the patterns:
 - The old fourth number can only be defined on Gecko 1.5.x.y or 2.0.x.y
 - Release candidate number cannot be defined starting Gecko 5
 - Minor number and patch number cannot be both equal to 0'''


@pytest.mark.parametrize('version_string, expected_type', VALID_VERSIONS.items())
def test_gecko_version_is_of_a_defined_type(version_string, expected_type):
    release = GeckoVersion.parse(version_string)
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

    ('32.0a2', '32.0b1'),
    ('32.0a2', '32.0'),

    ('32.0b1', '32.0'),

    ('31.0a1', '31.0esr'),
    ('31.0a2', '31.0esr'),
    ('31.0b1', '31.0esr'),
    ('31.0', '31.0esr'),

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
def test_gecko_version_implements_lt_operator(previous, next):
    assert GeckoVersion.parse(previous) < GeckoVersion.parse(next)


@pytest.mark.parametrize('equivalent_version_string', (
    '32.0', '032.0', '32.0build1', '32.0build01', '32.0-build1', '32.0build2',
))
def test_gecko_version_implements_eq_operator(equivalent_version_string):
    assert GeckoVersion.parse('32.0') == GeckoVersion.parse(equivalent_version_string)
    # raw strings are also converted
    assert GeckoVersion.parse('32.0') == equivalent_version_string


@pytest.mark.parametrize('wrong_type', (
    32,
    32.0,
    ('32', '0', '1'),
    ['32', '0', '1'],
    LooseVersion('32.0'),
    StrictVersion('32.0'),
))
def test_gecko_version_raises_eq_operator(wrong_type):
    with pytest.raises(ValueError):
        assert GeckoVersion.parse('32.0') == wrong_type
    # AttributeError is raised by LooseVersion and StrictVersion
    with pytest.raises((ValueError, AttributeError)):
        assert wrong_type == GeckoVersion.parse('32.0')


def test_gecko_version_implements_remaining_comparision_operators():
    assert GeckoVersion.parse('32.0') <= GeckoVersion.parse('32.0')
    assert GeckoVersion.parse('32.0') <= GeckoVersion.parse('33.0')

    assert GeckoVersion.parse('33.0') >= GeckoVersion.parse('32.0')
    assert GeckoVersion.parse('33.0') >= GeckoVersion.parse('33.0')

    assert GeckoVersion.parse('33.0') > GeckoVersion.parse('32.0')
    assert not GeckoVersion.parse('33.0') > GeckoVersion.parse('33.0')

    assert not GeckoVersion.parse('32.0') < GeckoVersion.parse('32.0')

    assert GeckoVersion.parse('33.0') != GeckoVersion.parse('32.0')


@pytest.mark.parametrize('version_string, expected_output', (
    ('31.0esr', '31.0esr'),
    ('31.0.1esr', '31.0.1esr'),

    ('32.0', '32.0'),
    ('032.0', '32.0'),
    ('32.0build1', '32.0build1'),
    ('32.0build01', '32.0build1'),
    ('32.0.1', '32.0.1'),
    ('32.0a1', '32.0a1'),
    ('32.0a2', '32.0a2'),
    ('32.0b1', '32.0b1'),
    ('32.0b01', '32.0b1'),
))
def test_gecko_version_implements_str_operator(version_string, expected_output):
    assert str(GeckoVersion.parse(version_string)) == expected_output


@pytest.mark.parametrize('version_string, field, expected', (
    ('0.9', 'major_number', '1.0'),
    ('0.9.1', 'major_number', '1.0'),
    ('1.0b1', 'beta_number', '1.0b2'),
    ('1.0rc1', 'release_candidate_number', '1.0rc2'),
    ('1.0', 'patch_number', '1.0.1'),
    ('1.5', 'minor_number', '1.6'),
    ('1.5.0.1', 'minor_number', '1.6'),
    ('1.5', 'old_fourth_number', '1.5.0.1'),
    ('1.5.0.1', 'old_fourth_number', '1.5.0.2'),
    ('2.0rc1', 'release_candidate_number', '2.0rc2'),
    ('2.0', 'old_fourth_number', '2.0.0.1'),
    ('2.0.0.1', 'old_fourth_number', '2.0.0.2'),
    ('2.0', 'major_number', '3.0'),
    ('2.0.0.1', 'major_number', '3.0'),

    ('31.0esr', 'major_number', '38.0esr'),
    ('31.0.1esr', 'major_number', '38.0esr'),
    ('31.0esr', 'minor_number', '31.1.0esr'),
    ('31.0.1esr', 'minor_number', '31.1.0esr'),
    ('31.0esr', 'patch_number', '31.0.1esr'),
    ('31.0.1esr', 'patch_number', '31.0.2esr'),

    ('32.0a1', 'major_number', '33.0a1'),
    ('32.0a2', 'major_number', '33.0a2'),
    ('32.0b1', 'major_number', '33.0b1'),
    ('32.0', 'major_number', '33.0'),
    ('32.0.1', 'major_number', '33.0'),

    ('32.0', 'minor_number', '32.1.0'),
    ('32.0.1', 'minor_number', '32.1.0'),

    ('32.0', 'patch_number', '32.0.1'),
    ('32.0.1', 'patch_number', '32.0.2'),

    ('32.0b1', 'beta_number', '32.0b2'),

    ('32.0build1', 'build_number', '32.0build2'),
    ('32.0b1build1', 'build_number', '32.0b1build2'),
    ('31.0esrbuild1', 'build_number', '31.0esrbuild2'),

    ('68.0esr', 'major_number', '78.0esr'),
    ('68.0.1esr', 'major_number', '78.0esr'),
    ('68.1.0esr', 'major_number', '78.0esr'),
))
def test_gecko_version_bump(version_string, field, expected):
    version = GeckoVersion.parse(version_string)
    assert str(version.bump(field)) == expected


@pytest.mark.parametrize('version_string, field', (
    ('31.0esr', 'release_candidate_number'),
    ('31.0esr', 'old_fourth_number'),
    ('31.0esr', 'beta_number'),
    ('31.0esr', 'build_number'),

    ('32.0a1', 'minor_number'),
    ('32.0a1', 'patch_number'),
    ('32.0a1', 'beta_number'),
    ('32.0a1', 'release_candidate_number'),
    ('32.0a1', 'old_fourth_number'),
    ('32.0a1', 'build_number'),

    ('32.0a2', 'minor_number'),
    ('32.0a2', 'patch_number'),
    ('32.0a2', 'beta_number'),
    ('32.0a2', 'release_candidate_number'),
    ('32.0a2', 'old_fourth_number'),
    ('32.0a2', 'build_number'),

    ('32.0b1', 'minor_number'),
    ('32.0b1', 'patch_number'),
    ('32.0b1', 'release_candidate_number'),
    ('32.0b1', 'old_fourth_number'),
    ('32.0a2', 'build_number'),

    ('32.0', 'build_number'),

    ('78.0esr', 'major_number'),
    ('78.0.1esr', 'major_number'),
    ('78.1.0esr', 'major_number'),
))
def test_gecko_version_bump_raises(version_string, field):
    version = GeckoVersion.parse(version_string)
    with pytest.raises(ValueError):
        version.bump(field)




_SUPER_PERMISSIVE_PATTERN = re.compile(r"""
(?P<major_number>\d+)\.(?P<minor_number>\d+)(\.(\d+))*
(?P<is_nightly>a1)?(?P<is_aurora_or_devedition>a2)?(b(?P<beta_number>\d+))?
(?P<is_esr>esr)?
""", re.VERBOSE)


@pytest.mark.parametrize('version_string', (
    '32.0a1a2', '32.0a1b2', '31.0b2esr'
))
def test_gecko_version_ensures_it_does_not_have_multiple_type(monkeypatch, version_string):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = GeckoVersion._VALID_ENOUGH_VERSION_PATTERN
    GeckoVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    with pytest.raises(TooManyTypesError):
        GeckoVersion.parse(version_string)

    GeckoVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern


def test_gecko_version_ensures_a_new_added_release_type_is_caught(monkeypatch):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = GeckoVersion._VALID_ENOUGH_VERSION_PATTERN
    GeckoVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    # And a broken type detection
    original_is_release = GeckoVersion.is_release
    GeckoVersion.is_release = False

    with pytest.raises(NoVersionTypeError):
        mozilla_version.gecko.GeckoVersion.parse('32.0.0.0')

    GeckoVersion.is_release = original_is_release
    GeckoVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern


@pytest.mark.parametrize('version_string', (
    # Firefox released versions
    # TODO '0.10rc',
    '0.10',
    '0.10.1',
    '0.8',
    # TODO '0.9rc',
    '0.9',
    '0.9.1',
    '0.9.2',
    '0.9.3',

    '1.0rc1', '1.0rc2', '1.0',
    '1.0.1', '1.0.2', '1.0.3', '1.0.4', '1.0.5', '1.0.6', '1.0.7', '1.0.8',
    '1.5b1', '1.5b2',
    '1.5rc1', '1.5rc2', '1.5rc3', '1.5',
    # '1.5.0.1rc1' is handled as a _RELEASED_EDGE_CASES
    '1.5.0.1',
    '1.5.0.2', '1.5.0.3', '1.5.0.4', '1.5.0.5', '1.5.0.6', '1.5.0.7', '1.5.0.8', '1.5.0.9',
    '1.5.0.10', '1.5.0.11', '1.5.0.12',

    '2.0b1',
    '2.0b2',
    '2.0rc1', '2.0rc2', '2.0rc3', '2.0',
    '2.0.0.1', '2.0.0.2', '2.0.0.3', '2.0.0.4', '2.0.0.5', '2.0.0.6', '2.0.0.7', '2.0.0.8',
    '2.0.0.9', '2.0.0.10', '2.0.0.11', '2.0.0.12', '2.0.0.13', '2.0.0.14', '2.0.0.15', '2.0.0.16',
    '2.0.0.17', '2.0.0.18', '2.0.0.19', '2.0.0.20',

    '3.0rc1', '3.0rc2', '3.0rc3', '3.0',
    '3.1b1', '3.1b2', '3.1b3', '3.5b4',
    '3.5', '3.5rc2', '3.5rc3',
    '3.6', '3.6rc1', '3.6rc2',
    '3.6b1', '3.6b2', '3.6b3', '3.6b4', '3.6b5',
    '3.0.1', '3.0.2', '3.0.3', '3.0.4', '3.0.5', '3.0.6', '3.0.7', '3.0.8', '3.0.9', '3.0.10',
    '3.0.11', '3.0.12', '3.0.13', '3.0.14', '3.0.15',
    # TODO '3.0.16-real',
    '3.0.17', '3.0.18',
    # TODO '3.0.19-real-real',
    '3.1b1', '3.1b2', '3.1b3',
    '3.5b4', '3.5b99',
    '3.5rc1', '3.5rc2', '3.5rc3', '3.5',
    '3.5.1', '3.5.2', '3.5.3', '3.5.4', '3.5.5', '3.5.6', '3.5.7', '3.5.8', '3.5.9', '3.5.10',
    '3.5.11', '3.5.12', '3.5.13', '3.5.14', '3.5.15', '3.5.16', '3.5.17', '3.5.18', '3.5.19',
    '3.6rc1', '3.6rc2', '3.6',
    '3.6b1', '3.6b2', '3.6b3', '3.6b4', '3.6b5',
    # 3.6.1 never shipped
    '3.6.2', '3.6.3',
    # TODO '3.6.3plugin1',
    '3.6.4', '3.6.6', '3.6.7', '3.6.8', '3.6.9', '3.6.10', '3.6.11', '3.6.12', '3.6.13', '3.6.14',
    '3.6.15', '3.6.16', '3.6.17', '3.6.18', '3.6.19', '3.6.20', '3.6.21', '3.6.22', '3.6.23',
    '3.6.24', '3.6.25', '3.6.26', '3.6.27', '3.6.28',

    '4.0b1', '4.0b2', '4.0b3', '4.0b4', '4.0b5', '4.0b6', '4.0b7', '4.0b8', '4.0b9', '4.0b10',
    '4.0b11', '4.0b12',
    '4.0rc1', '4.0rc2', '4.0',
    '4.0.1',

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


@pytest.mark.parametrize('version_string, expected', (
    ('2.0b2', '2.0rc1'),
    ('2.0rc1', '2.0'),
    ('2.0rc2', '2.0'),

    ('31.0', '31.0esr'),
    ('31.0build1', '31.0esrbuild1'),
    ('31.0build2', '31.0esrbuild1'),
    ('31.0.1', '31.0.1esr'),

    ('32.0a1', '32.0a2'),
    ('32.0a2', '32.0b1'),
    ('32.0b1', '32.0'),
    ('32.0b2', '32.0'),
    ('32.0b10', '32.0'),
    ('32.0b10', '32.0'),
    ('32.0b10build3', '32.0build1'),

    ('54.0a1', '54.0a2'),
    ('54.0a2', '54.0b1'),

    ('55.0a1', '55.0b1'),
    ('55.0b1', '55.0'),

    ('60.0', '60.0esr'),
))
def test_gecko_version_bump_version_type(version_string, expected):
    version = GeckoVersion.parse(version_string)
    assert str(version.bump_version_type()) == expected


@pytest.mark.parametrize('version_string', (
    '9.0',
    '31.0esr',
    '32.0',
))
def test_gecko_version_bump_version_type_fail(version_string):
    version = GeckoVersion.parse(version_string)
    with pytest.raises(ValueError):
        version.bump_version_type()


@pytest.mark.parametrize('version_string', (
    '1.5.0.1rc1',
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


@pytest.mark.parametrize('version_string, field, expected', (
    ('67.0a1', 'major_number', '68.0a1'),
    ('67.0b1', 'major_number', '68.0b1'),
    ('67.0', 'major_number', '68.0'),

    ('68.0a1', 'minor_number', '68.1a1'),
    ('68.1a1', 'minor_number', '68.2a1'),
    ('68.0b1', 'minor_number', '68.1b1'),
    ('68.1b1', 'minor_number', '68.2b1'),
    ('68.0', 'minor_number', '68.1.0'),
    ('68.0.1', 'minor_number', '68.1.0'),

    ('68.0', 'patch_number', '68.0.1'),
    ('68.0.1', 'patch_number', '68.0.2'),

    ('33.1build1', 'build_number', '33.1build2')
))
def test_fennec_version_bumps_edge_cases(version_string, field, expected):
    version = FennecVersion.parse(version_string)
    assert str(version.bump(field)) == expected


@pytest.mark.parametrize('version_string, field', (
    ('68.0a1', 'major_number'),
    ('68.0b1', 'major_number'),
    ('68.0', 'major_number'),

    ('68.0a1', 'patch_number'),
    ('68.0b1', 'patch_number'),
))
def test_fennec_version_bumps_raises(version_string, field):
    version = FennecVersion.parse(version_string)
    with pytest.raises(ValueError):
        version.bump(field)


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
    '32.0a2', '31.0esr1', '32.0-build1',
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
