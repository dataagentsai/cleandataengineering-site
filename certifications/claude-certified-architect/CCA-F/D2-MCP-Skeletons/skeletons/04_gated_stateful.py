"""
Skeleton 04 · Gated / stateful server — the prerequisite pattern.

PATTERN           A side-effecting tool refuses to run until a prerequisite tool
                  has been called in this session. The classic pairing is
                  get_customer → process_refund.
WHAT IT EXPOSES   You cannot enforce ordering with prose. Writing "always call
                  get_customer first" in a description is a *request*; the model
                  complies most of the time, which is the worst possible rate for
                  something that moves money. The server is the only place the
                  ordering can actually be enforced.
                  It also exposes where session state lives: the MCP server
                  process, not the model's context.
EXAM SHAPE        "How do you ensure the agent verifies identity before refunding?"
                  → gate it server-side; the description is documentation, not
                  a control.

Run:  python 04_gated_stateful.py
"""

from fastmcp import FastMCP

mcp = FastMCP("gated-refunds")

_CUSTOMERS = {
    "ana@example.com": {"name": "Ana", "tier": "gold", "orders": ["A-1001"]},
}

# Session state, held by the SERVER. In a stdio server one process serves one
# client, so a module-level dict is a legitimate session store. Over HTTP with
# many concurrent clients it is a bug — key it by session there.
_verified: set[str] = set()


@mcp.tool
def get_customer(email: str) -> dict:
    """Look up a customer and verify their identity.

    Must be called before process_refund for the same customer — the refund tool
    is gated on it and will refuse otherwise.
    """
    customer = _CUSTOMERS.get(email)
    if customer is None:
        return {"isError": True, "errorCategory": "validation", "isRetryable": False,
                "message": f"No customer with email {email}."}
    _verified.add(email)                      # ← the gate opens here, server-side
    return {"isError": False, **customer}


@mcp.tool
def process_refund(email: str, order_id: str, amount: float) -> dict:
    """Refund an order for a verified customer.

    Requires get_customer to have been called for this email first.
    """
    if email not in _verified:
        # This is the whole point: not a hint, a refusal.
        return {"isError": True,
                "errorCategory": "business",
                "isRetryable": True,
                "message": f"Identity for {email} has not been verified in this session.",
                "nextStep": f"Call get_customer with email='{email}', then retry this call."}

    return {"isError": False, "orderId": order_id, "refunded": amount}


@mcp.tool
def end_session(email: str) -> dict:
    """Clear the verified state for a customer.

    Call when the conversation moves to a different customer.
    """
    _verified.discard(email)
    return {"isError": False, "cleared": email}


# -----------------------------------------------------------------------------
# WHY THE GATE RETURNS isRetryable=True
#
# Unusually, this failure IS retryable — but only after a different call. That is
# what nextStep is for: it names the recovery action, so a capable agent
# self-corrects in one hop (get_customer → retry) instead of surfacing a dead end
# to the user. Compare with skeleton 03's "already refunded", which is retryable
# by nobody and says so.
#
# THE TRAP
# Server-side state and statelessness pull against each other. This gate assumes
# one client per process — true for stdio, false for a shared HTTP server, where
# `_verified` would leak one user's verification to another user's session. If
# you have seen `get_customer` gating in a scenario question, the follow-up is
# usually "now it runs over HTTP for 500 users" — and the module-level set is
# then the vulnerability.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
