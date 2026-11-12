import pytest
from marathon_registration import entry_fee, start_wave, finisher_status

#Example test cases:
def test_10k_standard():
    assert entry_fee("10k", 30, False, False) == 800

def test_first_timer_wave():
    assert start_wave(None, "full") == "D"

#Write the rest of the test cases so that the code is 90- 100% covered.
