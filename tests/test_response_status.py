from app.llm.client import (
    LLMResponseStatusError,
    OpenRouterClient,
)


def test_success_response_status():
    response = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": "valid response",
                },
            }
        ]
    }

    assert OpenRouterClient.check_response_status(response) == "success"


def test_incomplete_response_status():
    response = {
        "choices": [
            {
                "finish_reason": "length",
                "message": {
                    "content": '{"id":"request-id"',
                },
            }
        ]
    }

    assert OpenRouterClient.check_response_status(response) == "incomplete"


def test_cancelled_response_status():
    response = {
        "choices": [
            {
                "finish_reason": "cancelled",
                "message": {
                    "content": "partial response",
                },
            }
        ]
    }

    assert OpenRouterClient.check_response_status(response) == "cancelled"


def test_missing_choices_is_error():
    response = {}

    assert OpenRouterClient.check_response_status(response) == "error"


def test_incomplete_response_is_rejected():
    response = {
        "choices": [
            {
                "finish_reason": "length",
                "message": {
                    "content": '{"id":"request-id"',
                },
            }
        ]
    }

    try:
        OpenRouterClient.require_successful_response(response)
    except LLMResponseStatusError as exc:
        assert "incomplete" in str(exc)
    else:
        raise AssertionError(
            "Incomplete response should not be accepted."
        )


def test_cancelled_response_is_rejected():
    response = {
        "choices": [
            {
                "finish_reason": "cancelled",
                "message": {
                    "content": "partial response",
                },
            }
        ]
    }

    try:
        OpenRouterClient.require_successful_response(response)
    except LLMResponseStatusError as exc:
        assert "cancelled" in str(exc)
    else:
        raise AssertionError(
            "Cancelled response should not be accepted."
        )


def test_error_response_is_rejected():
    response = {
        "choices": []
    }

    try:
        OpenRouterClient.require_successful_response(response)
    except LLMResponseStatusError as exc:
        assert "error" in str(exc)
    else:
        raise AssertionError(
            "Error response should not be accepted."
        )