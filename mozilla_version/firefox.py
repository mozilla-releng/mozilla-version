import functools
import re

from mozilla_version.errors import InvalidVersionError, MissingFieldError, TooManyTypesError

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
        |(?P<potential_zero_minor_number>\d+)\.(?P<non_zero_patch_number>[1-9]\d*) # 46.0.0 is not correct
    )(?P<is_three_digit_esr>esr)?                                         # Neither is 46.2.0b1
    # 3-digits end
)(?P<has_build_number>build(?P<build_number>\d+))?$""", re.VERBOSE)        # See more examples of (in)valid versions in the tests


_NUMBERS_TO_REGEX_GROUP_NAMES = {
    'major_number': ('major_number',),
    'minor_number': ('zero_minor_number', 'non_zero_minor_number', 'potential_zero_minor_number'),
    'patch_number': ('non_zero_patch_number', 'potential_zero_patch_number'),
    'beta_number': ('beta_number',),
    'build_number': ('build_number',),
}

_POSSIBLE_RELEASE_TYPES = (
    'is_nightly', 'is_aurora_or_devedition', 'is_beta', 'is_esr', 'is_release',
)


class FirefoxVersion(object):

    def __init__(self, version_string):
        self._version_string = version_string
        self._regex_matches = _VALID_VERSION_PATTERN.match(self._version_string)
        if self._regex_matches is None:
            raise InvalidVersionError(self._version_string)

        for field in ('major_number', 'minor_number'):
            self._assign_mandatory_number(field)

        for field in ('patch_number', 'beta_number', 'build_number'):
            self._assign_optional_number(field)

        self._perform_sanity_check()

    def _assign_mandatory_number(self, field_name):
        matched_value = _get_value_matched_by_regex(field_name, self._regex_matches, self._version_string)
        setattr(self, field_name, int(matched_value))

    def _assign_optional_number(self, field_name):
        try:
            self._assign_mandatory_number(field_name)
        except (MissingFieldError, TypeError):    # TypeError is when None can't be cast to int
            pass

    def _perform_sanity_check(self):
        first_release_type_to_match = None

        def ensure_only_one_release_type(has_previous_type_been_identified, current_release_type):
            is_current_type_identified = getattr(self, current_release_type)
            if is_current_type_identified:
                if has_previous_type_been_identified:
                    raise TooManyTypesError(self._version_string, first_release_type_to_match, current_release_type)    # noqa: F823

                first_release_type_to_match = current_release_type  # noqa: F841

            return has_previous_type_been_identified or is_current_type_identified

        functools.reduce(ensure_only_one_release_type, _POSSIBLE_RELEASE_TYPES, False)

    @property
    def is_nightly(self):
        return self._regex_matches['is_nightly'] is not None

    @property
    def is_aurora_or_devedition(self):
        # TODO raise error for major_number > X. X being the first release shipped after we moved
        # devedition onto beta.
        return self._regex_matches['is_aurora_or_devedition'] is not None

    @property
    def is_beta(self):
        try:
            self.beta_number
            return True
        except AttributeError:
            return False

    @property
    def is_esr(self):
        return self._regex_matches['is_two_digit_esr'] is not None or \
            self._regex_matches['is_three_digit_esr'] is not None

    @property
    def is_release(self):
        return not (self.is_nightly or self.is_aurora_or_devedition or self.is_beta or self.is_esr)

    def __str__(self):
        return self._version_string

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ne__(self, other):
        return self._compare(other) != 0

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def _compare(self, other):
        """Compare this release with another.

        Returns:
            0 if equal
            < 0 is this precedes the other
            > 0 if the other precedes this

        Raises:
            Error if they're not from the same channel
        """
        # self._check_other_is_of_compatible_type(other)

        for field in ('major_number', 'minor_number', 'patch_number', 'beta_number'):
            this_number = getattr(self, field, 0)
            other_number = getattr(other, field, 0)

            difference = this_number - other_number

            if difference != 0:
                return difference

            # beta vs release is a special case handled when major_number is
            # the same. the release will have 'undefined' beta_number, so isn't
            # compariable to beta with a genuine digit
            if field == 'major_number':
                if self.is_beta and other.is_release:
                    return -1
                elif self.is_release and other.is_beta:
                    return 1

        # Build numbers are a special case. We might compare a regular version number
        # (like "32.0b8") versus a release build (as in "32.0b8build1"). As a consequence,
        # we only compare build_numbers when we both have them.
        try:
            return self.build_number - other.build_number
        except AttributeError:
            pass

        return 0


def _get_value_matched_by_regex(field_name, regex_matches, version_string):
    group_names = _NUMBERS_TO_REGEX_GROUP_NAMES[field_name]
    for group_name in group_names:
        value = regex_matches[group_name]
        if value is not None:
            return value

    raise MissingFieldError(version_string, field_name)
