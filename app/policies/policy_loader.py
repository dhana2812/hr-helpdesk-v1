from pathlib import Path


POLICY_DIRECTORY = Path("data/policies")


POLICY_FILES = {
    "leave": "leave_policy.txt",
    "work_from_home": "wfh_policy.txt",
    "reimbursement": "reimbursement_policy.txt",
    "office_hours": "office_hours_policy.txt",
    "joining": "joining_policy.txt",
    "separation": "separation_policy.txt",
}


def load_policy(policy_name: str) -> str:
    """
    Load the requested HR policy document directly from disk.

    No embeddings or vector database are used in V1.
    """

    if policy_name not in POLICY_FILES:
        raise ValueError(
            f"Unsupported policy: {policy_name}"
        )

    policy_path = POLICY_DIRECTORY / POLICY_FILES[policy_name]

    if not policy_path.exists():
        raise FileNotFoundError(
            f"Policy file not found: {policy_path}"
        )

    return policy_path.read_text(
        encoding="utf-8"
    )