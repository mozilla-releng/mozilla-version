import pytest

from mozilla_version.balrog import BalrogReleaseName
from mozilla_version.firefox import FirefoxVersion


@pytest.mark.parametrize(
    'product, major_number, minor_number, patch_number, beta_number, build_number, is_nightly, \
is_aurora_or_devedition, is_esr, expected_output_string', ((
    'firefox', 32, 0, None, None, 1, False, False, False, 'firefox-32.0-build1'
), (
    'firefox', 32, 0, 1, None, 2, False, False, False, 'firefox-32.0.1-build2'
), (
    'firefox', 32, 0, None, 3, 4, False, False, False, 'firefox-32.0b3-build4'
), (
    'firefox', 32, 0, None, None, 5, True, False, False, 'firefox-32.0a1-build5'
), (
    'firefox', 32, 0, None, None, 6, False, True, False, 'firefox-32.0a2-build6'
), (
    'firefox', 32, 0, None, None, 7, False, False, True, 'firefox-32.0esr-build7'
), (
    'firefox', 32, 0, 1, None, 8, False, False, True, 'firefox-32.0.1esr-build8'
)))
def test_balrog_release_name_constructor_and_str(
    product, major_number, minor_number, patch_number, beta_number, build_number, is_nightly,
    is_aurora_or_devedition, is_esr, expected_output_string
):
    assert str(BalrogReleaseName(product, FirefoxVersion(
        major_number=major_number,
        minor_number=minor_number,
        patch_number=patch_number,
        beta_number=beta_number,
        build_number=build_number,
        is_nightly=is_nightly,
        is_aurora_or_devedition=is_aurora_or_devedition,
        is_esr=is_esr
    ))) == expected_output_string


@pytest.mark.parametrize('string', (
    'firefox-32.0-build1',
    'firefox-32.0.1-build2',
    'firefox-32.0b3-build4',
    'firefox-32.0a1-build5',
    'firefox-32.0a2-build6',
    'firefox-32.0esr-build7',
    'firefox-32.0.1esr-build8',
))
def test_balrog_release_name_parse(string):
    assert str(BalrogReleaseName.parse(string)) == string


@pytest.mark.parametrize('previous, next', (
    ('firefox-32.0-build1', 'firefox-33.0-build1'),
    ('firefox-32.0-build1', 'firefox-32.1.0-build1'),
    ('firefox-32.0-build1', 'firefox-32.0.1-build1'),
    ('firefox-32.0-build1', 'firefox-32.0-build2'),

    ('firefox-32.0a1-build1', 'firefox-32.0-build1'),
    ('firefox-32.0a2-build1', 'firefox-32.0-build1'),
    ('firefox-32.0b1-build1', 'firefox-32.0-build1'),

    ('firefox-32.0.1-build1', 'firefox-33.0-build1'),
    ('firefox-32.0.1-build1', 'firefox-32.1.0-build1'),
    ('firefox-32.0.1-build1', 'firefox-32.0.2-build1'),
    ('firefox-32.0.1-build1', 'firefox-32.0.1-build2'),

    ('firefox-32.1.0-build1', 'firefox-33.0-build1'),
    ('firefox-32.1.0-build1', 'firefox-32.2.0-build1'),
    ('firefox-32.1.0-build1', 'firefox-32.1.1-build1'),
    ('firefox-32.1.0-build1', 'firefox-32.1.0-build2'),

    ('firefox-32.0b1-build1', 'firefox-33.0b1-build1'),
    ('firefox-32.0b1-build1', 'firefox-32.0b2-build1'),
    ('firefox-32.0b1-build1', 'firefox-32.0b1-build2'),

    ('firefox-2.0-build1', 'firefox-10.0-build1'),
    ('firefox-10.2.0-build1', 'firefox-10.10.0-build1'),
    ('firefox-10.0.2-build1', 'firefox-10.0.10-build1'),
    ('firefox-10.10.1-build1', 'firefox-10.10.10-build1'),
    ('firefox-10.0-build2', 'firefox-10.0-build10'),
    ('firefox-10.0b2-build1', 'firefox-10.0b10-build1'),
))
def test_firefox_version_implements_lt_operator(previous, next):
    assert BalrogReleaseName.parse(previous) < BalrogReleaseName.parse(next)


def test_firefox_version_implements_remaining_comparision_operators():
    assert BalrogReleaseName.parse('firefox-32.0-build1') <= BalrogReleaseName.parse('firefox-32.0-build1')
    assert BalrogReleaseName.parse('firefox-32.0-build1') <= BalrogReleaseName.parse('firefox-33.0-build1')

    assert BalrogReleaseName.parse('firefox-33.0-build1') >= BalrogReleaseName.parse('firefox-32.0-build1')
    assert BalrogReleaseName.parse('firefox-33.0-build1') >= BalrogReleaseName.parse('firefox-33.0-build1')

    assert BalrogReleaseName.parse('firefox-33.0-build1') > BalrogReleaseName.parse('firefox-32.0-build1')
    assert not BalrogReleaseName.parse('firefox-33.0-build1') > BalrogReleaseName.parse('firefox-33.0-build1')

    assert not BalrogReleaseName.parse('firefox-32.0-build1') < BalrogReleaseName.parse('firefox-32.0-build1')

    assert BalrogReleaseName.parse('firefox-33.0-build1') != BalrogReleaseName.parse('firefox-32.0-build1')
