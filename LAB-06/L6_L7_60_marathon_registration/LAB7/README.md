# L6_L7_60 — Marathon Registration

Lab 7: Fuzzing for Input Validation Bugs

## About

A small Python module that reads marathon registration details typed in by a user: bib names, finish times and split times. It assumes every input is well formed.

## Files

| File | Description |
|------|-------------|
| `marathon_registration_parser.py` | The buggy module you will fuzz and fix |
| `test_marathon_registration_parser.py` | Hypothesis test template to complete |

Keep all your Lab 7 work in this `LAB7` folder.

Follow the lab handout for the full instructions. Use the file names above wherever the handout refers to the code and test files.

## Screenshots

| Screenshot | What it must show |
|------------|-------------------|
| SS1 | `python marathon_registration_parser.py` run on the buggy module |
| SS2 | `pytest test_marathon_registration_parser.py` with your completed tests failing on the buggy module |
| SS3 | `python marathon_registration_parser.py` run on your fixed module |
| SS4 | `pytest test_marathon_registration_parser.py` with all tests passing on your fixed module |

## Deliverables

Commit these three files in this `LAB7` folder:

1. `marathon_registration_parser.py`: your fixed module. All three functions must handle any input without crashing.
2. `test_marathon_registration_parser.py`: your completed Hypothesis tests, one for each of the three functions.
3. `SRN_NAME_LAB7.pdf`: screenshots SS1 to SS4 and your answers to the three reflection questions in the handout.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.
