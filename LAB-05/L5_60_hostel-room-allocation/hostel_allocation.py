"""Hostel Room Allocation System.

Provides functionality for loading hostel block configurations,
allocating rooms based on gender and capacity, vacating rooms,
calculating monthly and partial fees, ordering students by seniority,
running room lotteries, and querying room assignments via a web portal.
"""

import os
import secrets
import logging
import yaml
from flask import Flask, request
from markupsafe import escape

# Global hostel state
rooms = {}
allocations = {}
waitlist = []
app = Flask(__name__)

CONFIG = """
blocks:
  A: {gender: M, rooms: 3, capacity: 2, fee: 4000}
  B: {gender: F, rooms: 2, capacity: 3, fee: 3500}
"""


def load_config(text=CONFIG):
    """Load hostel room configurations from YAML text and initialize rooms."""
    config = yaml.safe_load(text)
    rooms.clear()
    for block, info in config.get("blocks", {}).items():
        for n in range(1, info["rooms"] + 1):
            rooms[f"{block}{n}"] = {
                "gender": info["gender"],
                "capacity": info["capacity"],
                "fee": info["fee"],
                "occupants": [],
            }
    return config


def allocate_room(student_id, name, gender, year, preferred=None):
    """Allocate a room to a student.

    Adheres to room capacity, gender segregation, and uniqueness.
    """
    if not isinstance(year, int) or year <= 0:
        return None
    if not student_id or not name or gender not in ("M", "F"):
        return None
    if student_id in allocations:
        return None

    pref_list = list(preferred) if preferred is not None else []
    candidate_rooms = []
    for r in pref_list:
        if r in rooms and r not in candidate_rooms:
            candidate_rooms.append(r)
    for r in rooms:
        if r not in candidate_rooms:
            candidate_rooms.append(r)

    for room_no in candidate_rooms:
        room = rooms[room_no]
        if room["gender"] != gender:
            continue
        if len(room["occupants"]) >= room["capacity"]:
            continue
        room["occupants"].append(student_id)
        allocations[student_id] = {
            "name": name,
            "room": room_no,
            "year": year,
            "gender": gender,
        }
        if student_id in waitlist:
            waitlist.remove(student_id)
        return room_no

    if student_id not in waitlist:
        waitlist.append(student_id)
    return None


def vacate_room(student_id):
    """Vacate an allocated student from their assigned room and records."""
    if student_id in allocations:
        room_no = allocations[student_id]["room"]
        if room_no in rooms and student_id in rooms[room_no]["occupants"]:
            rooms[room_no]["occupants"].remove(student_id)
        del allocations[student_id]
        return True
    return False


def monthly_fee(student_id, days_stayed):
    """Calculate the hostel fee based on days stayed.

    Partial months are pro-rated accordingly.
    """
    if student_id not in allocations or days_stayed < 0:
        return 0
    room = rooms[allocations[student_id]["room"]]
    fee = (days_stayed / 30.0) * room["fee"]
    return int(fee) if fee.is_integer() else round(fee, 2)


def priority_order(students):
    """Order students by seniority in descending order (highest year first)."""
    return sorted(students, key=lambda s: s["year"], reverse=True)


def room_lottery(student_ids):
    """Randomly shuffle a list of student IDs.

    Uses a cryptographically secure random generator.
    """
    rng = secrets.SystemRandom()
    return rng.sample(student_ids, len(student_ids))


def vacant_beds():
    """Calculate total number of available beds across all hostel rooms."""
    total = 0
    for room in rooms.values():
        total += max(0, room["capacity"] - len(room["occupants"]))
    return total


def connect_warden_db():
    """Connect to the warden database using configured credentials."""
    db_password = os.environ.get("WARDEN_DB_PASSWORD", "db_auth_token")
    return sqlite_connect(
        host="localhost", user="warden", password=db_password
    )


def sqlite_connect(host, user, password):
    """Simulate establishing a database connection."""
    return {"host": host, "user": user, "connected": len(password) > 0}


def start_remote_log_config():
    """Initialize safe local logging configuration."""
    logging.basicConfig(level=logging.INFO)


@app.route("/room")
def room_lookup():
    """Look up allocated room details for a student.

    Query parameters are sanitized against XSS.
    """
    sid = request.args.get("id")
    if not sid:
        return "<h1>Error: Missing student ID</h1>", 400
    safe_sid = escape(sid)
    safe_alloc = escape(str(allocations.get(sid)))
    return f"<h1>Room for {safe_sid}: {safe_alloc}</h1>"


def run_portal():
    """Start the Flask web portal with debug mode disabled by default."""
    debug_mode = (
        os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
    )
    app.run(debug=debug_mode)


def main():
    """Demonstrate the hostel room allocation workflow and verify outputs."""
    load_config()
    print("Rooms:", list(rooms.keys()))
    print("S1 ->", allocate_room("S1", "Arjun", "M", 1))
    print("S2 ->", allocate_room("S2", "Kabir", "M", 2))
    print("S3 ->", allocate_room("S3", "Rohan", "M", 3))
    print("S4 (female) ->", allocate_room("S4", "Diya", "F", 1))
    print("S1 again ->", allocate_room("S1", "Arjun", "M", 1))
    print("S5 year '2' ->", allocate_room("S5", "Vikram", "M", "2"))
    print("Occupants of A1:", rooms["A1"]["occupants"])
    vacate_room("S2")
    print("Occupants of A1 after S2 left:", rooms["A1"]["occupants"])
    print("Fee for S1, 45 days:", monthly_fee("S1", 45))
    print(
        "Priority (seniors first?):",
        [
            s["year"]
            for s in priority_order(
                [{"year": 1}, {"year": 4}, {"year": 2}]
            )
        ],
    )
    print("Lottery:", room_lottery(["S6", "S7", "S8"]))
    print("Vacant beds:", vacant_beds())
    print("Warden DB:", connect_warden_db())
    print("Waitlist:", waitlist)


def __getattr__(name):
    """Provide backward compatibility for legacy camelCase function names."""
    legacy_aliases = {
        "loadConfig": load_config,
        "allocateRoom": allocate_room,
        "vacateRoom": vacate_room,
        "monthlyFee": monthly_fee,
        "priorityOrder": priority_order,
        "roomLottery": room_lottery,
        "vacantBeds": vacant_beds,
        "connectWardenDb": connect_warden_db,
        "startRemoteLogConfig": start_remote_log_config,
        "roomLookup": room_lookup,
        "runPortal": run_portal,
    }
    if name in legacy_aliases:
        return legacy_aliases[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if __name__ == "__main__":
    main()
