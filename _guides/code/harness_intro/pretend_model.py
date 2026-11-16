"""A pretend model, so the example runs with no account and no cost.

It returns replies in the same shape a real model does: a list of content blocks and a stop_reason.
A real model reads the words and decides; this one follows three simple rules, which is enough to
show the loop. Replace it with a call to a real model and agent.py does not change.
"""

import json
import re


def _results(messages):
    """Every tool result the loop has shown the model so far."""
    out = []
    for m in messages:
        if m["role"] == "user" and isinstance(m["content"], list):
            out += [json.loads(b["content"]) for b in m["content"] if b["type"] == "tool_result"]
    return out


def _ask(n, name, args):
    return {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": f"call_{n}", "name": name, "input": args}]}


def _say(text):
    return {"stop_reason": "end_turn", "content": [{"type": "text", "text": text}]}


def pretend_model(system, tools, messages):
    task = messages[0]["content"]
    seen = _results(messages)
    policy_id = re.search(r"P-\d+", task).group()
    if not seen:  # nothing looked up yet: start with the policy
        return _ask(1, "get_policy", {"policy_id": policy_id})
    policy = seen[0]
    if "error" in policy:
        return _say("I can't find that policy number.")
    if "register" not in task:  # only a question: answer from the policy
        return _say(f"Your policy covers: {', '.join(policy['covers'])}.")
    if not policy["active"]:
        return _say("This policy is not active, so I can't register a claim.")
    if len(seen) == 1:  # policy is fine: now create the claim
        return _ask(2, "create_claim", {"policy_id": policy_id, "accident_date": "2026-11-15", "what_happened": "car accident"})
    return _say(f"Your claim {seen[1]['claim_id']} is registered.")


def stuck_model(system, tools, messages):
    """A model that never finishes: it asks for the same tool every time."""
    return _ask(len(messages), "get_policy", {"policy_id": "P-1001"})
