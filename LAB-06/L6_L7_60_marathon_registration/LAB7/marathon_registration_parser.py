def format_bib_name(name):
    """
    Upper-cases a runner's name and cuts it to 12 characters for the bib.
    Handles None, non-string, empty strings, and whitespace safely.
    Fallback: returns "" (empty string) for invalid or empty input.
    """
    if not isinstance(name, str):
        return ""
    cleaned = name.strip()
    if not cleaned:
        return ""
    return cleaned.upper()[:12]


def parse_finish_time(text):
    """
    Converts a finish time written as H:MM:SS into total seconds.
    Validates structure, non-negative hours, minutes (0-59), and seconds (0-59).
    Fallback: returns None for invalid, malformed, or out-of-range inputs.
    """
    if not isinstance(text, str):
        return None
    parts = text.strip().split(':')
    if len(parts) != 3:
        return None
    hours_str, minutes_str, seconds_str = parts[0].strip(), parts[1].strip(), parts[2].strip()
    if not (hours_str.isdigit() and minutes_str.isdigit() and seconds_str.isdigit()):
        return None
    hours = int(hours_str)
    minutes = int(minutes_str)
    seconds = int(seconds_str)
    if hours < 0 or not (0 <= minutes < 60) or not (0 <= seconds < 60):
        return None
    return hours * 3600 + minutes * 60 + seconds


def average_split(text):
    """
    Averages split times given in minutes, separated by spaces.
    Validates non-empty input, numeric tokens, and positive split values.
    Prevents division by zero and rejects negative/invalid splits safely.
    Fallback: returns None for invalid, empty, or unparseable inputs.
    """
    if not isinstance(text, str):
        return None
    tokens = text.strip().split()
    if not tokens:
        return None
    splits = []
    for token in tokens:
        if not token.isdigit():
            return None
        val = int(token)
        if val <= 0:
            return None
        splits.append(val)
    if not splits:
        return None
    return sum(splits) / len(splits)


def main():
    print("==== Running format_bib_name ====")
    value = input("Enter the name to print on the bib: ")
    print("Bib name:", format_bib_name(value))

    print("\n==== Running parse_finish_time ====")
    value = input("Enter a finish time as H:MM:SS (e.g. 3:45:10): ")
    print("Finish time in seconds:", parse_finish_time(value))

    print("\n==== Running average_split ====")
    value = input("Enter your 5 km split times in minutes separated by spaces (e.g. 25 26 24): ")
    print("Average split (minutes):", average_split(value))


if __name__ == "__main__":
    main()
