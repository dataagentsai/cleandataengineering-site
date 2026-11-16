"""A tiny pretend insurance company: two policies and a list of claims."""

POLICIES = {
    "P-1001": {"holder": "Rohan", "active": True, "covers": ["accident", "theft"]},
    "P-2002": {"holder": "Meera", "active": False, "covers": ["accident"]},
}
CLAIMS = {}


def get_policy(policy_id):
    return POLICIES.get(policy_id) or {"error": f"No policy called {policy_id}"}


def create_claim(policy_id, accident_date, what_happened):
    claim_id = f"C-{501 + len(CLAIMS)}"
    CLAIMS[claim_id] = {"policy_id": policy_id, "accident_date": accident_date, "what_happened": what_happened}
    return {"claim_id": claim_id, "status": "registered"}
