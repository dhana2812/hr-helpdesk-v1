from app.memory.conversation import filter_messages


def test_empty_messages_removed():
    messages = [
        {
            "role": "user",
            "message": "Hello",
        },
        {
            "role": "user",
            "message": "   ",
        },
        {
            "role": "assistant",
            "message": "Hi there",
        },
    ]

    result = filter_messages(messages)

    print("EMPTY MESSAGE FILTER TEST")
    print(result)

    assert len(result) == 2
    assert all(item["message"].strip() for item in result)

    print("EMPTY MESSAGE FILTER TEST: PASS")


def test_duplicates_removed():
    messages = [
        {
            "role": "user",
            "message": "What is my leave balance?",
        },
        {
            "role": "user",
            "message": "What is my leave balance?",
        },
        {
            "role": "assistant",
            "message": "I can check that.",
        },
        {
            "role": "assistant",
            "message": "I can check that.",
        },
    ]

    result = filter_messages(messages)

    print("DUPLICATE FILTER TEST")
    print(result)

    assert len(result) == 2

    print("DUPLICATE FILTER TEST: PASS")


def test_order_preserved():
    messages = [
        {
            "role": "user",
            "message": "First message",
        },
        {
            "role": "assistant",
            "message": "Second message",
        },
        {
            "role": "user",
            "message": "Third message",
        },
    ]

    result = filter_messages(messages)

    print("ORDER PRESERVATION TEST")
    print(result)

    assert result[0]["message"] == "First message"
    assert result[1]["message"] == "Second message"
    assert result[2]["message"] == "Third message"

    print("ORDER PRESERVATION TEST: PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("MEMORY FILTER TESTS")
    print("=" * 60)

    test_empty_messages_removed()
    print()

    test_duplicates_removed()
    print()

    test_order_preserved()

    print("=" * 60)
    print("ALL MEMORY FILTER TESTS PASSED")
    print("=" * 60)