import pytest
import re

import mozilla_version.gecko

from mozilla_version.errors import PatternNotMatchedError, TooManyTypesError, NoVersionTypeError
from mozilla_version.gecko import FirefoxVersion, DeveditionVersion, ThunderbirdVersion, FennecVersion


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
))
def test_firefox_version_raises_when_invalid_version_is_given(version_string, ExpectedErrorType):
    with pytest.raises(ExpectedErrorType):
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
    '32.0', '032.0', '32.0build1', '32.0build01', '32.0-build1', '32.0build2', '32.0esr',
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
(?P<major_number>\d+)\.(?P<minor_number>\d+)(\.(\d+))*
(?P<is_nightly>a1)?(?P<is_aurora_or_devedition>a2)?(b(?P<beta_number>\d+))?
(?P<is_esr>esr)?
""", re.VERBOSE)


@pytest.mark.parametrize('version_string', (
    '32.0a1a2', '32.0a1b2', '32.0b2esr'
))
def test_firefox_version_ensures_it_does_not_have_multiple_type(monkeypatch, version_string):
    # Let's make sure the sanity checks detect a broken regular expression
    monkeypatch.setattr(
        mozilla_version.gecko, '_VALID_ENOUGH_VERSION_PATTERN', _SUPER_PERMISSIVE_PATTERN
    )

    with pytest.raises(TooManyTypesError):
        FirefoxVersion.parse(version_string)


def test_firefox_version_ensures_a_new_added_release_type_is_caught(monkeypatch):
    # Let's make sure the sanity checks detect a broken regular expression
    monkeypatch.setattr(
        mozilla_version.gecko, '_VALID_ENOUGH_VERSION_PATTERN', _SUPER_PERMISSIVE_PATTERN
    )
    # And a broken type detection
    original_is_release = FirefoxVersion.is_release
    FirefoxVersion.is_release = False

    with pytest.raises(NoVersionTypeError):
        mozilla_version.gecko.FirefoxVersion.parse('32.0.0.0')

    FirefoxVersion.is_release = original_is_release


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
