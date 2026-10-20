HARBORFLOW PORT INTELLIGENCE CONSOLE - TEAM README

Run instructions
----------------
Command: python3 main.py
Python version tested: Python 3.13.14

Team members and concrete contributions
---------------------------------------
Name: Hannes Lindberg
Contribution:
- GitHub initiation
- Task 0
- Task 3
- Task 4

Name: Hugo Karlsson
Contribution:
- Tasks 1 
- Task 2


Name: Brian Rauch
Contribution:
- Task 5 and Task 6



Name: Aytunch Tuzdzhu
Contribution:
- Task 7
- Task 8
- Task 9

Architecture
------------
main.py responsibilities: Menu loop and orchestration.
data_access.py responsibilities: All file access.
operations.py responsibilities: Business logic.
text_tools.py responsibilities: Text and sequence algorithms.

File and error-handling design
------------------------------
How paths are resolved:
- All paths are relative to the project root
- pathlib.Path is used to find files with glob("*.json")

How malformed or missing input is handled:
- Expected problems are caught where a useful response is possible: json.JSONDecodeError, FileNotFoundError and ValueError.
- A bad file or row is skipped without stopping later valid records.
- User input is checked in loops that repeat only the failing prompt.

How generated files are updated safely:
- The incident index is written with json.dump with sorted keys and sorted ID lists.
- It is reused only if it exists, is valid JSON with the keys "index" and "titles", and is newer than every incident file.
- Otherwise it is rebuilt and saved again.
- A corrupt cache repairs itself.

Known limitations
- Task 1 must be run before task 2.
- Task 9 indexes every word, such as "a" or "gate".

