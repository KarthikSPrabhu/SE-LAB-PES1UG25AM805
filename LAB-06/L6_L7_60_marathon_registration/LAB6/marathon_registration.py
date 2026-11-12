ENTRY_FEE = {"5k": 500, "10k": 800, "half": 1200, "full": 1800}


def entry_fee(race, age, is_early_bird, needs_tshirt):
    if race not in ENTRY_FEE:
        raise ValueError("unknown race")
    if age < 12:
        raise ValueError("too young")
    if race in ("half", "full") and age < 18:
        raise ValueError("too young for this distance")
    fee = ENTRY_FEE[race]
    if is_early_bird:
        fee -= fee // 4
    if age >= 65:
        fee = fee // 2
    if needs_tshirt:
        fee += 300
    return fee


def start_wave(best_time_minutes, race):
    if best_time_minutes is None:
        return "D"
    if race == "full":
        cutoff = 240
    else:
        cutoff = 120
    if best_time_minutes * 4 <= cutoff * 3:
        return "A"
    elif best_time_minutes <= cutoff:
        return "B"
    return "C"


def finisher_status(elapsed_minutes, race, checkpoints_missed):
    if checkpoints_missed > 0:
        return "DSQ"
    if race == "full":
        limit = 360
    elif race == "half":
        limit = 180
    else:
        limit = 90
    if elapsed_minutes <= limit:
        return "finisher"
    return "DNF"
