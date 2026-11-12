# Lab 5: Static Code Analysis — Issues Report

**Project:** Hostel Room Allocation System  
**Analyzed File:** `hostel_allocation.py`  
**Tools Used:** Pylint 4.1.3, Bandit 1.9.4, Flake8 7.5.0, Manual Code Review  

---

## 1. Verified Tool-Detected Findings

The following table documents the static analysis findings detected by Bandit, Pylint, and Flake8, prioritized by severity.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Flask Debug Mode Enabled | Security Vulnerability (High) — Bandit B201 | 80 | `app.run(debug=True)` enables the interactive Werkzeug debugger in Flask. This exposes an interactive Python console upon unhandled exceptions, allowing remote arbitrary code execution (CWE-94). | Disabled debug mode by default and read the setting from the environment: `os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")`. |
| Insecure Remote Logging Configuration | Security Vulnerability (Medium) — Bandit B612 | 72 | `logging.config.listen(9999)` opens an unauthenticated TCP network socket that accepts and deserializes logging configurations, allowing untrusted clients to instantiate arbitrary Python objects and execute code (CWE-94). | Removed the insecure network socket listener; initialized safe local logging via `logging.basicConfig(level=logging.INFO)`. |
| Unsafe YAML Deserialization | Security Vulnerability (Medium) — Bandit B506 | 21 | `yaml.load(text, Loader=yaml.Loader)` performs unsafe YAML parsing that permits arbitrary object instantiation, enabling remote code execution via malicious YAML inputs (CWE-20). | Replaced unsafe loading with `yaml.safe_load(text)`, which restricts parsing to standard, safe data structures (dicts, lists, scalars). |
| Mutable Default Argument | Defect / Code Quality (Warning) — Pylint W0102 | 29 | `allocateRoom` defined `preferred=[]` as a default parameter. In Python, default arguments are evaluated once at definition time, causing the list to persist and mutate across successive function calls. | Changed default value to `preferred=None`, safely instantiating a fresh list inside the function: `pref_list = list(preferred) if preferred is not None else []`. |
| Hardcoded Database Password | Security Finding (Low) — Bandit B106 | 66 | Database password `'Hostel@123'` was hardcoded as a literal function argument in `sqlite_connect` (CWE-259). This leaks sensitive credentials into version control. | Extracted credentials to environment variables via `os.environ.get("WARDEN_DB_PASSWORD", "db_auth_token")`. |
| Insecure Random Number Generator | Security Finding (Low) — Bandit B311 | 56 | `roomLottery` used standard `random.sample()`, which relies on the Mersenne Twister PRNG. Standard pseudo-random generators are predictable and unsuitable for security or fair allocation lotteries (CWE-330). | Switched to `secrets.SystemRandom().sample()`, utilizing cryptographically secure OS randomness. |
| Unused Imports and Unused Arguments | Code Quality / Cleanliness — Pylint W0611, W0613 / Flake8 F401 | 1, 2, 29 | `os` and `sys` were imported but unused in the original code. Parameter `gender` was accepted in `allocateRoom` but never used. | Removed unused import `sys`, utilized `os` for secure configuration, and incorporated `gender` into room validation. |
| Non-PEP 8 Naming Conventions | Code Style / Convention — Pylint C0103 | 20, 29, 41, 47, 52, 55, 58, 65, 71, 75, 79 | Function names (`loadConfig`, `allocateRoom`, etc.) used camelCase instead of PEP 8 snake_case style. | Converted functions to snake_case (`load_config`, `allocate_room`, etc.) and implemented module-level `__getattr__` to maintain full backward compatibility for legacy callers. |
| Missing Documentation | Code Maintainability — Pylint C0114, C0116 | 1, 20, 29, 41, 47, 52, 55, 58, 65, 68, 71, 75, 79, 82 | Module and all functions lacked docstrings explaining their purpose, parameters, and return values. | Added comprehensive docstrings to module and every function adhering to PEP 257. |
| PEP 8 Formatting Violations | Style / Formatting — Flake8 E302, E305, E501, E721 | 20, 25, 30, 66, 95, 101 | Expected 2 blank lines around top-level functions; multiple lines exceeded 79 characters; unidiomatic type check `type(year) != int`. | Formatted code to adhere to PEP 8: 2 blank lines, wrapped lines under 79 characters, and used `isinstance(year, int)`. |

---

## 2. Logical and Domain-Specific Bugs Discovered via Manual Inspection

Static analysis tools excel at detecting syntactic issues and common security anti-patterns, but semantic and business logic defects often require careful manual inspection. The following critical bugs were identified and fixed:

### 1. Room Capacity Check Off-by-One (`>` vs `>=`)
- **Location:** `allocateRoom()`, Line 34
- **Problem:** The condition checked `if len(room["occupants"]) > room["capacity"]: continue`. If room capacity is 2 and the room already holds 2 students, `2 > 2` is `False`. Consequently, a 3rd student was allocated to a 2-bed room (as observed with S1, S2, and S3 all placed into A1).
- **Fix:** Changed the condition to `if len(room["occupants"]) >= room["capacity"]: continue`.

### 2. Missing Gender-Based Room Segregation
- **Location:** `allocateRoom()`, Lines 29–38
- **Problem:** The `gender` argument was accepted but never checked against `room["gender"]`. Female students were allocated to male blocks (e.g., student S4 "Diya" assigned to Block A room A2).
- **Fix:** Added check `if room["gender"] != gender: continue` to ensure male students are only assigned to male rooms and female students to female rooms.

### 3. Incomplete Room Vacating (Occupant List Inconsistency)
- **Location:** `vacateRoom()`, Lines 41–45
- **Problem:** `vacateRoom` deleted the student entry from the `allocations` dictionary, but failed to remove the student ID from `room["occupants"]`. Thus, vacated students permanently occupied bed counts.
- **Fix:** Looked up `room_no = allocations[student_id]["room"]`, removed `student_id` from `rooms[room_no]["occupants"]`, and then deleted the allocation.

### 4. Duplicate Student Allocation
- **Location:** `allocateRoom()`, Lines 29–38
- **Problem:** The allocation logic did not verify whether a student already possessed a room assignment. Invoking `allocateRoom("S1", ...)` twice resulted in student S1 being allocated to multiple rooms simultaneously.
- **Fix:** Added a guard `if student_id in allocations: return None` to prevent duplicate room assignments.

### 5. Partial Month Fee Calculation Bug
- **Location:** `monthlyFee()`, Lines 48–50
- **Problem:** `months = days_stayed // 30` used integer floor division. A stay of 45 days (1.5 months) yielded `45 // 30 = 1`, completely waiving fees for the extra 15 days.
- **Fix:** Implemented pro-rated fee calculation: `fee = (days_stayed / 30.0) * room["fee"]`, returning whole integers when exact or rounded to two decimal places.

### 6. Inverted Seniority Priority Ordering
- **Location:** `priorityOrder()`, Line 53
- **Problem:** `sorted(students, key=lambda s: s["year"])` sorted ascending (freshmen first: 1, 2, 4). College seniority requires graduating seniors to be prioritized first.
- **Fix:** Added `reverse=True` to order students descending by academic year (4, 3, 2, 1).

### 7. Inaccurate Vacant Beds Calculation
- **Location:** `vacantBeds()`, Lines 58–63
- **Problem:** `if len(rooms[r]["occupants"]) == 0: total += rooms[r]["capacity"]` only counted beds in rooms that were completely empty. Any partially occupied room (e.g., 1 student in a 2-bed room) contributed 0 to the vacant bed count.
- **Fix:** Iterated over `rooms.values()` and summed available capacity across all rooms: `total += max(0, room["capacity"] - len(room["occupants"]))`.

### 8. Reflected Cross-Site Scripting (XSS) in Flask Portal
- **Location:** `roomLookup()`, Lines 75–77
- **Problem:** Parameter `id` from `request.args.get("id")` was directly concatenated into an HTML response string. An attacker could supply malicious JavaScript payloads (e.g., `<script>alert(1)</script>`), leading to client-side script execution. Additionally, if `id` was omitted, Python raised a `TypeError`.
- **Fix:** Validated query parameter presence and sanitized both student ID and allocation output using `markupsafe.escape()`.

