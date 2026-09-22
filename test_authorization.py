from app.security.authorization import (
    AuthorizationError,
    authorize_employee_access,
)


def test_own_employee_access():
    authorize_employee_access("EMP001", "EMP001")

    print("OWN DATA TEST: PASS")


def test_another_employee_access():
    try:
        authorize_employee_access("EMP001", "EMP002")
        print("ANOTHER EMPLOYEE TEST: FAIL")

    except AuthorizationError as exc:
        print("ANOTHER EMPLOYEE TEST: PASS")
        print("Error:", exc)


def test_second_employee_own_access():
    authorize_employee_access("EMP002", "EMP002")

    print("SECOND EMPLOYEE OWN DATA TEST: PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("AUTHORIZATION TESTS")
    print("=" * 60)

    test_own_employee_access()
    print()

    test_another_employee_access()
    print()

    test_second_employee_own_access()

    print("=" * 60)
    print("AUTHORIZATION TESTS COMPLETE")
    print("=" * 60)