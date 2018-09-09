"""Defines parser helpers."""

from mozilla_version.errors import MissingFieldError

from typing import Union, Optional, NoReturn, Match, cast  # noqa


def get_value_matched_by_regex(field_name, regex_matches, string):
    # type: (str, Match, str) -> Optional[str]
    """Ensure value stored in regex group exists."""
    try:
        value = cast(  # cast is only used by mypy, doesn't alter actual code
            Optional[str],
            regex_matches.group(field_name)
        )
        if value is not None:
            return value
    except IndexError:
        pass

    raise MissingFieldError(string, field_name)
