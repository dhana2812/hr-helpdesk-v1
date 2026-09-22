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

    test_invalid_json()
    print()

    test_missing_field()
    print()

    test_invented_category()

    print("=" * 60)