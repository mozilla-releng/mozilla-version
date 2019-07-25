import pytest

from mozilla_version.errors import PatternNotMatchedError


@pytest.mark.parametrize('string, patterns, expected_message', ((
    'some string',
    ['one single pattern'],
    '"some string" does not match the pattern: one single pattern',
), (
    'some string',
    ['one pattern', 'two patterns'],
    '''"some string" does not match the patterns:
 - one pattern
 - two patterns''',
)))
def test_pattern_not_matched_error_changes_its_error_message(string, patterns, expected_message):
    with pytest.raises(PatternNotMatchedError) as exc_info:
        raise PatternNotMatchedError(string, patterns)

    assert exc_info.value.args == (expected_message,)


def test_pattern_not_matched_error_raises_if_badly_initialized():
    with pytest.raises(ValueError) as exc_info:
        raise PatternNotMatchedError('some string', patterns=())

    assert exc_info.value.args == ('At least one pattern must be provided',)
