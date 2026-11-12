import pytest
from hypothesis import given, strategies as st
from marathon_registration_parser import format_bib_name, parse_finish_time, average_split


@given(st.text() | st.none())
def test_format_bib_name_no_crash(s):
    """
    Hypothesis fuzz test for format_bib_name.
    Ensures arbitrary strings and None never cause unexpected crashes
    and preserve return type and truncation invariants.
    """
    try:
        result = format_bib_name(s)
    except Exception as e:
        pytest.fail(f"format_bib_name crashed on input {s!r} with {type(e).__name__}: {e}")
    assert isinstance(result, str), f"Expected str return type, got {type(result).__name__}"
    assert len(result) <= 12, f"Expected bib name length <= 12, got length {len(result)}"
    assert result == result.upper(), f"Expected uppercase bib name, got {result!r}"


@given(st.text() | st.none())
def test_parse_finish_time_no_crash(s):
    """
    Hypothesis fuzz test for parse_finish_time.
    Ensures arbitrary strings and None never cause unhandled exceptions
    and return a non-negative integer or safe None fallback.
    """
    try:
        result = parse_finish_time(s)
    except Exception as e:
        pytest.fail(f"parse_finish_time crashed on input {s!r} with {type(e).__name__}: {e}")
    assert result is None or (isinstance(result, int) and result >= 0), (
        f"Expected None or non-negative int, got {result!r} of type {type(result).__name__}"
    )


@given(st.text() | st.none())
def test_average_split_no_crash(s):
    """
    Hypothesis fuzz test for average_split.
    Ensures arbitrary strings and None never cause unhandled exceptions
    and return a non-negative number or safe None fallback.
    """
    try:
        result = average_split(s)
    except Exception as e:
        pytest.fail(f"average_split crashed on input {s!r} with {type(e).__name__}: {e}")
    assert result is None or (isinstance(result, (int, float)) and result >= 0), (
        f"Expected None or non-negative float/int, got {result!r} of type {type(result).__name__}"
    )
