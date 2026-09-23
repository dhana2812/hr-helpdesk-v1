from app.llm.structured_output import parse_hr_response, StructuredOutputError


def test_valid():
    content = """
    {
        "id": "test-001",
        "request_type": "general_question",
        "status": "answered",
        "answer": "Test response",
        "requires_tool": false,
        "tool_name": null,
        "tool_arguments": {},
        "category": "general_hr",
        "priority": "low"
    }
    """

    result = parse_hr_response(content)

    print("VALID TEST: PASS")
    print("Request type:", result.request_type)


def test_scenario_1_1_ambiguous_portal_error():
    content = """
    {
        "id": "test-s1-1",
        "request_type": "ticket_classification",
        "status": "answered",
        "answer": "Portal access error logged.",
        "category": "it_access",
        "urgency": "medium",
        "requires_human_review": true,
        "summary": "Employee experiencing unclear portal access error 403."
    }
    """
    result = parse_hr_response(content)
    assert result.category == "it_access"
    assert result.urgency == "medium"
    assert result.priority == "medium"
    assert result.requires_human_review is True
    assert result.summary == "Employee experiencing unclear portal access error 403."
    print("SCENARIO 1.1 TEST: PASS")


def test_scenario_1_2_intranet_calendar_low_urgency():
    content = """
    {
        "id": "test-s1-2",
        "request_type": "ticket_classification",
        "status": "answered",
        "answer": "Holiday calendar inquiry.",
        "category": "general",
        "urgency": "low",
        "requires_human_review": false,
        "summary": "Employee requesting location of intranet holiday calendar."
    }
    """
    result = parse_hr_response(content)
    assert result.category == "general"
    assert result.urgency == "low"
    assert result.requires_human_review is False
    print("SCENARIO 1.2 TEST: PASS")


def test_scenario_1_3_critical_payroll_failure():
    content = """
    {
        "id": "test-s1-3",
        "request_type": "ticket_classification",
        "status": "answered",
        "answer": "Regional payroll failure reported.",
        "category": "payroll",
        "urgency": "critical",
        "requires_human_review": true,
        "summary": "Regional direct deposit payroll failure affecting multiple employees."
    }
    """
    result = parse_hr_response(content)
    assert result.category == "payroll"
    assert result.urgency == "critical"
    assert result.priority == "critical"
    assert result.requires_human_review is True
    print("SCENARIO 1.3 TEST: PASS")


def test_invalid_json():
    try:
        parse_hr_response("This is not JSON")
        print("INVALID JSON TEST: FAIL")
    except StructuredOutputError as exc:
        print("INVALID JSON TEST: PASS")
        print("Error:", exc)


def test_missing_field():
    content = """
    {
        "id": "test-002",
        "request_type": "general_question",
        "status": "answered",
        "requires_tool": false,
        "tool_name": null,
        "tool_arguments": {},
        "category": "general_hr",
        "priority": "low"
    }
    """

    try:
        parse_hr_response(content)
        print("MISSING FIELD TEST: FAIL")
    except StructuredOutputError as exc:
        print("MISSING FIELD TEST: PASS")
        print("Error:", exc)


def test_invented_category():
    content = """
    {
        "id": "test-003",
        "request_type": "general_question",
        "status": "answered",
        "answer": "Test response",
        "requires_tool": false,
        "tool_name": null,
        "tool_arguments": {},
        "category": "made_up_category",
        "priority": "low"
    }
    """

    try:
        parse_hr_response(content)
        print("INVENTED CATEGORY TEST: FAIL")
    except StructuredOutputError as exc:
        print("INVENTED CATEGORY TEST: PASS")
        print("Error:", exc)


if __name__ == "__main__":
    print("=" * 60)
    print("STRUCTURED OUTPUT TESTS")
    print("=" * 60)

    test_valid()
    print()

    test_scenario_1_1_ambiguous_portal_error()
    print()

    test_scenario_1_2_intranet_calendar_low_urgency()
    print()

    test_scenario_1_3_critical_payroll_failure()
    print()

    test_invalid_json()
    print()

    test_missing_field()
    print()

    test_invented_category()

    print("=" * 60)
    print("ALL STRUCTURED OUTPUT TESTS PASSED")
    print("=" * 60)