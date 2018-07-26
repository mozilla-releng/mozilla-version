"""Defines characteristics of a Firefox version number.

Examples:
    .. code-block:: python

        from mozilla_version.firefox import FirefoxVersion

        version = FirefoxVersion.parse('60.0.1')

        version.major_number    # 60
        version.minor_number    # 0
        version.patch_number    # 1

        version.is_release  # True
        version.is_beta     # False
        version.is_nightly  # False

        str(version)        # '60.0.1'

        previous_version = FirefoxVersion.parse('60.0b14')
        previous_version < version      # True

        previous_version.beta_number    # 14
        previous_version.major_number   # 60
        previous_version.minor_number   # 0
        previous_version.patch_number   # raises AttributeError

        previous_version.is_beta     # True
        previous_version.is_release  # False
        previous_version.is_nightly  # False

        invalid_version = FirefoxVersion.parse('60.1')      # raises InvalidVersionError
        invalid_version = FirefoxVersion.parse('60.0.0')    # raises InvalidVersionError
        version = FirefoxVersion.parse('60.0')    # valid

"""

import re
import attr

from mozilla_version.errors import (
    InvalidVersionError, MissingFieldError, TooManyTypesError, NoVersionTypeError
)
from mozilla_version.version import VersionType

_VALID_VERSION_PATTERN = re.compile(r"""
^(?P<major_number>\d+)\.(
    (?P<zero_minor_number>0)
        (   # 2-digit-versions (like 46.0, 46.0b1, 46.0esr)
            (?P<is_nightly>a1)
            |(?P<is_aurora_or_devedition>a2)
            |b(?P<beta_number>\d+)
            |(?P<is_two_digit_esr>esr)
        )?
    |(  # Here begins the 3-digit-versions.
        (?P<non_zero_minor_number>[1-9]\d*)\.(?P<potential_zero_patch_number>\d+)
        |(?P<potential_zero_minor_number>\d+)\.(?P<non_zero_patch_number>[1-9]\d*)
        # 46.0.0 is not correct
    )(?P<is_three_digit_esr>esr)? # Neither is 46.2.0b1
    # 3-digits end
)(?P<has_build_number>build(?P<build_number>\d+))?$""", re.VERBOSE)
# See more examples of (in)valid versions in the tests


_NUMBERS_TO_REGEX_GROUP_NAMES = {
    'major_number': ('major_number',),
    'minor_number': ('zero_minor_number', 'non_zero_minor_number', 'potential_zero_minor_number'),
    'patch_number': ('non_zero_patch_number', 'potential_zero_patch_number'),
    'beta_number': ('beta_number',),
    'build_number': ('build_number',),
}


def _int_or_none(val):
    if val is None:
        return val
    return int(val)


def _find_type(version):
    version_type = None

    def ensure_version_type_is_not_already_defined(previous_type, candidate_type):
        if previous_type is not None:
            raise TooManyTypesError(
                version._version_string, previous_type, candidate_type
            )

    if version.is_nightly:
        version_type = VersionType.NIGHTLY
    if version.is_aurora_or_devedition:
        ensure_version_type_is_not_already_defined(
            version_type, VersionType.AURORA_OR_DEVEDITION
        )
        version_type = VersionType.AURORA_OR_DEVEDITION
    if version.is_beta:
        ensure_version_type_is_not_already_defined(version_type, VersionType.BETA)
        version_type = VersionType.BETA
    if version.is_esr:
        ensure_version_type_is_not_already_defined(version_type, VersionType.ESR)
        version_type = VersionType.ESR
    if version.is_release:
        ensure_version_type_is_not_already_defined(version_type, VersionType.RELEASE)
        version_type = VersionType.RELEASE

    if version_type is None:
        raise NoVersionTypeError(version._version_string)

    return version_type


@attr.s(frozen=True, cmp=False)
class FirefoxVersion(object):
    """Class that validates and handles Firefox version numbers.

    Args:
        version_string (str): the string to validate and build the object from

    Raises:
        InvalidVersionError: if the string doesn't match the pattern of a valid version number
        MissingFieldError: if a mandatory field is missing in the string. Mandatory fields are
            `major_number` and `minor_number`
        TypeError: if an integer can't be cast from the string
        TooManyTypesError: if the string matches more than 1 `VersionType`
        NoVersionTypeError: if the string matches none.

    """

    _version_string = attr.ib(type=str)
    is_nightly = attr.ib(type=bool)
    is_aurora_or_devedition = attr.ib(type=bool)
    is_esr = attr.ib(type=bool)
    major_number = attr.ib(type=int, converter=int)
    minor_number = attr.ib(type=int, converter=int)
    patch_number = attr.ib(type=int, converter=_int_or_none, default=None)
    beta_number = attr.ib(type=int, converter=_int_or_none, default=None)
    build_number = attr.ib(type=int, converter=_int_or_none, default=None)
    version_type = attr.ib(init=False, default=attr.Factory(_find_type, takes_self=True))

    @classmethod
    def parse(cls, version_string):
        """Construct an object representing a valid Firefox version number."""
        regex_matches = _VALID_VERSION_PATTERN.match(version_string)
        if regex_matches is None:
            raise InvalidVersionError(version_string)

        args = {}

        for field in ('major_number', 'minor_number'):
            args[field] = _get_value_matched_by_regex(field, regex_matches, version_string)

        for field in ('patch_number', 'beta_number', 'build_number'):
            try:
                args[field] = _get_value_matched_by_regex(field, regex_matches, version_string)
            except MissingFieldError:
                pass

        return cls(
            version_string=version_string,
            is_nightly=regex_matches.group('is_nightly') is not None,
            is_aurora_or_devedition=regex_matches.group('is_aurora_or_devedition') is not None,
            is_esr=regex_matches.group('is_two_digit_esr') is not None or
            regex_matches.group('is_three_digit_esr') is not None,
            **args
        )

    @property
    def is_beta(self):
        """Return `True` if `FirefoxVersion` was built with a string matching a beta version."""
        return self.beta_number is not None

    @property
    def is_release(self):
        """Return `True` if `FirefoxVersion` was built with a string matching a release version."""
        return not (self.is_nightly or self.is_aurora_or_devedition or self.is_beta or self.is_esr)

    def __str__(self):
        """Implement string representation.

        Return the original string passed to the constructor.
        """
        return self._version_string

    def __eq__(self, other):
        """Implement `==` operator.

        A version is considered equal to another if all numbers match and if they are of the same
        `VersionType`. Like said in `VersionType`, release and ESR are considered equal (if they
        share the same numbers). If a version contains a build number but not the other, the build
        number won't be considered in the comparison.

        Examples:
            .. code-block:: python

                assert FirefoxVersion.parse('60.0') == FirefoxVersion.parse('60.0')
                assert FirefoxVersion.parse('60.0') == FirefoxVersion.parse('60.0esr')
                assert FirefoxVersion.parse('60.0') == FirefoxVersion.parse('60.0build1')
                assert FirefoxVersion.parse('60.0build1') == FirefoxVersion.parse('60.0build1')

                assert FirefoxVersion.parse('60.0') != FirefoxVersion.parse('61.0')
                assert FirefoxVersion.parse('60.0') != FirefoxVersion.parse('60.1.0')
                assert FirefoxVersion.parse('60.0') != FirefoxVersion.parse('60.0.1')
                assert FirefoxVersion.parse('60.0') != FirefoxVersion.parse('60.0a1')
                assert FirefoxVersion.parse('60.0') != FirefoxVersion.parse('60.0a2')
                assert FirefoxVersion.parse('60.0') != FirefoxVersion.parse('60.0b1')
                assert FirefoxVersion.parse('60.0build1') != FirefoxVersion.parse('60.0build2')

        """
        return self._compare(other) == 0

    def __ne__(self, other):
        """Implement `!=` operator."""
        return self._compare(other) != 0

    def __lt__(self, other):
        """Implement `<` operator."""
        return self._compare(other) < 0

    def __le__(self, other):
        """Implement `<=` operator."""
        return self._compare(other) <= 0

    def __gt__(self, other):
        """Implement `>` operator."""
        return self._compare(other) > 0

    def __ge__(self, other):
        """Implement `>=` operator."""
        return self._compare(other) >= 0

    def _compare(self, other):
        """Compare this release with another.

        Returns:
            0 if equal
            < 0 is this precedes the other
            > 0 if the other precedes this

        """
        for field in ('major_number', 'minor_number', 'patch_number'):
            this_number = getattr(self, field)
            this_number = 0 if this_number is None else this_number
            other_number = getattr(other, field)
            other_number = 0 if other_number is None else other_number

            difference = this_number - other_number

            if difference != 0:
                return difference

        channel_difference = self._compare_version_type(other)
        if channel_difference != 0:
            return channel_difference

        if self.is_beta and other.is_beta:
            beta_difference = self.beta_number - other.beta_number
            if beta_difference != 0:
                return beta_difference

        # Build numbers are a special case. We might compare a regular version number
        # (like "32.0b8") versus a release build (as in "32.0b8build1"). As a consequence,
        # we only compare build_numbers when we both have them.
        try:
            return self.build_number - other.build_number
        except TypeError:
            pass

        return 0

    def _compare_version_type(self, other):
        return self.version_type.compare(other.version_type)


def _get_value_matched_by_regex(field_name, regex_matches, version_string):
    group_names = _NUMBERS_TO_REGEX_GROUP_NAMES[field_name]
    for group_name in group_names:
        try:
            value = regex_matches.group(group_name)
            if value is not None:
                return value
        except IndexError:
            pass

    raise MissingFieldError(version_string, field_name)
