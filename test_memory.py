from app.memory.conversation import (
    initialize_memory_database,
    load_recent_messages,
    save_message,
)


CONVERSATION_ID = "test-conversation-001"
USER_ID = "EMP001"


def test_memory_persistence():
    initialize_memory_database()

    save_message(
        conversation_id=CONVERSATION_ID,
        user_id=USER_ID,
        role="user",
        message="My name is Arun.",
    )

    save_message(
        conversation_id=CONVERSATION_ID,
        user_id=USER_ID,
        role="assistant",
        message="Hello Arun.",
    )

    messages = load_recent_messages(
        conversation_id=CONVERSATION_ID,
        user_id=USER_ID,
    )

    print("MEMORY PERSISTENCE TEST")
    print(messages)

    assert len(messages) >= 2
    assert messages[-2]["message"] == "My name is Arun."
    assert messages[-1]["message"] == "Hello Arun."

    print("MEMORY PERSISTENCE TEST: PASS")


def test_user_isolation():
    messages = load_recent_messages(
        conversation_id=CONVERSATION_ID,
        user_id="EMP002",
    )

    print("USER ISOLATION TEST")
    print(messages)

    assert len(messages) == 0

    print("USER ISOLATION TEST: PASS")


def test_empty_message_is_ignored():
    save_message(
        conversation_id=CONVERSATION_ID,
        user_id=USER_ID,
        role="user",
        message="   ",
    )

    messages = load_recent_messages(
        conversation_id=CONVERSATION_ID,
        user_id=USER_ID,
    )

    print("EMPTY MESSAGE TEST: PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("CONVERSATION MEMORY TESTS")
    print("=" * 60)

    test_memory_persistence()
    print()

    test_user_isolation()
    print()

    test_empty_message_is_ignored()

    print("=" * 60)
    print("ALL MEMORY TESTS PASSED")
    print("=" * 60)