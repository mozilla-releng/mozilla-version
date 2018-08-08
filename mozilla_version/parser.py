"""Defines parser helpers."""

from mozilla_version.errors import PatternNotMatchedError, MissingFieldError


def parse_and_construct_object(
    klass, pattern, string, mandatory_fields, optional_fields, boolean_fields
):
    """Parse string looking for fields and construct klass object."""
    regex_matches = pattern.match(string)
    if regex_matches is None:
        raise PatternNotMatchedError(string, pattern)

    args = {}

    for field in mandatory_fields:
        args[field] = get_value_matched_by_regex(field, regex_matches, string)

    for field in optional_fields:
        try:
            args[field] = get_value_matched_by_regex(field, regex_matches, string)
        except MissingFieldError:
            pass

    for field in boolean_fields:
        args[field] = regex_matches.group(field) is not None

    return klass(**args)


def get_value_matched_by_regex(field_name, regex_matches, string):
    """Ensure value stored in regex group exists."""
    try:
        value = regex_matches.group(field_name)
        if value is not None:
            return value
    except IndexError:
        pass

    raise MissingFieldError(string, field_name)
