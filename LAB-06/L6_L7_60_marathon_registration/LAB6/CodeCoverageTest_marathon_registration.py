import pytest
from marathon_registration import entry_fee, start_wave, finisher_status


# =====================================================================
# Tests for entry_fee() - Statement / Code Coverage
# =====================================================================

def test_entry_fee_all_four_valid_races():
    """Verify standard fee calculation for all four valid race categories."""
    assert entry_fee("5k", 25, False, False) == 500
    assert entry_fee("10k", 25, False, False) == 800
    assert entry_fee("half", 25, False, False) == 1200
    assert entry_fee("full", 25, False, False) == 1800


def test_entry_fee_invalid_race():
    """Verify ValueError is raised when race category is unknown."""
    with pytest.raises(ValueError, match="unknown race"):
        entry_fee("ultra", 25, False, False)


def test_entry_fee_age_below_12():
    """Verify ValueError is raised when participant age is below 12."""
    with pytest.raises(ValueError, match="too young"):
        entry_fee("5k", 11, False, False)


def test_entry_fee_half_marathon_age_below_18():
    """Verify ValueError is raised for half marathon if age is below 18."""
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("half", 17, False, False)


def test_entry_fee_full_marathon_age_below_18():
    """Verify ValueError is raised for full marathon if age is below 18."""
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("full", 17, False, False)


def test_entry_fee_early_bird_discount():
    """Verify 25% early bird discount applies correctly."""
    # full: 1800 - 450 = 1350
    assert entry_fee("full", 30, True, False) == 1350
    # 10k: 800 - 200 = 600
    assert entry_fee("10k", 30, True, False) == 600


def test_entry_fee_senior_citizen_discount():
    """Verify 50% senior citizen discount applies for age >= 65."""
    # full: 1800 // 2 = 900
    assert entry_fee("full", 65, False, False) == 900
    # half: 1200 // 2 = 600
    assert entry_fee("half", 70, False, False) == 600


def test_entry_fee_tshirt_additional_charge():
    """Verify additional charge of 300 for T-shirt."""
    # 5k: 500 + 300 = 800
    assert entry_fee("5k", 25, False, True) == 800


def test_entry_fee_combination_early_bird_and_senior():
    """Verify combination of early bird and senior citizen discounts."""
    # full: 1800 -> 1350 -> 675
    assert entry_fee("full", 65, True, False) == 675
    # 10k: 800 -> 600 -> 300
    assert entry_fee("10k", 70, True, False) == 300


def test_entry_fee_combination_discounts_and_tshirt():
    """Verify combination of both discounts and T-shirt charge."""
    # full: 1800 -> 1350 -> 675 + 300 = 975
    assert entry_fee("full", 65, True, True) == 975
    # half: 1200 -> 900 -> 450 + 300 = 750
    assert entry_fee("half", 65, True, True) == 750


def test_entry_fee_boundary_ages():
    """Verify boundary ages: 12 (min valid), 17 (valid for 5k/10k), 18 (min for half/full), 64/65 (senior)."""
    # Boundary 12: minimum valid age for 5k
    assert entry_fee("5k", 12, False, False) == 500

    # Boundary 17: valid for 5k and 10k, invalid for half and full
    assert entry_fee("5k", 17, False, False) == 500
    assert entry_fee("10k", 17, False, False) == 800
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("half", 17, False, False)
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("full", 17, False, False)

    # Boundary 18: eligible for half and full
    assert entry_fee("half", 18, False, False) == 1200
    assert entry_fee("full", 18, False, False) == 1800

    # Boundary 64 vs 65: senior discount cutoff
    assert entry_fee("full", 64, False, False) == 1800
    assert entry_fee("full", 65, False, False) == 900


# =====================================================================
# Tests for start_wave() - Statement / Code Coverage
# =====================================================================

def test_start_wave_none_timing():
    """Verify first-timer or timing None runner gets assigned to Wave D."""
    assert start_wave(None, "full") == "D"
    assert start_wave(None, "10k") == "D"


def test_start_wave_wave_a_full_marathon():
    """Verify Wave A assignment for full marathon (time <= 75% of 240 = 180)."""
    assert start_wave(170, "full") == "A"


def test_start_wave_wave_a_other_races():
    """Verify Wave A assignment for non-full races (time <= 75% of 120 = 90)."""
    assert start_wave(80, "half") == "A"
    assert start_wave(70, "10k") == "A"


def test_start_wave_wave_b_full_marathon():
    """Verify Wave B assignment for full marathon (180 < time <= 240)."""
    assert start_wave(200, "full") == "B"


def test_start_wave_wave_b_other_races():
    """Verify Wave B assignment for other races (90 < time <= 120)."""
    assert start_wave(110, "half") == "B"
    assert start_wave(105, "10k") == "B"


def test_start_wave_wave_c_full_marathon():
    """Verify Wave C assignment for full marathon (time > 240)."""
    assert start_wave(250, "full") == "C"


def test_start_wave_wave_c_other_races():
    """Verify Wave C assignment for other races (time > 120)."""
    assert start_wave(130, "half") == "C"
    assert start_wave(150, "5k") == "C"


def test_start_wave_exact_cutoff_boundaries():
    """Verify exact cutoff boundaries: 240 for full, 120 for others."""
    # Full marathon cutoff boundary at 240
    assert start_wave(240, "full") == "B"
    assert start_wave(241, "full") == "C"

    # Other races cutoff boundary at 120
    assert start_wave(120, "half") == "B"
    assert start_wave(121, "half") == "C"


def test_start_wave_exact_75_percent_cutoff_boundaries():
    """Verify exact 75% cutoff boundaries: 180 for full, 90 for others."""
    # Full marathon 75% boundary: 180 vs 181
    assert start_wave(180, "full") == "A"
    assert start_wave(181, "full") == "B"

    # Other races 75% boundary: 90 vs 91
    assert start_wave(90, "half") == "A"
    assert start_wave(91, "half") == "B"


# =====================================================================
# Tests for finisher_status() - Statement / Code Coverage
# =====================================================================

def test_finisher_status_disqualified_when_checkpoints_missed():
    """Verify DSQ when checkpoints are missed regardless of time."""
    assert finisher_status(200, "full", 1) == "DSQ"
    assert finisher_status(60, "10k", 2) == "DSQ"


def test_finisher_status_within_full_marathon_limit():
    """Verify finisher status within full marathon limit of 360 minutes."""
    assert finisher_status(300, "full", 0) == "finisher"


def test_finisher_status_beyond_full_marathon_limit():
    """Verify DNF status beyond full marathon limit of 360 minutes."""
    assert finisher_status(400, "full", 0) == "DNF"


def test_finisher_status_within_half_marathon_limit():
    """Verify finisher status within half marathon limit of 180 minutes."""
    assert finisher_status(150, "half", 0) == "finisher"


def test_finisher_status_beyond_half_marathon_limit():
    """Verify DNF status beyond half marathon limit of 180 minutes."""
    assert finisher_status(190, "half", 0) == "DNF"


def test_finisher_status_within_other_race_limits():
    """Verify finisher status within other race limits of 90 minutes."""
    assert finisher_status(60, "10k", 0) == "finisher"
    assert finisher_status(45, "5k", 0) == "finisher"


def test_finisher_status_beyond_other_race_limits():
    """Verify DNF status beyond other race limits of 90 minutes."""
    assert finisher_status(100, "10k", 0) == "DNF"
    assert finisher_status(95, "5k", 0) == "DNF"


def test_finisher_status_exact_time_limit_boundaries():
    """Verify exact time-limit boundaries for all race categories."""
    # Full marathon limit: 360 vs 361
    assert finisher_status(360, "full", 0) == "finisher"
    assert finisher_status(361, "full", 0) == "DNF"

    # Half marathon limit: 180 vs 181
    assert finisher_status(180, "half", 0) == "finisher"
    assert finisher_status(181, "half", 0) == "DNF"

    # Other races limit: 90 vs 91
    assert finisher_status(90, "10k", 0) == "finisher"
    assert finisher_status(91, "10k", 0) == "DNF"

