import pytest

from mozilla_version.errors import InvalidVersionError
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


@pytest.mark.parametrize('version_string', (
    '32', '32.b2', '.1', '32.2', '32.02', '32.0a1a2', '32.0a1b2', '32.0b2esr', '32.0esrb2',
))
def test_firefox_version_raises_when_invalid_version_is_given(version_string):
    with pytest.raises(InvalidVersionError):
        FirefoxVersion(version_string)


@pytest.mark.parametrize('version_string, expected_type', VALID_VERSIONS.items())
def test_firefox_version_is_of_a_defined_type(version_string, expected_type):
    release = FirefoxVersion(version_string)
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

    ('2.0', '10.0'),
    ('10.2.0', '10.10.0'),
    ('10.0.2', '10.0.10'),
    ('10.10.1', '10.10.10'),
    ('10.0build2', '10.0build10'),
    ('10.0b2', '10.0b10'),
))
def test_firefox_version_implements_lt_operator(previous, next):
    assert FirefoxVersion(previous) < FirefoxVersion(next)


@pytest.mark.parametrize('equivalent_version_string', (
    '32.0', '032.0', '32.0build1', '32.0build01',
))
def test_firefox_version_implements_eq_operator(equivalent_version_string):
    assert FirefoxVersion('32.0') == FirefoxVersion(equivalent_version_string)


@pytest.mark.parametrize('version_string', (
    '32.0', '032.0', '32.0build1', '32.0build01',
))
def test_firefox_version_implements_str_operator(version_string):
    assert str(FirefoxVersion(version_string)) == version_string
