from app.policies.policy_loader import load_policy


def test_wfh_policy():
    policy = load_policy("work_from_home")

    print("WFH POLICY TEST")
    print("Policy loaded:", len(policy), "characters")

    assert "two days per week" in policy
    assert "Friday is not eligible" in policy

    print("WFH POLICY TEST: PASS")


def test_leave_policy():
    policy = load_policy("leave")

    print("LEAVE POLICY TEST")
    print("Policy loaded:", len(policy), "characters")

    assert "Casual Leave" in policy
    assert "Sick Leave" in policy
    assert "must never automatically approve or reject" in policy

    print("LEAVE POLICY TEST: PASS")


def test_reimbursement_policy():
    policy = load_policy("reimbursement")

    print("REIMBURSEMENT POLICY TEST")
    print("Policy loaded:", len(policy), "characters")

    assert "Pending Claims" in policy
    assert "must not modify reimbursement records" in policy

    print("REIMBURSEMENT POLICY TEST: PASS")


def test_invalid_policy():
    try:
        load_policy("payroll")
        print("INVALID POLICY TEST: FAIL")

    except ValueError as exc:
        print("INVALID POLICY TEST: PASS")
        print("Error:", exc)


if __name__ == "__main__":
    print("=" * 60)
    print("POLICY LOADER TESTS")
    print("=" * 60)

    test_wfh_policy()
    print()

    test_leave_policy()
    print()

    test_reimbursement_policy()
    print()

    test_invalid_policy()

    print("=" * 60)
    print("ALL POLICY LOADER TESTS PASSED")
    print("=" * 60)