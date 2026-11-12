import pytest
from marathon_registration import entry_fee, start_wave, finisher_status


# =====================================================================
# Branch Coverage Tests for entry_fee()
# =====================================================================

def test_branch_entry_fee_race_not_in_entry_fee_true():
    """Branch: if race not in ENTRY_FEE -> True (raises ValueError)."""
    with pytest.raises(ValueError, match="unknown race"):
        entry_fee("unknown_race", 25, False, False)


def test_branch_entry_fee_race_not_in_entry_fee_false():
    """Branch: if race not in ENTRY_FEE -> False (continues to age validation)."""
    assert entry_fee("5k", 25, False, False) == 500


def test_branch_entry_fee_age_below_12_true():
    """Branch: if age < 12 -> True (raises ValueError)."""
    with pytest.raises(ValueError, match="too young"):
        entry_fee("5k", 11, False, False)


def test_branch_entry_fee_age_below_12_false():
    """Branch: if age < 12 -> False (proceeds past age check)."""
    assert entry_fee("5k", 12, False, False) == 500


def test_branch_entry_fee_half_full_and_under_18_both_true():
    """Branch: if race in ('half', 'full') and age < 18 -> True (raises ValueError).
    Evaluates condition when both left and right conjuncts are True.
    """
    # half marathon with age 17 (< 18)
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("half", 17, False, False)

    # full marathon with age 17 (< 18)
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("full", 17, False, False)


def test_branch_entry_fee_half_full_true_but_age_under_18_false():
    """Branch: if race in ('half', 'full') and age < 18 -> False (age >= 18).
    Evaluates condition when race is half/full (True) but age < 18 is False.
    """
    assert entry_fee("half", 18, False, False) == 1200
    assert entry_fee("full", 18, False, False) == 1800


def test_branch_entry_fee_half_full_false():
    """Branch: if race in ('half', 'full') and age < 18 -> False (race is not half/full).
    Evaluates condition when race is not half/full, testing short-circuit / false branch
    for runners under 18 and over 18.
    """
    # 5k and 10k runners who are under 18 (e.g., 14) are allowed
    assert entry_fee("5k", 14, False, False) == 500
    assert entry_fee("10k", 16, False, False) == 800

    # 5k and 10k runners who are 18 or older
    assert entry_fee("5k", 25, False, False) == 500
    assert entry_fee("10k", 25, False, False) == 800


def test_branch_entry_fee_is_early_bird_true_and_false():
    """Branch: if is_early_bird -> True vs False."""
    # False: no early bird discount
    assert entry_fee("full", 30, False, False) == 1800
    # True: early bird discount applied (1800 - 450 = 1350)
    assert entry_fee("full", 30, True, False) == 1350


def test_branch_entry_fee_senior_citizen_true_and_false():
    """Branch: if age >= 65 -> True vs False."""
    # False: age 64 (just below senior threshold) -> no discount
    assert entry_fee("full", 64, False, False) == 1800
    # True: age 65 (exact threshold) -> 50% discount
    assert entry_fee("full", 65, False, False) == 900
    # True: age 75 (> threshold) -> 50% discount
    assert entry_fee("half", 75, False, False) == 600


def test_branch_entry_fee_needs_tshirt_true_and_false():
    """Branch: if needs_tshirt -> True vs False."""
    # False: no T-shirt charge
    assert entry_fee("10k", 30, False, False) == 800
    # True: T-shirt charge of 300 added
    assert entry_fee("10k", 30, False, True) == 1100


def test_branch_entry_fee_all_modifiers_combined():
    """Branch: exercise combination where early_bird=True, senior=True, needs_tshirt=True."""
    # full: 1800 -> early_bird(1350) -> senior(675) -> tshirt(975)
    assert entry_fee("full", 65, True, True) == 975
    # half: 1200 -> early_bird(900) -> senior(450) -> tshirt(750)
    assert entry_fee("half", 70, True, True) == 750


# =====================================================================
# Branch Coverage Tests for start_wave()
# =====================================================================

def test_branch_start_wave_timing_none_true_and_false():
    """Branch: if best_time_minutes is None -> True vs False."""
    # True: timing is None -> wave "D"
    assert start_wave(None, "full") == "D"
    assert start_wave(None, "half") == "D"

    # False: timing is provided -> proceeds to wave determination
    assert start_wave(150, "full") != "D"


def test_branch_start_wave_race_full_true_and_false():
    """Branch: if race == 'full' -> True (cutoff=240) vs False (cutoff=120)."""
    # True: race is "full" -> cutoff is 240
    # 240 is Wave B for full; for other races 240 would be Wave C (240 > 120)
    assert start_wave(240, "full") == "B"

    # False: race is not "full" -> cutoff is 120
    assert start_wave(120, "half") == "B"
    assert start_wave(120, "10k") == "B"


def test_branch_start_wave_wave_a_condition_true_and_false_full():
    """Branch: if best_time_minutes * 4 <= cutoff * 3 -> True vs False (full marathon).
    For full marathon cutoff = 240, cutoff * 3 / 4 = 180.
    """
    # True: time <= 180 -> Wave A
    assert start_wave(180, "full") == "A"
    assert start_wave(175, "full") == "A"

    # False: time > 180 -> proceeds to elif (Wave B or C)
    assert start_wave(181, "full") == "B"


def test_branch_start_wave_wave_a_condition_true_and_false_non_full():
    """Branch: if best_time_minutes * 4 <= cutoff * 3 -> True vs False (other races).
    For other races cutoff = 120, cutoff * 3 / 4 = 90.
    """
    # True: time <= 90 -> Wave A
    assert start_wave(90, "half") == "A"
    assert start_wave(85, "10k") == "A"

    # False: time > 90 -> proceeds to elif (Wave B or C)
    assert start_wave(91, "half") == "B"


def test_branch_start_wave_wave_b_elif_condition_true_and_false_full():
    """Branch: elif best_time_minutes <= cutoff -> True vs False (full marathon).
    For full marathon cutoff = 240.
    """
    # True: 180 < time <= 240 -> Wave B
    assert start_wave(240, "full") == "B"
    assert start_wave(210, "full") == "B"

    # False: time > 240 -> Wave C
    assert start_wave(241, "full") == "C"
    assert start_wave(300, "full") == "C"


def test_branch_start_wave_wave_b_elif_condition_true_and_false_non_full():
    """Branch: elif best_time_minutes <= cutoff -> True vs False (other races).
    For other races cutoff = 120.
    """
    # True: 90 < time <= 120 -> Wave B
    assert start_wave(120, "half") == "B"
    assert start_wave(100, "10k") == "B"

    # False: time > 120 -> Wave C
    assert start_wave(121, "half") == "C"
    assert start_wave(150, "5k") == "C"


# =====================================================================
# Branch Coverage Tests for finisher_status()
# =====================================================================

def test_branch_finisher_status_checkpoints_missed_true_and_false():
    """Branch: if checkpoints_missed > 0 -> True (DSQ) vs False (continues)."""
    # True: checkpoints missed > 0 -> DSQ
    assert finisher_status(100, "full", 1) == "DSQ"
    assert finisher_status(50, "half", 3) == "DSQ"

    # False: checkpoints missed == 0 -> proceeds
    assert finisher_status(350, "full", 0) == "finisher"


def test_branch_finisher_status_race_full_true_and_false():
    """Branch: if race == 'full' -> True (limit=360) vs False (proceeds to elif)."""
    # True: full marathon -> limit is 360
    assert finisher_status(360, "full", 0) == "finisher"
    assert finisher_status(361, "full", 0) == "DNF"

    # False: not full marathon -> proceeds to elif race == 'half'
    assert finisher_status(180, "half", 0) == "finisher"


def test_branch_finisher_status_race_half_true_and_false():
    """Branch: elif race == 'half' -> True (limit=180) vs False (limit=90)."""
    # True: half marathon -> limit is 180
    assert finisher_status(180, "half", 0) == "finisher"
    assert finisher_status(181, "half", 0) == "DNF"

    # False: other race categories -> limit is 90
    assert finisher_status(90, "10k", 0) == "finisher"
    assert finisher_status(91, "10k", 0) == "DNF"
    assert finisher_status(90, "5k", 0) == "finisher"
    assert finisher_status(91, "5k", 0) == "DNF"


def test_branch_finisher_status_elapsed_within_limit_true_and_false():
    """Branch: if elapsed_minutes <= limit -> True ('finisher') vs False ('DNF')."""
    # True: within or equal to limit -> 'finisher'
    assert finisher_status(300, "full", 0) == "finisher"
    assert finisher_status(150, "half", 0) == "finisher"
    assert finisher_status(60, "10k", 0) == "finisher"

    # False: strictly greater than limit -> 'DNF'
    assert finisher_status(361, "full", 0) == "DNF"
    assert finisher_status(181, "half", 0) == "DNF"
    assert finisher_status(91, "10k", 0) == "DNF"

