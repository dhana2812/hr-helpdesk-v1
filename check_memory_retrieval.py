from app.memory.conversation import (
    filter_messages,
    load_recent_messages,
)

messages = load_recent_messages(
    conversation_id="memory-demo-001",
    user_id="EMP001",
    limit=10,
)

filtered = filter_messages(messages)

print("=" * 60)
print("LOADED MEMORY")
print("=" * 60)

for message in filtered:
    print(f"ROLE: {message['role']}")
    print(f"MESSAGE: {message['message']}")
    print("-" * 60)

print(f"Total loaded messages: {len(filtered)}")