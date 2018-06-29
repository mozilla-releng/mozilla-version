"""Defines all errors reported by mozilla-version."""


class InvalidVersionError(ValueError):
    """Error when `version_string` doesn't match the pattern of a valid version number."""

    def __init__(self, version_string):
        """Constructor.

        Args:
            version_string (str): The string it was unable to match.
        """
        super(InvalidVersionError, self).__init__(
            'Version "{}" does not match the pattern of a valid version'.format(version_string)
        )


class NoVersionTypeError(ValueError):
    """Error when `version_string` matched the pattern, but was unable to find its type."""

    def __init__(self, version_string):
        """Constructor.

        Args:
            version_string (str): The string it was unable to guess the type.
        """
        super(NoVersionTypeError, self).__init__(
            'Version "{}" matched the pattern of a valid version, but it is unable to find what type it is. \
This is likely a bug in mozilla-version'.format(version_string)
        )


class MissingFieldError(ValueError):
    """Error when `version_string` lacks an expected field."""

    def __init__(self, version_string, field_name):
        """Constructor.

        Args:
            version_string (str): The string it was unable to extract a given field.
            field_name (str): The name of the missing field.
        """
        super(MissingFieldError, self).__init__(
            'Release "{}" does not contain a valid {}'.format(version_string, field_name)
        )


class TooManyTypesError(ValueError):
    """Error when `version_string` has too many types."""

    def __init__(self, version_string, first_matched_type, second_matched_type):
        """Constructor.

        Args:
            version_string (str): The string that gave too many types.
            first_matched_type (str): The name of the first detected type.
            second_matched_type (str): The name of the second detected type
        """
        super(TooManyTypesError, self).__init__(
            'Release "{}" cannot match types "{}" and "{}"'.format(
                version_string, first_matched_type, second_matched_type
            )
        )
