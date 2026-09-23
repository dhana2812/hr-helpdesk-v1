from typing import Any, Literal

from pydantic import BaseModel, Field


RequestType = Literal[
    "general_question",
    "policy_question",
    "employee_record_lookup",
    "ticket_classification",
    "out_of_scope",
]

ResponseStatus = Literal[
    "answered",
    "needs_tool",
    "declined",
    "needs_clarification",
]

Category = Literal[
    "leave",
    "payroll",
    "reimbursement",
    "benefits",
    "attendance",
    "work_from_home",
    "it_access",
    "general",
    "general_hr",
    "other",
]

Priority = Literal[
    "low",
    "medium",
    "high",
    "critical",
    "urgent",
]


class HRResponse(BaseModel):
    model_config = {"extra": "forbid"}
    id: str
    request_type: RequestType
    status: ResponseStatus
    answer: str

    requires_tool: bool = False
    tool_name: str | None = None
    tool_arguments: dict[str, Any] = Field(default_factory=dict)

    category: Category | None = None
    priority: Priority | None = None
    urgency: Priority | None = None
    summary: str | None = None
    requires_human_review: bool = False


class TicketClassification(BaseModel):
    category: Category
    urgency: Priority
    requires_human_review: bool
    summary: str

class ChatRequest(BaseModel):
    conversation_id: str = Field(
        min_length=1,
        max_length=100,
    )

    user_id: str = Field(
        min_length=1,
        max_length=50,
    )

    message: str = Field(
        min_length=1,
        max_length=4000,
    )