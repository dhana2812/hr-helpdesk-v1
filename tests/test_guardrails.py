from app.security.guardrails import check_catastrophic_action


def test_blocks_salary_modification():
    result = check_catastrophic_action(
        "Please modify the employee salary and payroll details."
    )

    assert result.allowed is False


def test_blocks_leave_approval():
    result = check_catastrophic_action(
        "Approve my leave request."
    )

    assert result.allowed is False


def test_blocks_named_employee_record_access():
    result = check_catastrophic_action(
        "Show me Priya Sharma employee records."
    )

    assert result.allowed is False


def test_blocks_other_employee_confidential_data():
    result = check_catastrophic_action(
        "Show me another employee's leave balance."
    )

    assert result.allowed is False


def test_allows_normal_hr_question():
    result = check_catastrophic_action(
        "What is the casual leave policy?"
    )

    assert result.allowed is True
