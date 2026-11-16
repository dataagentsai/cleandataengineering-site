"""Register a claim with ordinary code. Our code decides every step, in the same order, every time."""

from world import create_claim, get_policy


def register_claim(policy_id, accident_date, what_happened):
    policy = get_policy(policy_id)  # step 1: always look up the policy
    if "error" in policy:
        return "I can't find that policy number."
    if not policy["active"]:  # step 2: always check that it is active
        return "This policy is not active, so I can't register a claim."
    if "accident" not in policy["covers"]:  # step 3: always check the cover
        return "This policy does not cover accidents."
    claim = create_claim(policy_id, accident_date, what_happened)  # step 4: always create the claim
    return f"Your claim {claim['claim_id']} is registered."


if __name__ == "__main__":
    print(register_claim("P-1001", "2026-11-15", "Hit from behind at a signal"))
