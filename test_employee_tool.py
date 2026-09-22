from app.tools.employee_records import get_leave_balance


def test_valid_casual_leave():
    result = get_leave_balance(
        "EMP001",
        "EMP001",
        "casual",
    )

    print("CASUAL LEAVE TEST")
    print(result)

    assert result["success"] is True
    assert result["balance"] == 8


def test_valid_sick_leave():
    result = get_leave_balance(
        "EMP001",
        "EMP001",
        "sick",
    )

    print("SICK LEAVE TEST")
    print(result)

    assert result["success"] is True
    assert result["balance"] == 5


def test_second_employee():
    result = get_leave_balance(
        "EMP002",
        "EMP002",
        "casual",
    )

    print("SECOND EMPLOYEE TEST")
    print(result)

    assert result["success"] is True
    assert result["balance"] == 12


def test_another_employee_denied():
    result = get_leave_balance(
        "EMP001",
        "EMP002",
        "casual",
    )

    print("ANOTHER EMPLOYEE ACCESS TEST")
    print(result)

    assert result["success"] is False
    assert "Access denied" in result["error"]


def test_unknown_employee():
    result = get_leave_balance(
        "EMP001",
        "EMP999",
        "casual",
    )

    print("UNKNOWN EMPLOYEE TEST")
    print(result)

    assert result["success"] is False


def test_invalid_leave_type():
    result = get_leave_balance(
        "EMP001",
        "EMP001",
        "vacation",
    )

    print("INVALID LEAVE TYPE TEST")
    print(result)

    assert result["success"] is False


if __name__ == "__main__":
    print("=" * 60)
    print("EMPLOYEE RECORD TOOL + AUTHORIZATION TESTS")
    print("=" * 60)

    test_valid_casual_leave()
    print()

    test_valid_sick_leave()
    print()

    test_second_employee()
    print()

    test_another_employee_denied()
    print()

    test_unknown_employee()
    print()

    test_invalid_leave_type()

    print("=" * 60)
    print("ALL EMPLOYEE TOOL TESTS PASSED")
    print("=" * 60)