import pytest
import re

from distutils.version import StrictVersion, LooseVersion

import mozilla_version.gecko

from mozilla_version.errors import PatternNotMatchedError, TooManyTypesError, NoVersionTypeError
from mozilla_version.fenix import FenixVersion
from mozilla_version.test import does_not_raise


VALID_VERSIONS = {
    '0.3.0-rc.1': 'release_candidate',
    '1.0.0': 'release',
    '1.0.0-rc.1': 'release_candidate',
    '1.0.0-rc.2': 'release_candidate',
    '1.0.1': 'release',
    '1.0.1-rc.1': 'release_candidate',
    '1.1.0': 'release',
    '1.1.0-rc.1': 'release_candidate',
    '1.1.0-rc.2': 'release_candidate',
    '1.2.0': 'release',
    '1.2.0-rc.1': 'release_candidate',
    '1.2.0-rc.2': 'release_candidate',
    '1.3.0': 'release',
    '1.3.0-rc.1': 'release_candidate',
    '1.3.0-rc.2': 'release_candidate',
    '1.3.0-rc.3': 'release_candidate',
    '2.2.0-rc.1': 'release_candidate',
    '3.0.0-beta.2': 'beta',
    '3.0.0-beta.3': 'beta',
    '3.0.0': 'release',
}


@pytest.mark.parametrize('major_number, minor_number, patch_number, beta_number, rc_number, expected_output_string', ((
    3, 0, 0, None, None, '3.0.0'
), (
    3, 0, 1, None, None, '3.0.1'
), (
    3, 0, 0, 3, None, '3.0.0-beta.3'
), (
    3, 0, 0, None, 3, '3.0.0-rc.3'
)))
def test_fenix_version_constructor_and_str(major_number, minor_number, patch_number, beta_number, rc_number, expected_output_string):
    assert str(FenixVersion(
        major_number=major_number,
        minor_number=minor_number,
        patch_number=patch_number,
        beta_number=beta_number,
        release_candidate_number=rc_number,
    )) == expected_output_string


@pytest.mark.parametrize('major_number, minor_number, patch_number, beta_number, rc_number, ExpectedErrorType', ((
    3, 0, 0, 1, 1, TooManyTypesError
), (
    3, 0, 0, 0, None, ValueError
), (
    3, 0, None, None, None, TypeError
), (
    3, 0, 0, None, 0, ValueError
), (
    -1, 0, 0, None, None, ValueError
), (
    3, -1, 0, None, None, ValueError
), (
    3, 0, -1, None, None, ValueError
), (
    2.2, 0, 0, None, None, ValueError
), (
    'some string', 0, 0, None, None, ValueError
)))
def test_fail_fenix_version_constructor(major_number, minor_number, patch_number, beta_number, rc_number, ExpectedErrorType):
    with pytest.raises(ExpectedErrorType):
        FenixVersion(
            major_number=major_number,
            minor_number=minor_number,
            patch_number=patch_number,
            beta_number=beta_number,
            release_candidate_number=rc_number,
        )


def test_fenix_version_constructor_minimum_kwargs():
    assert str(FenixVersion(3, 0, 1)) == '3.0.1'
    assert str(FenixVersion(3, 1, 0)) == '3.1.0'
    assert str(FenixVersion(3, 0, 0, beta_number=1)) == '3.0.0-beta.1'

    assert str(FenixVersion(1, 0, 0, release_candidate_number=1)) == '1.0.0-rc.1'


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
))
def test_fenix_version_raises_when_invalid_version_is_given(version_string, ExpectedErrorType):
    with pytest.raises(ExpectedErrorType):
        FenixVersion.parse(version_string)


@pytest.mark.parametrize('version_string, expected_type', VALID_VERSIONS.items())
def test_fenix_version_is_of_a_defined_type(version_string, expected_type):
    release = FenixVersion.parse(version_string)
    assert getattr(release, 'is_{}'.format(expected_type))


@pytest.mark.parametrize('previous, next', (
    ('2.0.0', '3.0.0'),
    ('2.0.0', '3.1.0'),
    ('2.0.0', '3.0.1'),

    ('2.0.1', '3.0.0'),
    ('2.0.1', '2.1.0'),
    ('2.0.1', '2.0.2'),

    ('2.1.0', '3.0.0'),
    ('2.1.0', '2.2.0'),
    ('2.1.0', '2.1.1'),

    ('2.0.0-beta.1', '3.0.0-beta.1'),
    ('2.0.0-beta.1', '2.0.0-beta.2'),

    ('2.0.0-beta.1', '2.0.0'),

    ('1.0.0-rc.1', '1.0.0-rc.2'),
    ('1.0.0-rc.1', '1.0.0'),
    ('3.5.0-beta.4', '3.5.0-rc.2'),
    ('3.5.0-beta.4', '3.5.0'),
    ('3.5.0-rc.2', '3.5.0'),
    ('3.5.0-rc.2', '3.5.0-rc.3'),
))
def test_fenix_version_implements_lt_operator(previous, next):
    assert FenixVersion.parse(previous) < FenixVersion.parse(next)


@pytest.mark.parametrize('equivalent_version_string', (
    '3.00.0', '03.0.0', '3.0.0',
))
def test_fenix_version_implements_eq_operator(equivalent_version_string):
    assert FenixVersion.parse('3.0.0') == FenixVersion.parse(equivalent_version_string)
    # raw strings are also converted
    assert FenixVersion.parse('3.0.0') == equivalent_version_string


@pytest.mark.parametrize('equivalent_version_string', (
    '3.00.0-beta.1', '03.0.0-beta.1', '3.0.0-beta.1',
))
def test_fenix_beta_version_implements_eq_operator(equivalent_version_string):
    assert FenixVersion.parse('3.0.0-beta.1') == FenixVersion.parse(equivalent_version_string)
    # raw strings are also converted
    assert FenixVersion.parse('3.0.0-beta.1') == equivalent_version_string


@pytest.mark.parametrize('equivalent_version_string', (
    '3.00.0-rc.1', '03.0.0-rc.1', '3.0.0-rc.01',
))
def test_fenix_rc_version_implements_eq_operator(equivalent_version_string):
    assert FenixVersion.parse('3.0.0-rc.1') == FenixVersion.parse(equivalent_version_string)
    # raw strings are also converted
    assert FenixVersion.parse('3.0.0-rc.1') == equivalent_version_string


@pytest.mark.parametrize('wrong_type', (
    3,
    3.0,
    ('3', '0', '1'),
    ['3', '0', '1'],
    LooseVersion('3.0.0'),
    StrictVersion('3.0.0'),
))
def test_fenix_version_raises_eq_operator(wrong_type):
    with pytest.raises(ValueError):
        assert FenixVersion.parse('3.0.0') == wrong_type
    # AttributeError is raised by LooseVersion and StrictVersion
    with pytest.raises((ValueError, AttributeError)):
        assert wrong_type == FenixVersion.parse('3.0.0')


def test_fenix_version_implements_remaining_comparision_operators():
    assert FenixVersion.parse('2.0.0') <= FenixVersion.parse('2.0.0')
    assert FenixVersion.parse('2.0.0') <= FenixVersion.parse('3.0.0')

    assert FenixVersion.parse('3.0.0') >= FenixVersion.parse('2.0.0')
    assert FenixVersion.parse('3.0.0') >= FenixVersion.parse('3.0.0')

    assert FenixVersion.parse('3.0.0') > FenixVersion.parse('2.0.0')
    assert not FenixVersion.parse('3.0.0') > FenixVersion.parse('3.0.0')

    assert not FenixVersion.parse('2.0.0') < FenixVersion.parse('2.0.0')

    assert FenixVersion.parse('3.0.0') != FenixVersion.parse('2.0.0')


@pytest.mark.parametrize('version_string, expected_output', (
    ('2.0.0', '2.0.0'),
    ('02.0.0', '2.0.0'),
    ('2.0.1', '2.0.1'),
    ('2.0.0-rc.1', '2.0.0-rc.1'),
    ('2.0.0-rc.2', '2.0.0-rc.2'),
    ('2.0.0-rc.02', '2.0.0-rc.2'),
    ('2.0.0-beta.1', '2.0.0-beta.1'),
    ('2.0.0-beta.01', '2.0.0-beta.1'),
))
def test_fenix_version_implements_str_operator(version_string, expected_output):
    assert str(FenixVersion.parse(version_string)) == expected_output


@pytest.mark.parametrize('version_string, field, expected', (
    ('0.9.0', 'major_number', '1.0.0'),
    ('0.9.1', 'major_number', '1.0.0'),
    ('1.0.0-beta.1', 'beta_number', '1.0.0-beta.2'),
    ('1.0.0-rc.1', 'release_candidate_number', '1.0.0-rc.2'),
    ('1.0.0', 'patch_number', '1.0.1'),
    ('1.5.0', 'minor_number', '1.6.0'),
    ('1.5.1', 'minor_number', '1.6.0'),
    ('2.0.0-rc.1', 'release_candidate_number', '2.0.0-rc.2'),
    ('2.0.0', 'major_number', '3.0.0'),
    ('2.0.1', 'major_number', '3.0.0'),

    ('2.0.0-rc.2', 'major_number', '3.0.0'),
    ('2.0.0-beta.1', 'major_number', '3.0.0-beta.1'),
    ('2.0.0', 'major_number', '3.0.0'),
    ('2.0.1', 'major_number', '3.0.0'),

    ('2.0.0', 'minor_number', '2.1.0'),
    ('2.0.1', 'minor_number', '2.1.0'),

    ('2.0.0', 'patch_number', '2.0.1'),
    ('2.0.1', 'patch_number', '2.0.2'),

    ('2.0.0-beta.1', 'beta_number', '2.0.0-beta.2'),
))
def test_fenix_version_bump(version_string, field, expected):
    version = FenixVersion.parse(version_string)
    assert str(version.bump(field)) == expected


@pytest.mark.parametrize('version_string, field', (
    ('2.0.0-beta.1', 'release_candidate_number'),
))
def test_fenix_version_bump_raises(version_string, field):
    version = FenixVersion.parse(version_string)
    with pytest.raises(ValueError):
        version.bump(field)


_SUPER_PERMISSIVE_PATTERN = re.compile(r"""
^(?P<major_number>\d+)\.(?P<minor_number>\d+)(\.(?P<patch_number>\d+))?
(-beta\.(?P<beta_number>\d+))?(-rc\.(?P<release_candidate_number>\d+))?
""", re.VERBOSE)


@pytest.mark.parametrize('version_string', (
    '2.0.0-beta.1-rc.2',
))
def test_fenix_version_ensures_it_does_not_have_multiple_type(monkeypatch, version_string):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = FenixVersion._VALID_ENOUGH_VERSION_PATTERN
    FenixVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    with pytest.raises(TooManyTypesError):
        FenixVersion.parse(version_string)

    FenixVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern


def test_fenix_version_ensures_a_new_added_release_type_is_caught(monkeypatch):
    # Let's make sure the sanity checks detect a broken regular expression
    original_pattern = FenixVersion._VALID_ENOUGH_VERSION_PATTERN
    FenixVersion._VALID_ENOUGH_VERSION_PATTERN = _SUPER_PERMISSIVE_PATTERN

    # And a broken type detection
    original_is_release = FenixVersion.is_release
    FenixVersion.is_release = False

    with pytest.raises(NoVersionTypeError):
        mozilla_version.fenix.FenixVersion.parse('2.0.0')

    FenixVersion.is_release = original_is_release
    FenixVersion._VALID_ENOUGH_VERSION_PATTERN = original_pattern
