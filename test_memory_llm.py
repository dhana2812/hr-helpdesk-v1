import asyncio

from app.llm.client import llm_client


async def main():
    messages = [
        {
            "role": "user",
            "content": "My name is Arun.",
        },
        {
            "role": "assistant",
            "content": "Hello Arun! How can I help you today?",
        },
        {
            "role": "user",
            "content": "What is my name?",
        },
    ]

    response = await llm_client.chat(
        messages=messages
    )

    content = llm_client.extract_content(response)

    print("=" * 60)
    print("RAW LLM CONTENT")
    print("=" * 60)
    print(repr(content))
    print("=" * 60)
    print(content)
    print("=" * 60)

    print("MODEL:", response.get("model"))
    print("USAGE:", llm_client.extract_usage(response))


if __name__ == "__main__":
    asyncio.run(main())