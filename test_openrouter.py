import asyncio

from app.llm.client import llm_client


async def main():
    response = await llm_client.chat(
        "Hello. Reply with exactly one short sentence confirming that the HR Helpdesk Assistant is connected."
    )

    print("Request successful.")
    print("Model:", response.get("model"))
    print("Response:")
    print(response["choices"][0]["message"]["content"])


if __name__ == "__main__":
    asyncio.run(main())