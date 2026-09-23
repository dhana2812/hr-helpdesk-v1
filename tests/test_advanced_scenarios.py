import pytest
from app.policies.policy_loader import load_policy
from app.tools.employee_records import get_leave_balance
from app.llm.structured_output import parse_hr_response


# =====================================================================
# 1. Policy Grounding Tests (Exact Numbers, Preconditions, Prohibitions)
# =====================================================================

def test_pattern_a_exact_numbers():
    leave = load_policy("leave")
    assert "maximum of 8 unused casual leaves" in leave
    
    reimb = load_policy("reimbursement")
    assert "within 30 days of the expense date" in reimb


def test_pattern_b_preconditions():
    wfh = load_policy("work_from_home")
    assert "currently on probation are not eligible" in wfh
    assert "90-day (3 months) probation period" in wfh
    
    leave = load_policy("leave")
    assert "emergency sick leave for 1 or 2 days without a doctor's certificate" in leave


def test_pattern_c_explicit_prohibitions():
    reimb = load_policy("reimbursement")
    assert "Alcoholic beverages, personal entertainment items" in reimb
    assert "strictly non-reimbursable" in reimb


# =====================================================================
# 2. Complex Ticket Classification Edge Cases
# =====================================================================

def test_scenario_2_1_multi_category_blended():
    json_str = """
    {
      "id": "req-blend",
      "request_type": "ticket_classification",
      "status": "answered",
      "answer": "Blended hardware and leave issue logged.",
      "category": "it_access",
      "urgency": "high",
      "requires_human_review": true,
      "summary": "Hardware failure (laptop charger) and attendance/leave discrepancy."
    }
    """
    res = parse_hr_response(json_str)
    assert res.category == "it_access"
    assert res.urgency == "high"
    assert res.requires_human_review is True
    assert "Hardware failure" in res.summary


def test_scenario_2_2_sarcastic_tone_payroll():
    json_str = """
    {
      "id": "req-sarcastic",
      "request_type": "ticket_classification",
      "status": "answered",
      "answer": "Salary deduction inquiry logged.",
      "category": "payroll",
      "urgency": "high",
      "requires_human_review": true,
      "summary": "Employee reported incorrect salary deduction / duplicate tax deduction."
    }
    """
    res = parse_hr_response(json_str)
    assert res.category == "payroll"
    assert res.urgency == "high"
    assert res.requires_human_review is True


def test_scenario_2_3_dramatic_phrasing_low_urgency():
    json_str = """
    {
      "id": "req-dramatic",
      "request_type": "ticket_classification",
      "status": "answered",
      "answer": "Dress code inquiry answered.",
      "category": "general",
      "urgency": "low",
      "requires_human_review": false,
      "summary": "Inquiry regarding office dress code / lanyard guidelines."
    }
    """
    res = parse_hr_response(json_str)
    assert res.category == "general"
    assert res.urgency == "low"
    assert res.requires_human_review is False


# =====================================================================
# 3. Deterministic Tools & Zero Balance Handling
# =====================================================================

def test_scenario_3_1_zero_leave_balance():
    res = get_leave_balance(
        authenticated_user_id="EMP003",
        requested_employee_id="EMP003",
        leave_type="casual",
    )
    assert res["success"] is True
    assert res["balance"] == 0
    assert res["employee_name"] == "John Doe"
