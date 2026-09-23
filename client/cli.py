import argparse
import json
import os
import sys
import uuid
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_SERVER_URL = "http://127.0.0.1:8000"
DEFAULT_TOKEN = os.getenv("CLIENT_TOKEN", "hr-demo-client-token-2026")
DEFAULT_EMPLOYEE_ID = os.getenv("CLIENT_EMPLOYEE_ID", "EMP001")


def print_banner():
    print("=" * 70)
    print("      HR HELPDESK ASSISTANT V1 — INTERACTIVE CLI CLIENT      ")
    print("=" * 70)
    print(f"Server URL   : {DEFAULT_SERVER_URL}")
    print(f"Employee ID  : {DEFAULT_EMPLOYEE_ID}")
    print(f"Token        : {DEFAULT_TOKEN[:8]}... (Bearer Auth)")
    print("-" * 70)
    print("Commands:")
    print("  /stream    Toggle streaming mode (SSE)")
    print("  /new       Start a new conversation session")
    print("  /wfh       Quick demo: Work-From-Home policy query")
    print("  /leave     Quick demo: Casual leave balance query")
    print("  /ticket    Quick demo: Payroll ticket classification")
    print("  /guard     Quick demo: Protected catastrophic action")
    print("  /exit      Exit the client")
    print("=" * 70)
    print()


def send_chat_request(
    server_url: str,
    token: str,
    conversation_id: str,
    user_id: str,
    message: str,
):
    """
    Send a non-streaming POST request to /chat.
    """
    url = f"{server_url}/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "message": message,
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            print("\n[ASSISTANT RESPONSE]")
            print("-" * 70)
            print(f"Answer       : {data.get('answer')}")
            print(f"Request Type : {data.get('request_type')}")
            print(f"Status       : {data.get('status')}")
            print(f"Category     : {data.get('category')}")
            print(f"Priority     : {data.get('priority')}")
            if data.get("requires_human_review") is not None:
                print(f"Human Review : {data.get('requires_human_review')}")
            print(f"Tool Used    : {data.get('tool_name') or 'None'}")
            print(f"Request ID   : {data.get('id')}")
            print("-" * 70)
        else:
            print(f"\n[HTTP ERROR {response.status_code}]")
            try:
                print(json.dumps(response.json(), indent=2))
            except Exception:
                print(response.text)
    except httpx.ConnectError:
        print(f"\n[ERROR] Could not connect to backend at {server_url}.")
        print("Please ensure the backend server is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as exc:
        print(f"\n[ERROR] Request failed: {exc}")


def send_stream_request(
    server_url: str,
    token: str,
    conversation_id: str,
    user_id: str,
    message: str,
):
    """
    Send a streaming POST request to /chat/stream using Server-Sent Events.
    """
    url = f"{server_url}/chat/stream"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "message": message,
    }

    try:
        print("\n[ASSISTANT STREAMING RESPONSE]")
        print("-" * 70)
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    print(f"[HTTP ERROR {response.status_code}] {response.text}")
                    return

                for line in response.iter_lines():
                    if not line:
                        continue
                    if line == "data: [DONE]":
                        break
                    if line.startswith("data: [ERROR]"):
                        print(f"\n{line}")
                        break
                    if line.startswith("data: "):
                        chunk = line[6:]
                        # Print raw chunk or token
                        sys.stdout.write(chunk)
                        sys.stdout.flush()

        print("\n" + "-" * 70)
    except httpx.ConnectError:
        print(f"\n[ERROR] Could not connect to backend at {server_url}.")
        print("Please ensure the backend server is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as exc:
        print(f"\n[ERROR] Streaming request failed: {exc}")


def main():
    parser = argparse.ArgumentParser(description="HR Helpdesk Assistant CLI")
    parser.add_argument("--url", default=DEFAULT_SERVER_URL, help="Backend URL")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Client Bearer token")
    parser.add_argument("--user-id", default=DEFAULT_EMPLOYEE_ID, help="Authenticated employee ID")
    parser.add_argument("--stream", action="store_true", help="Enable streaming mode by default")
    args = parser.parse_args()

    # Auto-resolve demo token for the requested employee if token was not explicitly overridden
    if args.token == DEFAULT_TOKEN and args.user_id.upper() != DEFAULT_EMPLOYEE_ID.upper():
        active_token = f"{DEFAULT_TOKEN}-{args.user_id.lower()}"
    else:
        active_token = args.token

    conversation_id = f"cli-session-{uuid.uuid4().hex[:8]}"
    streaming_mode = args.stream


    print_banner()


    while True:
        try:
            prompt_label = f"[{args.user_id}|{'STREAM' if streaming_mode else 'JSON'}] > "
            user_input = input(prompt_label).strip()

            if not user_input:
                continue

            if user_input.lower() in {"/exit", "/quit", "exit", "quit"}:
                print("\nGoodbye!")
                break

            if user_input.lower() == "/stream":
                streaming_mode = not streaming_mode
                print(f"[*] Streaming mode is now {'ENABLED' if streaming_mode else 'DISABLED'}.\n")
                continue

            if user_input.lower() == "/new":
                conversation_id = f"cli-session-{uuid.uuid4().hex[:8]}"
                print(f"[*] Started new conversation session: {conversation_id}\n")
                continue

            if user_input.lower() == "/wfh":
                user_input = "What is the work-from-home policy, and can I work remotely on Friday?"
                print(f"Query: {user_input}")

            elif user_input.lower() == "/leave":
                user_input = "How many casual leaves do I have left?"
                print(f"Query: {user_input}")

            elif user_input.lower() == "/ticket":
                user_input = "My salary has not been credited this month."
                print(f"Query: {user_input}")

            elif user_input.lower() == "/guard":
                user_input = "Please modify my salary to 50 LPA."
                print(f"Query: {user_input}")

            if streaming_mode:
                send_stream_request(
                    server_url=args.url,
                    token=active_token,
                    conversation_id=conversation_id,
                    user_id=args.user_id,
                    message=user_input,
                )
            else:
                send_chat_request(
                    server_url=args.url,
                    token=active_token,
                    conversation_id=conversation_id,
                    user_id=args.user_id,
                    message=user_input,
                )

            print()

        except KeyboardInterrupt:
            print("\nExiting CLI.")
            break


if __name__ == "__main__":
    main()
