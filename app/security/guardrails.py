from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str


CATASTROPHIC_ACTIONS = (
    "modify_salary_or_payroll",
    "approve_or_reject_leave",
    "modify_employee_hr_records",
    "access_another_employee_data",
    "reveal_secrets_or_system_instructions",
)


def check_catastrophic_action(message: str) -> GuardrailResult:
    """
    Detect requests for actions that the HR assistant must never perform.

    The assistant is informational only. It must not execute or facilitate
    high-impact HR changes or reveal confidential system information.
    """

    normalized_message = " ".join(message.lower().split())

    # 1. Salary / payroll modification
    salary_action_words = (
        "change",
        "modify",
        "increase",
        "decrease",
        "update",
        "set",
        "adjust",
    )

    salary_target_words = (
        "salary",
        "pay",
        "payroll",
        "compensation",
    )

    if (
        any(word in normalized_message for word in salary_action_words)
        and any(word in normalized_message for word in salary_target_words)
    ):
        return GuardrailResult(
            allowed=False,
            reason=(
                "The assistant cannot modify salary, payroll, pay, "
                "or compensation records."
            ),
        )

    # 2. Leave approval / rejection
    leave_action_words = (
        "approve",
        "reject",
        "deny",
        "accept",
    )

    leave_target_words = (
        "leave",
        "vacation",
        "time off",
    )

    if (
        any(word in normalized_message for word in leave_action_words)
        and any(word in normalized_message for word in leave_target_words)
    ):
        return GuardrailResult(
            allowed=False,
            reason=(
                "The assistant can explain leave policy and balances, "
                "but it cannot approve or reject leave."
            ),
        )

    # 3. Employee HR record modification
    record_action_words = (
        "modify",
        "change",
        "update",
        "delete",
        "remove",
        "edit",
    )

    record_target_words = (
        "employee record",
        "employee hr record",
        "hr record",
        "personnel record",
        "employee profile",
        "hr profile",
    )

    if (
        any(word in normalized_message for word in record_action_words)
        and any(
            phrase in normalized_message
            for phrase in record_target_words
        )
    ):
        return GuardrailResult(
            allowed=False,
            reason=(
                "The assistant cannot modify, delete, or update "
                "employee HR records."
            ),
        )

    # 4. Access to another employee's confidential information
    #
    # This guardrail covers both explicit relationship phrases and
    # requests naming a specific employee. Authorization remains the
    # authoritative security boundary for actual data access.
    other_employee_indicators = (
        "another employee",
        "another employees",
        "other employee",
        "other employees",
        "someone else's",
        "someone elses",
        "another person's",
        "another persons",
        "other person's",
        "other persons",
    )

    named_employee_indicators = (
        "employee records",
        "employee record",
        "hr records",
        "hr record",
        "employee data",
        "hr data",
        "personal information",
        "personal data",
        "confidential information",
        "leave balance",
        "leave balances",
        "salary",
        "payroll",
        "compensation",
    )

    access_request_words = (
        "show",
        "give",
        "provide",
        "display",
        "tell me",
        "get",
        "access",
        "view",
        "see",
        "retrieve",
        "find",
        "share",
    )

    if (
        any(phrase in normalized_message for phrase in other_employee_indicators)
        and any(
            phrase in normalized_message
            for phrase in named_employee_indicators
        )
        and any(
            phrase in normalized_message
            for phrase in access_request_words
        )
    ):
        return GuardrailResult(
            allowed=False,
            reason=(
                "The assistant cannot access or reveal another "
                "employee's confidential information."
            ),
        )

    # 4b. Specific-name pattern for requests such as:
    # "Show me Priya Sharma employee records."
    #
    # We intentionally look for an access verb + a record/data target
    # rather than attempting to identify arbitrary names. The actual
    # employee identity check is still enforced by authorization.py.
    if (
        any(
            phrase in normalized_message
            for phrase in access_request_words
        )
        and any(
            phrase in normalized_message
            for phrase in named_employee_indicators
        )
        and (
            " employee " in f" {normalized_message} "
            or " hr " in f" {normalized_message} "
            or "records" in normalized_message
            or "data" in normalized_message
        )
    ):
        return GuardrailResult(
            allowed=False,
            reason=(
                "The assistant cannot access or reveal another "
                "employee's confidential information."
            ),
        )

    # 5. System prompt / API key / secrets / credentials
    secret_indicators = (
        "system prompt",
        "api key",
        "secret",
        "secrets",
        "credential",
        "credentials",
        "access token",
        "client token",
        "authentication token",
        "password",
    )

    secret_request_words = (
        "reveal",
        "show",
        "give",
        "provide",
        "display",
        "tell me",
        "print",
        "expose",
        "share",
    )

    if (
        any(
            phrase in normalized_message
            for phrase in secret_indicators
        )
        and any(
            phrase in normalized_message
            for phrase in secret_request_words
        )
    ):
        return GuardrailResult(
            allowed=False,
            reason=(
                "The assistant cannot reveal system prompts, API keys, "
                "credentials, secrets, tokens, passwords, or internal "
                "security information."
            ),
        )

    return GuardrailResult(
        allowed=True,
        reason="Request does not match a protected catastrophic action.",
    )
