"""Defines characteristics of a Fenix version at Mozilla."""

import attr
import re

from mozilla_version.errors import TooManyTypesError, NoVersionTypeError
from mozilla_version.version import BaseVersion, VersionType
from mozilla_version.parser import strictly_positive_int_or_none, positive_int


def _find_type(version):
    version_type = None

    def ensure_version_type_is_not_already_defined(previous_type, candidate_type):
        if previous_type is not None:
            raise TooManyTypesError(
                str(version), previous_type, candidate_type
            )

    if version.is_beta:
        version_type = VersionType.BETA
    if version.is_release_candidate:
        ensure_version_type_is_not_already_defined(version_type, VersionType.RELEASE_CANDIDATE)
        version_type = VersionType.RELEASE_CANDIDATE
    if version.is_release:
        ensure_version_type_is_not_already_defined(version_type, VersionType.RELEASE)
        version_type = VersionType.RELEASE

    if version_type is None:
        raise NoVersionTypeError(str(version))

    return version_type


@attr.s(frozen=True, eq=False, hash=True)
class FenixVersion(BaseVersion):
    """Class that validates and handles Fenix version numbers."""

    _VALID_ENOUGH_VERSION_PATTERN = re.compile(r"""
        ^(?P<major_number>\d+)
        \.(?P<minor_number>\d+)
        \.(?P<patch_number>\d+)
        (
            -beta\.(?P<beta_number>\d+)
            |-rc\.(?P<release_candidate_number>\d+)
        )?$""", re.VERBOSE)

    # Patch_number is required, so can't be none like in BaseVersion
    patch_number = attr.ib(type=int, converter=positive_int, default=None)

    _MANDATORY_NUMBERS = BaseVersion._MANDATORY_NUMBERS + (
        'patch_number',
    )
    _OPTIONAL_NUMBERS = (
        'beta_number', 'release_candidate_number',
    )

    _ALL_NUMBERS = _MANDATORY_NUMBERS + _OPTIONAL_NUMBERS

    beta_number = attr.ib(type=int, converter=strictly_positive_int_or_none, default=None)
    release_candidate_number = attr.ib(
        type=int, converter=strictly_positive_int_or_none, default=None
    )
    version_type = attr.ib(init=False, default=attr.Factory(_find_type, takes_self=True))

    @property
    def is_beta(self):
        """Return `True` if `FenixVersion` was built with a string matching a beta version."""
        return self.beta_number is not None

    @property
    def is_release_candidate(self):
        """Return `True` if `FenixVersion` was built with a string matching an RC version."""
        return self.release_candidate_number is not None

    @property
    def is_release(self):
        """Return `True` if `FenixVersion` was built with a string matching a release version."""
        return not any((
            self.is_beta, self.is_release_candidate,
        ))

    def __str__(self):
        """Implement string representation.

        Computes a new string based on the given attributes.
        """
        string = super(FenixVersion, self).__str__()

        if self.is_beta:
            string = '{}-beta.{}'.format(string, self.beta_number)
        elif self.is_release_candidate:
            string = '{}-rc.{}'.format(string, self.release_candidate_number)

        return string

    def _compare(self, other):
        if isinstance(other, str):
            other = FenixVersion.parse(other)
        elif not isinstance(other, FenixVersion):
            raise ValueError('Cannot compare "{}", type not supported!'.format(other))

        difference = super(FenixVersion, self)._compare(other)
        if difference != 0:
            return difference

        channel_difference = self._compare_version_type(other)
        if channel_difference != 0:
            return channel_difference

        if self.is_beta and other.is_beta:
            beta_difference = self.beta_number - other.beta_number
            if beta_difference != 0:
                return beta_difference

        if self.is_release_candidate and other.is_release_candidate:
            rc_difference = self.release_candidate_number - other.release_candidate_number
            if rc_difference != 0:
                return rc_difference

        return 0

    def _compare_version_type(self, other):
        return self.version_type.compare(other.version_type)

    def _create_bump_kwargs(self, field):
        bump_kwargs = super(FenixVersion, self)._create_bump_kwargs(field)

        if bump_kwargs.get('beta_number') == 0:
            if self.is_beta:
                bump_kwargs['beta_number'] = 1
            else:
                del bump_kwargs['beta_number']

        if field != 'release_candidate_number':
            del bump_kwargs['release_candidate_number']

        return bump_kwargs
