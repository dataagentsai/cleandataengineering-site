"""
Skeleton 01 · Tools-only server — the baseline.

PATTERN           Expose capabilities as tools. Nothing else. This is the shape
                  ~80% of real MCP servers actually have.
WHAT IT EXPOSES   The tool *description* is the selection mechanism. The model
                  never sees your source, your function body or your intent —
                  only three fields: name, description, inputSchema. Anything you
                  need it to get right has to live in those three.
EXAM SHAPE        "The agent calls the wrong tool / never calls the tool /
                  calls it with the wrong arguments." The fix is almost always
                  the description, not the code.

Run:  python 01_tools_only.py          # stdio transport
"""

from fastmcp import FastMCP

mcp = FastMCP("orders-baseline")

# --- fake data, so the skeleton runs with no backend -------------------------
_ORDERS = [
    {"id": "A-1001", "email": "ana@example.com", "status": "shipped", "total": 82.50},
    {"id": "A-1002", "email": "ana@example.com", "status": "pending", "total": 19.00},
    {"id": "A-1003", "email": "bo@example.com", "status": "cancelled", "total": 240.00},
]


@mcp.tool
def search_orders(customer_email: str, limit: int = 10) -> list[dict]:
    """Find a customer's orders by their email address.

    Use this when you have an email address and need the order IDs belonging to
    it. Returns newest first. Does NOT include line items or shipping details —
    call get_order with a specific order ID for those.
    """
    hits = [o for o in _ORDERS if o["email"] == customer_email]
    return hits[:limit]


@mcp.tool
def get_order(order_id: str) -> dict:
    """Retrieve the full record for ONE order, given its exact order ID.

    Order IDs look like "A-1001". If you only have a customer's email, call
    search_orders first to obtain the ID — this tool cannot look up by email.
    """
    for o in _ORDERS:
        if o["id"] == order_id:
            return o
    return {"error": "not_found", "order_id": order_id}


# -----------------------------------------------------------------------------
# THE CONTRAST THAT MAKES THE POINT
#
# The two descriptions above do four things a weak one does not:
#   1. say WHEN to use the tool ("when you have an email address")
#   2. say what it does NOT do   ("does not include line items")
#   3. point at the companion tool ("call search_orders first")
#   4. show the argument's shape  ('Order IDs look like "A-1001"')
#
# The weak version of the same tool — everything the model needs is missing,
# and no amount of prompt engineering upstream recovers it:
#
#     @mcp.tool
#     def get_order(order_id: str) -> dict:
#         """Gets an order."""          # ✗ when? by ID or email? what comes back?
#
# Rule of thumb: write the description for a competent new hire who can see the
# signature but has never seen the system.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
