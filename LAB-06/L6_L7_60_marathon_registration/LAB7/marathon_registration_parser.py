def format_bib_name(name):
    """
    Upper-cases a runner's name and cuts it to 12 characters for the bib.
    Assumes name is a non-empty string.
    """
    return name.strip().upper()[:12]

def parse_finish_time(text):
    """
    Converts a finish time written as H:MM:SS into seconds.
    Assumes text has exactly three numeric parts.
    """
    hours, minutes, seconds = text.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

def average_split(text):
    """
    Averages split times given in minutes, separated by spaces.
    Assumes at least one split and that every split is a whole number.
    """
    splits = [int(s) for s in text.split()]
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
