"""Table-driven checks for both versions. Run: python3 test_both.py"""

import world
from agent import run
from deterministic import register_claim
from pretend_model import pretend_model, stuck_model

DETERMINISTIC = [
    # policy, expected reply
    ("P-1001", "Your claim C-501 is registered."),
    ("P-2002", "This policy is not active, so I can't register a claim."),
    ("P-9999", "I can't find that policy number."),
]

AGENT = [
    # task, model, expected reply
    ("I had a car accident yesterday. My policy is P-1001. Please register my claim.", pretend_model, "Your claim C-501 is registered."),
    ("Please register my claim on P-2002.", pretend_model, "This policy is not active, so I can't register a claim."),
    ("What does my policy P-1001 cover?", pretend_model, "Your policy covers: accident, theft."),
    ("Please register my claim on P-1001.", stuck_model, "I couldn't finish this in time, so I am handing over to a person."),
]

for policy, expected in DETERMINISTIC:
    world.CLAIMS.clear()
    got = register_claim(policy, "2026-11-15", "car accident")
    assert got == expected, (policy, got)

for task, model, expected in AGENT:
    world.CLAIMS.clear()
    got = run(task, model, log=lambda line: None)
    assert got == expected, (task, got)

print(f"{len(DETERMINISTIC) + len(AGENT)} cases passed")
