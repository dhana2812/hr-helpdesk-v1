from app.tools.ticket_tools import create_ticket


def test_create_ticket():
    result = create_ticket(
        authenticated_user_id="EMP001",
        category="it_access",
        priority="high",
        summary="Cracked laptop screen before urgent client demo",
        requires_human_review=True,
    )

    print("CREATE TICKET TEST")
    print("Result:", result)

    assert result["success"] is True
    assert result["category"] == "it_access"
    assert result["priority"] == "high"
    assert result["requires_human_review"] is True
    assert result["ticket_id"].startswith("TICK-")

    print("CREATE TICKET TEST: PASS")


if __name__ == "__main__":
    test_create_ticket()
