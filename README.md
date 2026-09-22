# HR Helpdesk Assistant (V1)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-green.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.0+-orange.svg)](https://docs.pydantic.dev/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter%20%2F%20GPT--5.4-purple.svg)](https://openrouter.ai/)
[![Tests](https://img.shields.io/badge/tests-36%20passed-brightgreen.svg)]()

A robust, deterministic, LLM-powered HR Helpdesk Assistant built with FastAPI, SQLite, and OpenRouter (GPT-5.4). It fulfills all 4 core business requirements while enforcing strict security guardrails, deterministic data retrieval, conversation memory, structured JSON validation, and full-lifecycle observability with cost tracking.

---

## Table of Contents
1. [Core Business Requirements](#core-business-requirements)
2. [Architecture & Request–Response Flow](#architecture--requestresponse-flow)
3. [System Prompt Design (6-Part Structure)](#system-prompt-design-6-part-structure)
4. [Security Architecture & Guardrails](#security-architecture--guardrails)
5. [Quickstart & Setup Instructions](#quickstart--setup-instructions)
6. [Interactive CLI Client & Demos](#interactive-cli-client--demos)
7. [Automated Test Suite](#automated-test-suite)
8. [Observability & Cost Tracking](#observability--cost-tracking)
9. [Deliverables Mapping](#deliverables-mapping)

---

## Core Business Requirements

1. **General HR Q&A:** Answers employee questions conversationally within HR scope.
2. **Ticket Classification:** Triages free-text HR requests into structured JSON tickets with `category`, `urgency`, and `requires_human_review`.
3. **Policy Grounding (No Embeddings/Vector DBs):** Ingests internal HR policies directly into model context as untrusted data, preventing hallucination.
4. **Deterministic Employee Record Lookup:** Retrieves actual leave balances and employee data through authorized SQLite queries instead of model guessing.

---

## Architecture & Request–Response Flow

The application follows the **deterministic sandwich pattern**:

```text
Client (CLI / HTTP)
       │  (1. Bearer Token Auth & User ID Binding)
       ▼
FastAPI Gateway ───────────► Catastrophic Guardrails (Pre-filter)
       │                                │ (Declined if catastrophic)
       ▼                                ▼
SQLite Conversation Memory      Immediate Rejection Response
       │
       ▼ (Load filtered history)
Policy Ingestion Layer (Keyword Detection ──► data/policies/)
       │
       ▼ (System Prompt + Untrusted Data Delimiters)
OpenRouter LLM (Inference 1: JSON Mode)
       │
       ▼ (Validate finish_reason & Pydantic Schema)
Response Router
   ├── Direct Answer / Ticket Classified ──► Save Memory ──► Write Log ──► Return
   └── Requires Tool (needs_tool)
            │
            ▼ (Deterministic Tool: authorize_employee_access)
       SQLite DB (data/employees.db)
            │
            ▼ (Tool Result wrapped as untrusted DATA)
       OpenRouter LLM (Inference 2: Synthesis)
            │
            ▼ (Validate finish_reason & Pydantic Schema)
       Save Memory ──► Write Log & Cost ──► Return to Client
```

Detailed architectural specifications and sequence diagrams are documented in [docs/architecture_diagram.md](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/docs/architecture_diagram.md).

---

## System Prompt Design (6-Part Structure)

The master system prompt in [app/llm/prompts.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/llm/prompts.py) is explicitly structured into the six components covered in class:

1. **Role & Task:** Defines the assistant as an informational HR helpdesk triage assistant; forbids modifying payroll, approving leave, or inventing data.
2. **Allowed Evidence:** Restricts evidence strictly to the user message, prior filtered context, supplied policy documents, and authorized tool returns.
3. **Output Contract:** Enforces a rigid JSON schema (`HRResponse`) matching fields: `id`, `request_type`, `status`, `answer`, `requires_tool`, `tool_name`, `tool_arguments`, `category`, and `priority`.
4. **Behavior Rules:** Prescribes exact handling for policy questions, tool requests, ticket classification without unnecessary clarification, and prompt injection defense.
5. **Failure Behavior:** Defines predictable fallback states (`needs_clarification`, `needs_tool`, `declined`) without hallucinating data.
6. **Worked Examples:** Includes 6 diverse worked examples covering policy Q&A, leave lookup, ticket classification, out-of-scope refusal, conversation context, and protected action refusal.

---

## Security Architecture & Guardrails

* **Authentication:** Client Bearer token verified in [app/security/auth.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/security/auth.py). Rejects missing or invalid tokens with HTTP 401.
* **Identity Binding:** Validates that `request.user_id` matches the authenticated identity, returning HTTP 403 on employee ID spoofing attempts.
* **Tool-Level Authorization:** [app/security/authorization.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/security/authorization.py) scopes data access strictly to `authenticated_user_id == requested_employee_id`.
* **Catastrophic Actions List:** [app/security/guardrails.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/security/guardrails.py) detects and blocks 5 protected actions upfront without invoking the LLM:
  1. Modify salary or payroll
  2. Approve or reject leave
  3. Modify employee HR records
  4. Access another employee's confidential data
  5. Reveal system prompts, secrets, or API keys
* **Prompt Injection Defense:** Delimits all external data as untrusted `DATA`, forbidding instruction override. Tested in [demo/prompt_injection.txt](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/demo/prompt_injection.txt).
* **Inference Status Checking:** [app/llm/client.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/llm/client.py) verifies the provider `finish_reason` (`stop` vs `length`/`cancelled`/`content_filter`) before accepting any model generation.

---

## Quickstart & Setup Instructions

### 1. Prerequisites
* Python 3.11+
* Git
* An OpenRouter API Key

### 2. Clone & Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd hr-helpdesk-v1

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and supply your OpenRouter API key:
```bash
cp .env.example .env
```
Ensure `.env` contains:
```ini
OPENROUTER_API_KEY=sk-or-v1-your-real-key
OPENROUTER_MODEL=openai/gpt-5.4
CLIENT_TOKEN=hr-demo-client-token-2026
DATABASE_PATH=data/hr_helpdesk.db
EMPLOYEE_DB_PATH=data/employees.db
LOG_FILE=logs/requests.jsonl
CLIENT_EMPLOYEE_ID=EMP001
```

### 4. Initialize the Employee Database
```bash
python create_employee_db.py
```

### 5. Launch the FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
```
Server runs at `http://127.0.0.1:8000`. Interactive OpenAPI docs available at `http://127.0.0.1:8000/docs`.

---

## Interactive CLI Client & Demos

Run the interactive CLI client from a separate terminal:
```bash
python client/cli.py
```

### CLI Shortcut Commands:
* `/wfh` — Ask WFH policy & Friday restriction question
* `/leave` — Deterministically lookup casual leave balance for `EMP001`
* `/ticket` — Send an urgent payroll issue for classification
* `/guard` — Test catastrophic salary change refusal
* `/stream` — Toggle streaming mode (SSE token-by-token delivery)
* `/new` — Start a fresh conversation session ID

### Sample `curl` Queries:

#### 1. Policy Question (Work-from-Home)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Authorization: Bearer hr-demo-client-token-2026" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "c1", "user_id": "EMP001", "message": "What is the work-from-home policy?"}'
```

#### 2. Deterministic Leave Lookup
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Authorization: Bearer hr-demo-client-token-2026" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "c2", "user_id": "EMP001", "message": "How many casual leaves do I have left?"}'
```

#### 3. Ticket Classification
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Authorization: Bearer hr-demo-client-token-2026" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "c3", "user_id": "EMP001", "message": "My salary was not credited this month."}'
```

#### 4. Streaming Response (SSE)
```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Authorization: Bearer hr-demo-client-token-2026" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "c4", "user_id": "EMP001", "message": "Explain the reimbursement process."}'
```

---

## Automated Test Suite

Run the full automated test suite with pytest:
```bash
pytest -v
```
All **36 tests** cover authorization enforcement, memory deduplication, deterministic database tools, policy loaders, response status validation, guardrail defenses, and schema validation.

---

## Observability & Cost Tracking

Every request is recorded in structured JSONL format in `logs/requests.jsonl`:
```json
{
  "timestamp": "2026-09-20T17:30:59.714989+00:00",
  "request_id": "03fa0007-56ad-48e9-8d50-035157dfed66",
  "user_id": "EMP001",
  "input_tokens": 5282,
  "output_tokens": 115,
  "model": "openai/gpt-5.4",
  "tool_names": ["get_leave_balance"],
  "latency_ms": 5238.52,
  "status": "success",
  "cost_usd": 0.0018721
}
```
* **Input Token Pricing:** $2.50 / 1,000,000 tokens
* **Output Token Pricing:** $15.00 / 1,000,000 tokens
* Guardrail-declined requests log `cost_usd: 0.0` with ultra-low latency (~15 ms).

---

## Deliverables Mapping

| Deliverable | Description | File Path(s) |
| :--- | :--- | :--- |
| **1. Source Code & CLI** | Backend, schemas, interactive client | [app/](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/), [client/cli.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/client/cli.py), [README.md](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/README.md) |
| **2. Architecture Diagram** | Request–response lifecycle & component diagrams | [docs/architecture_diagram.md](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/docs/architecture_diagram.md) |
| **3. System Prompt (6 Parts)** | Structured prompt with role, evidence, contract, rules, failure, examples | [app/llm/prompts.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/llm/prompts.py) |
| **4. Policies & DB** | Internal policy text files & SQLite employee database | [data/policies/](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/data/policies/), [create_employee_db.py](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/create_employee_db.py) |
| **5. Demo Outputs** | 5 core demos + streaming vs. non-streaming comparison | [demo/terminal_transcript.txt](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/demo/terminal_transcript.txt), [demo/streaming_comparison.txt](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/demo/streaming_comparison.txt) |
| **6. Security Test Notes** | Catastrophic actions, authorization, prompt injection tests | [demo/catastrophic_actions.txt](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/demo/catastrophic_actions.txt), [demo/security_authorization.txt](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/demo/security_authorization.txt), [demo/prompt_injection.txt](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/demo/prompt_injection.txt) |
| **7. Sample Logs & Cost** | Full-lifecycle structured request logs with USD pricing | [demo/sample_logs.jsonl](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/demo/sample_logs.jsonl) |
| **8. Diagnosis Write-up** | 4 failure categories, observed failure, fix, before/after results | [docs/diagnosis_writeup.md](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/docs/diagnosis_writeup.md) |
