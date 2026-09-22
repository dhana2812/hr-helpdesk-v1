from pathlib import Path
import json
import sys

from dotenv import load_dotenv
import os
import httpx


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.llm.prompts import SYSTEM_PROMPT


load_dotenv(PROJECT_ROOT / ".env")

api_key = os.environ["OPENROUTER_API_KEY"]
model = "openai/gpt-5.4"

test_file = PROJECT_ROOT / "tests" / "phase8_regression_cases.json"

with test_file.open("r", encoding="utf-8-sig") as file:
    test_cases = json.load(file)


print("=" * 80)
print("PHASE 8 — GPT-5.4 FROZEN REGRESSION")
print("=" * 80)
print(f"Model: {model}")
print(f"Test cases: {len(test_cases)}")
print("=" * 80)


results = []


for test_case in test_cases:
    test_id = test_case["id"]
    message = test_case["message"]

    print()
    print("-" * 80)
    print(f"{test_id}: {message}")
    print("-" * 80)

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        content = data["choices"][0]["message"]["content"]
        finish_reason = data["choices"][0].get("finish_reason")

        print("Finish reason:", finish_reason)
        print("Response:")
        print(content)

        results.append(
            {
                "id": test_id,
                "message": message,
                "finish_reason": finish_reason,
                "response": content,
                "error": None,
            }
        )

    except Exception as exc:
        print("ERROR:", exc)

        results.append(
            {
                "id": test_id,
                "message": message,
                "finish_reason": None,
                "response": None,
                "error": str(exc),
            }
        )


output_file = PROJECT_ROOT / "demo" / "phase8_gpt54_regression_results.json"

with output_file.open("w", encoding="utf-8") as file:
    json.dump(
        results,
        file,
        indent=2,
        ensure_ascii=False,
    )


print()
print("=" * 80)
print("REGRESSION COMPLETE")
print("=" * 80)
print(f"Results saved to: {output_file}")
print("=" * 80)