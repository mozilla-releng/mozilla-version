"""Defines characteristics of a Balrog release name.

Balrog is the server that delivers Firefox and Thunderbird updates. Release names follow
the pattern "{product}-{version}-build{build_number}"

Examples:
    .. code-block:: python

        from mozilla_version.balrog import BalrogReleaseName

        balrog_release = BalrogReleaseName.parse('firefox-60.0.1-build1')

        balrog_release.product                 # firefox
        balrog_release.version.major_number    # 60
        str(balrog_release)                    # 'firefox-60.0.1-build1'

        previous_release = BalrogReleaseName.parse('firefox-60.0-build2')
        previous_release < balrog_release      # True

        invalid = BalrogReleaseName.parse('60.0.1')           # raises PatternNotMatchedError
        invalid = BalrogReleaseName.parse('firefox-60.0.1')   # raises PatternNotMatchedError

        # Releases can be built thanks to version classes like FirefoxVersion
        BalrogReleaseName('firefox', FirefoxVersion(60, 0, 1, 1))  # 'firefox-60.0.1-build1'

"""

import attr
import re

from mozilla_version.errors import PatternNotMatchedError
from mozilla_version.parser import parse_and_construct_object, get_value_matched_by_regex
from mozilla_version.firefox import FirefoxVersion


_VALID_ENOUGH_BALROG_RELEASE_PATTERN = re.compile(r"""
^(?P<product>[a-z]+)
-(?P<major_number>\d+)
\.(?P<minor_number>\d+)
(\.(?P<patch_number>\d+))?
(
    (?P<is_nightly>a1)
    |(?P<is_aurora_or_devedition>a2)
    |b(?P<beta_number>\d+)
    |(?P<is_esr>esr)
)?
-build(?P<build_number>\d+)
$""", re.VERBOSE | re.IGNORECASE)


_SUPPORTED_PRODUCTS = {
    'firefox': FirefoxVersion,
    # TODO support devedition, thunderbird, and fennec
}


def _supported_product(string):
    product = string.lower()
    if product not in _SUPPORTED_PRODUCTS:
        raise PatternNotMatchedError(string, pattern='unknown product')
    return product


@attr.s(frozen=True, cmp=True)
class BalrogReleaseName(object):
    """Class that validates and handles Balrog release names.

    Raises:
        PatternNotMatchedError: if a parsed string doesn't match the pattern of a valid release
        MissingFieldError: if a mandatory field is missing in the string. Mandatory fields are
            `product`, `major_number`, `minor_number`, and `build_number`
        ValueError: if an integer can't be cast or is not (strictly) positive
        TooManyTypesError: if the string matches more than 1 `VersionType`
        NoVersionTypeError: if the string matches none.

    """

    product = attr.ib(type=str, converter=_supported_product)
    version = attr.ib(type=FirefoxVersion)

    @classmethod
    def parse(cls, release_string):
        """Construct an object representing a valid Firefox version number."""
        product = get_value_matched_by_regex(
            'product', _VALID_ENOUGH_BALROG_RELEASE_PATTERN.match(release_string),
            release_string
        )
        version_class = _SUPPORTED_PRODUCTS[product]

        version = parse_and_construct_object(
            klass=version_class, pattern=_VALID_ENOUGH_BALROG_RELEASE_PATTERN,
            string=release_string,
            mandatory_fields=('major_number', 'minor_number', 'build_number'),
            optional_fields=('patch_number', 'beta_number'),
            boolean_fields=('is_nightly', 'is_aurora_or_devedition', 'is_esr')
        )

        return cls(product, version)

    def __str__(self):
        """Implement string representation.

        Computes a new string based on the given attributes.
        """
        version_string = str(self.version).replace('build', '-build')
        return '{}-{}'.format(self.product, version_string)
