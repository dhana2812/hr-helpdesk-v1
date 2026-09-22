import asyncio

from app.llm.client import llm_client


async def main():
    response = await llm_client.chat(
        "What is the difference between casual leave and sick leave?"
    )

    content = llm_client.extract_content(response)
    usage = llm_client.extract_usage(response)

    print("=" * 60)
    print("LLM CLIENT TEST")
    print("=" * 60)

    print("Model:", response.get("model"))

    print("\nCONTENT:")
    print(content)

    print("\nUSAGE:")
    print(usage)

    assert content
    assert isinstance(usage["input_tokens"], int)
    assert isinstance(usage["output_tokens"], int)

    print("\nLLM CLIENT TEST: PASS")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())