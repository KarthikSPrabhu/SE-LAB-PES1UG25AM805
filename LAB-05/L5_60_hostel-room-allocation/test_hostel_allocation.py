"""Automated unit and security tests for hostel_allocation.py.

Covers functionality, business logic, security constraints, and edge cases.
"""

import pytest
import hostel_allocation as ha


@pytest.fixture(autouse=True)
def reset_hostel_state():
    """Reset the global hostel state before each test."""
    ha.rooms.clear()
    ha.allocations.clear()
    ha.waitlist.clear()
    ha.load_config()


def test_load_config():
    """Test configuration loading from YAML text."""
    assert "A1" in ha.rooms
    assert "A2" in ha.rooms
    assert "A3" in ha.rooms
    assert "B1" in ha.rooms
    assert "B2" in ha.rooms
    assert ha.rooms["A1"]["gender"] == "M"
    assert ha.rooms["A1"]["capacity"] == 2
    assert ha.rooms["B1"]["gender"] == "F"
    assert ha.rooms["B1"]["capacity"] == 3


def test_successful_allocation():
    """Test successful room allocation for male and female students."""
    room_m = ha.allocate_room("S101", "Aarav", "M", 2)
    assert room_m == "A1"
    assert "S101" in ha.allocations
    assert ha.allocations["S101"]["room"] == "A1"
    assert "S101" in ha.rooms["A1"]["occupants"]

    room_f = ha.allocate_room("S102", "Priya", "F", 2)
    assert room_f == "B1"
    assert "S102" in ha.allocations
    assert ha.allocations["S102"]["room"] == "B1"
    assert "S102" in ha.rooms["B1"]["occupants"]


def test_room_capacity_limits():
    """Test that room capacity limits are strictly enforced."""
    # A1 capacity is 2
    r1 = ha.allocate_room("S1", "Student 1", "M", 1, preferred=["A1"])
    r2 = ha.allocate_room("S2", "Student 2", "M", 1, preferred=["A1"])
    r3 = ha.allocate_room("S3", "Student 3", "M", 1, preferred=["A1"])

    assert r1 == "A1"
    assert r2 == "A1"
    # S3 should not be in A1 because A1 is full (capacity 2)
    assert r3 != "A1"
    assert len(ha.rooms["A1"]["occupants"]) == 2


def test_gender_based_allocation():
    """Test that students are only allocated to rooms matching their gender."""
    # Block A is Male, Block B is Female
    room_female = ha.allocate_room("SF1", "Ananya", "F", 1)
    assert room_female.startswith("B")
    assert ha.rooms[room_female]["gender"] == "F"

    room_male = ha.allocate_room("SM1", "Karan", "M", 1)
    assert room_male.startswith("A")
    assert ha.rooms[room_male]["gender"] == "M"


def test_duplicate_student_prevention():
    """Test that an already allocated student cannot be allocated again."""
    r1 = ha.allocate_room("S201", "Rohan", "M", 3)
    assert r1 == "A1"

    # Attempt second allocation
    r2 = ha.allocate_room("S201", "Rohan", "M", 3)
    assert r2 is None
    # Verify allocations and room occupants still only have 1 entry
    assert ha.rooms["A1"]["occupants"].count("S201") == 1


def test_invalid_student_data():
    """Test rejection of invalid student inputs."""
    # Invalid year types or values
    assert ha.allocate_room("S1", "Test", "M", "2") is None
    assert ha.allocate_room("S2", "Test", "M", 0) is None
    assert ha.allocate_room("S3", "Test", "M", -1) is None
    assert ha.allocate_room("S4", "Test", "M", 2.5) is None

    # Invalid gender
    assert ha.allocate_room("S5", "Test", "X", 2) is None

    # Missing student id or name
    assert ha.allocate_room("", "Test", "M", 2) is None
    assert ha.allocate_room("S6", "", "M", 2) is None


def test_vacate_room():
    """Test vacating an allocated room."""
    ha.allocate_room("S301", "Meera", "F", 4)
    assert "S301" in ha.allocations

    res = ha.vacate_room("S301")
    assert res is True
    assert "S301" not in ha.allocations
    assert "S301" not in ha.rooms["B1"]["occupants"]

    # Vacating a non-existent student returns False
    assert ha.vacate_room("NONEXISTENT") is False


def test_occupant_list_consistency():
    """Test that allocations and room occupant lists remain consistent."""
    ha.allocate_room("S1", "A", "M", 1)
    ha.allocate_room("S2", "B", "M", 2)
    assert ha.rooms["A1"]["occupants"] == ["S1", "S2"]

    ha.vacate_room("S1")
    assert ha.rooms["A1"]["occupants"] == ["S2"]
    assert "S1" not in ha.allocations

    ha.vacate_room("S2")
    assert ha.rooms["A1"]["occupants"] == []
    assert "S2" not in ha.allocations


def test_fee_calculations():
    """Test pro-rated monthly fee calculation for partial and full months."""
    ha.allocate_room("S1", "A", "M", 1)  # Room A1 fee is 4000
    # Exactly 1 month (30 days)
    assert ha.monthly_fee("S1", 30) == 4000
    # Exactly 2 months (60 days)
    assert ha.monthly_fee("S1", 60) == 8000
    # Partial month: 45 days -> 1.5 months = 6000
    assert ha.monthly_fee("S1", 45) == 6000
    # Partial month: 15 days -> 0.5 months = 2000
    assert ha.monthly_fee("S1", 15) == 2000
    # 0 days
    assert ha.monthly_fee("S1", 0) == 0
    # Unallocated student
    assert ha.monthly_fee("UNKNOWN", 30) == 0


def test_priority_ordering():
    """Test ordering students by seniority (highest year first)."""
    students = [
        {"name": "Freshman", "year": 1},
        {"name": "Senior", "year": 4},
        {"name": "Sophomore", "year": 2},
        {"name": "Junior", "year": 3},
    ]
    ordered = ha.priority_order(students)
    years = [s["year"] for s in ordered]
    assert years == [4, 3, 2, 1]


def test_room_lottery():
    """Test room lottery random shuffling."""
    students = [f"S{i}" for i in range(10)]
    lottery_result = ha.room_lottery(students)
    assert len(lottery_result) == len(students)
    assert set(lottery_result) == set(students)


def test_vacant_beds_calculation():
    """Test accurate vacant bed calculation across rooms."""
    # Total beds in config: 3*2 + 2*3 = 6 + 6 = 12
    assert ha.vacant_beds() == 12

    # Allocate 1 student to A1 (cap 2 -> 1 left)
    ha.allocate_room("S1", "A", "M", 1)
    assert ha.vacant_beds() == 11

    # Allocate 2nd student to A1 (cap 2 -> 0 left)
    ha.allocate_room("S2", "B", "M", 1)
    assert ha.vacant_beds() == 10

    # Allocate 1 student to B1 (cap 3 -> 2 left)
    ha.allocate_room("S3", "C", "F", 1)
    assert ha.vacant_beds() == 9


def test_flask_room_lookup_security():
    """Test Flask room lookup endpoint security against XSS."""
    ha.allocate_room("S1", "Arjun", "M", 1)
    client = ha.app.test_client()

    # Normal lookup
    res = client.get("/room?id=S1")
    assert res.status_code == 200
    assert b"Room for S1" in res.data
    assert b"A1" in res.data

    # Missing ID
    res_missing = client.get("/room")
    assert res_missing.status_code == 400

    # XSS attempt injection
    xss_payload = "<script>alert('xss')</script>"
    res_xss = client.get(f"/room?id={xss_payload}")
    assert res_xss.status_code == 200
    assert b"<script>" not in res_xss.data
    assert b"&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in res_xss.data


def test_legacy_camelcase_interface():
    """Test that legacy camelCase names work seamlessly."""
    assert callable(ha.loadConfig)
    assert callable(ha.allocateRoom)
    assert callable(ha.vacateRoom)
    assert callable(ha.monthlyFee)
    assert callable(ha.priorityOrder)
    assert callable(ha.roomLottery)
    assert callable(ha.vacantBeds)
    assert callable(ha.connectWardenDb)
    assert callable(ha.startRemoteLogConfig)
    assert callable(ha.roomLookup)
    assert callable(ha.runPortal)

    # Calling legacy name works
    room = ha.allocateRoom("S99", "Legacy", "M", 4)
    assert room == "A1"
    assert ha.vacantBeds() == 11
    assert ha.vacateRoom("S99") is True
