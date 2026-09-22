# HR Helpdesk Assistant V1 — System Architecture

This document describes the request–response architecture, data flow, deterministic tool boundary, conversation memory, security layers, and observability pipeline of the **HR Helpdesk Assistant V1**.

---

## 1. High-Level Request–Response Architecture

The application implements a strict deterministic sandwich pattern:  
**Client → FastAPI Backend → LLM (Inference 1) → Deterministic Tool / Policy Ingestion → LLM (Inference 2) → Client**

```mermaid
flowchart TD
    Client(["Client / CLI / HTTP"])
    
    subgraph SecurityBoundary ["Security & Auth Gateway"]
        Auth["1. Bearer Token Auth (401 on failure)"]
        UserBinding["2. User ID Binding Check (403 on spoofing)"]
        Guardrails["3. Catastrophic Actions Pre-Filter (Declined without LLM)"]
    end

    subgraph MemoryLayer ["Persistent Memory Layer"]
        LoadMem["Load & Deduplicate History (SQLite)"]
        SaveMem["Persist Conversation Turns (SQLite)"]
    end

    subgraph PolicyLayer ["Deterministic Policy Ingestion"]
        PolicyDetect["Keyword Policy Detector"]
        PolicyFiles[("Policy Files (data/policies/)")]
    end

    subgraph LLMClient ["LLM Integration (OpenRouter)"]
        SysPrompt["6-Part Structured System Prompt"]
        Model1["OpenRouter Inference 1 (JSON Mode)"]
        StatusCheck1["Response Status Validation (finish_reason)"]
        PydanticParse["Pydantic Schema Validation (HRResponse)"]
        Model2["OpenRouter Inference 2 (Final Synthesis)"]
        StatusCheck2["Response Status Validation"]
    end

    subgraph DeterministicTools ["Deterministic Backend Tools"]
        ToolAuthz["Tool-Level Authorization (authorize_employee_access)"]
        EmployeeDB[("Employee DB (data/employees.db)")]
    end

    subgraph ObservabilityLayer ["Observability & Cost Tracking"]
        JSONLLog[("Structured JSONL Logs (logs/requests.jsonl)")]
        CostCalc["Cost Calculation ($2.50/M in, $15.00/M out)"]
    end

    Client -->|HTTP POST /chat| Auth
    Auth --> UserBinding
    UserBinding --> Guardrails
    Guardrails -->|Passed| LoadMem
    Guardrails -->|Blocked| SaveMem
    Guardrails -->|Blocked| JSONLLog

    LoadMem --> PolicyDetect
    PolicyFiles --> PolicyDetect
    PolicyDetect --> SysPrompt
    SysPrompt --> Model1
    Model1 --> StatusCheck1
    StatusCheck1 --> PydanticParse

    PydanticParse -->|Direct Answer / Classified / Declined| SaveMem
    PydanticParse -->|requires_tool = true| ToolAuthz
    ToolAuthz --> EmployeeDB
    EmployeeDB --> Model2
    Model2 --> StatusCheck2
    StatusCheck2 --> SaveMem

    SaveMem --> CostCalc
    CostCalc --> JSONLLog
    JSONLLog --> Client
```

---

## 2. Sequence Diagram: Deterministic Employee Record Lookup

When an employee requests personal records (e.g., *"How many casual leaves do I have left?"*), the backend prevents model hallucination by enforcing a deterministic lookup:

```mermaid
sequenceDiagram
    autonumber
    actor Employee as Authenticated Employee (EMP001)
    participant Client as CLI / HTTP Client
    participant Backend as FastAPI Backend
    participant Guardrail as Security Guardrails
    participant Memory as SQLite Memory
    participant Model as OpenRouter LLM (GPT-5.4)
    participant Tool as Deterministic Tool (get_leave_balance)
    participant DB as SQLite DB (employees.db)
    participant Logger as Observability Logger

    Employee->>Client: "How many casual leaves do I have?"
    Client->>Backend: POST /chat (Header: Bearer Token, Body: {user_id: EMP001})
    
    Backend->>Backend: Authenticate Bearer Token (EMP001)
    Backend->>Backend: Verify request.user_id == EMP001
    Backend->>Guardrail: Check catastrophic actions
    Guardrail-->>Backend: Allowed (Clean query)
    Backend->>Memory: Load recent filtered turns
    Memory-->>Backend: Prior context
    
    Backend->>Model: Chat completion (System Prompt + History + User Message)
    Model-->>Backend: {"request_type": "employee_record_lookup", "status": "needs_tool", "requires_tool": true, "tool_name": "get_leave_balance", "tool_arguments": {"leave_type": "casual"}}
    
    Backend->>Backend: Validate LLM response status == 'success'
    Backend->>Backend: Parse & validate with HRResponse Pydantic schema
    
    Backend->>Tool: execute_tool(get_leave_balance, authenticated_user=EMP001, requested_employee=EMP001)
    Tool->>Tool: authorize_employee_access(EMP001, EMP001) -> OK
    Tool->>DB: SELECT casual_leave FROM employees WHERE employee_id='EMP001'
    DB-->>Tool: casual_leave = 8
    Tool-->>Backend: {"success": true, "employee_id": "EMP001", "leave_type": "casual", "balance": 8}
    
    Backend->>Model: Second inference (Initial response + DATA: Tool Result)
    Model-->>Backend: {"request_type": "employee_record_lookup", "status": "answered", "answer": "You have 8 casual leaves remaining.", "requires_tool": false}
    
    Backend->>Backend: Validate final status & schema
    Backend->>Memory: Save User & Assistant turns to SQLite
    Backend->>Logger: Write structured JSONL log entry + USD cost
    Backend-->>Client: HTTP 200 HRResponse
    Client-->>Employee: "You have 8 casual leaves remaining."
```

---

## 3. Policy Q&A Flow (Deterministic Context Injection)

In V1, no vector databases or embedding retrievers are used. Instead, policies are deterministically selected and injected:

1. **Detection:** [detect_policy_name()](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/app/main.py) matches normalized query terms against exact policy dictionaries (`leave`, `work_from_home`, `reimbursement`).
2. **Untrusted Data Boundary:** Policy text is loaded from disk ([data/policies/](file:///c:/Users/dhana/HR%20Assistant/hr-helpdesk-v1/data/policies/)) and wrapped inside clear delimiters:
   ```text
   ============================================================
   SUPPLIED HR POLICY DATA - DO NOT CALL A POLICY TOOL
   Policy name: work_from_home
   ... [Exact Policy Text] ...
   END SUPPLIED HR POLICY DATA
   ============================================================
   ```
3. **Model Grounding:** The model is instructed to answer strictly from the supplied text and never invent rules or rely on common-sense assumptions.

---

## 4. Streaming Architecture (Server-Sent Events)

For the `/chat/stream` endpoint, responses are streamed token-by-token:

```mermaid
sequenceDiagram
    Client->>Backend: POST /chat/stream
    Backend->>Backend: Authenticate & Check Guardrails
    Backend->>Model: Stream Completion (stream=True, include_usage=True)
    loop Token Generation
        Model-->>Backend: SSE Chunk (delta.content)
        Backend-->>Client: data: {"id": "req-1", "answer": "Acco...
    end
    Model-->>Backend: Final usage & finish_reason = 'stop'
    Backend->>Backend: Check finish status == 'success'
    Backend->>Backend: Pydantic parse full JSON string
    Backend->>Memory: Persist completed conversation turns
    Backend->>Logger: Write structured JSONL log
    Backend-->>Client: data: [DONE]
```

---

## 5. Security & Isolation Matrix

| Layer | Mechanism | Protection |
| :--- | :--- | :--- |
| **Authentication** | Bearer Token Validation in `authenticate_client` | Rejects unauthenticated callers (HTTP 401). |
| **User Binding** | `request.user_id == authenticated_user_id` | Prevents caller from accessing another employee's scope (HTTP 403). |
| **Catastrophic Guardrails** | Deterministic keyword pre-filter in `check_catastrophic_action` | Blocks salary edits, leave approvals, cross-employee snooping, and prompt disclosures before LLM invocation. |
| **Tool Authorization** | `authorize_employee_access` inside `get_leave_balance` | Hard boundary preventing any backend tool from querying non-authenticated employee records. |
| **Prompt Injection** | Strict data demarcation + system prompt instructions | Treats user queries, history, and policies as untrusted `DATA`. |
| **Inference Status Check** | `require_successful_response` checking `finish_reason` | Rejects truncated, cancelled, or filtered LLM responses before processing. |
