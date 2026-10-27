"""
Skeleton 03 · Structured-error server — telling the agent what to DO next.

PATTERN           Every failure carries a category and a retryability flag, in a
                  shape the model can act on.
WHAT IT EXPOSES   An error string is not an error contract. "Request failed" tells
                  the agent nothing about whether to retry, fix its arguments,
                  give up, or escalate to a human — so it guesses, and the classic
                  failure is an infinite retry loop against a permanent error.
                  Four categories cover almost everything:
                      transient   → retry, with backoff        (503, timeout)
                      validation  → fix the arguments, retry    (bad date format)
                      business    → do NOT retry, explain        (already refunded)
                      permission  → do NOT retry, escalate       (not your order)
EXAM SHAPE        "The agent retried a failing tool 20 times" / "the agent gave up
                  on a request that would have succeeded a second later."

Run:  python 03_structured_errors.py
"""

from dataclasses import dataclass, asdict

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP("refunds")


@dataclass
class Failure:
    """The error contract. Same keys on every failure, always."""
    isError: bool
    errorCategory: str      # transient | validation | business | permission
    isRetryable: bool
    message: str            # for the model to relay to the user
    nextStep: str           # what the model should actually do now


def fail(category: str, retryable: bool, message: str, next_step: str) -> dict:
    return asdict(Failure(True, category, retryable, message, next_step))


_ORDERS = {
    "A-1001": {"owner": "ana@example.com", "refunded": False, "total": 82.50},
    "A-1003": {"owner": "bo@example.com", "refunded": True, "total": 240.00},
}


@mcp.tool
def process_refund(order_id: str, amount: float, requester_email: str) -> dict:
    """Refund an order, in full or in part.

    On failure this returns an object with isError=true, an errorCategory of
    transient/validation/business/permission, and isRetryable. Retry ONLY when
    isRetryable is true. Follow the nextStep field.
    """
    order = _ORDERS.get(order_id)

    if order is None:
        return fail("validation", False,
                    f"No order '{order_id}'. IDs look like 'A-1001'.",
                    "Ask the customer to confirm the order ID, or call search_orders.")

    if order["owner"] != requester_email:
        return fail("permission", False,
                    "That order belongs to a different customer.",
                    "Do not retry. Escalate to a human agent.")

    if order["refunded"]:
        return fail("business", False,
                    f"Order {order_id} was already refunded in full.",
                    "Do not retry. Tell the customer it is already done.")

    if amount > order["total"]:
        return fail("validation", True,
                    f"Amount {amount} exceeds the order total {order['total']}.",
                    f"Retry with an amount of {order['total']} or less.")

    if _payment_gateway_down():
        return fail("transient", True,
                    "The payment gateway is temporarily unavailable.",
                    "Wait a few seconds and retry the identical call.")

    order["refunded"] = True
    return {"isError": False, "orderId": order_id, "refunded": amount}


def _payment_gateway_down() -> bool:
    return False            # flip to True to watch the agent back off and retry


# -----------------------------------------------------------------------------
# RETURNED ERROR  vs  RAISED ERROR — two different mechanisms, both here.
#
# Everything above RETURNS a dict. The call succeeded at the protocol level; the
# payload describes a business failure. The model reads the fields and routes.
#
# Raising is the other channel — it sets the protocol-level isError flag:
#
#     raise ToolError("The payment gateway is unavailable")
#         → the model sees exactly this text. Safe: you chose it.
#
#     raise ValueError("conn refused: pg://admin:hunter2@10.0.0.4")
#         → in FastMCP 3.x the model sees:
#           "Error calling tool 'x': conn refused: pg://admin:hunter2@10.0.0.4"
#           An internal detail — a DSN with a password — just went into the
#           transcript. VERIFIED against fastmcp 3.4.7, not assumed.
#
# THE RULE: catch your exceptions. Re-raise as ToolError with a message you wrote,
# or return a structured Failure. Never let a raw stack-trace message reach the
# model — it is both a context leak and a security leak.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
