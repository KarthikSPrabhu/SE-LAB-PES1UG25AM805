from hypothesis import given, strategies as st
from marathon_registration_parser import format_bib_name, parse_finish_time, average_split

@given(st.text() | st.none())
def test_format_bib_name_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_parse_finish_time_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_average_split_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass
