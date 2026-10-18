"""
Skeleton 02 · Resources server — a content catalogue.

PATTERN           Expose readable content as *resources*, addressed by URI,
                  instead of as tools.
WHAT IT EXPOSES   The tool-vs-resource boundary, which is a control question, not
                  a data question:
                      tool      = model-controlled. The model decides to call it.
                                  May have side effects. Verb.
                      resource  = application-controlled. The CLIENT decides to
                                  read it and put it in context. Read-only. Noun.
                  A resource is closer to a file in a repo than to a function.
EXAM SHAPE        "Should this be a tool or a resource?" → ask who chooses, and
                  whether it changes anything. Read-only + client picks = resource.

Note the pragmatic caveat at the bottom: not every client supports resources.

Run:  python 02_resources.py
"""

from fastmcp import FastMCP

mcp = FastMCP("policy-catalogue")

_DOCS = {
    "refunds": "Refunds are accepted within 30 days of delivery, unworn, with tags.",
    "shipping": "Standard shipping is 3-5 business days. Express is next business day.",
    "returns": "Return shipping is free for exchanges, £4.99 deducted for refunds.",
}


# --- Static resource: one fixed URI ------------------------------------------
@mcp.resource("policy://index")
def policy_index() -> str:
    """The list of available policy documents."""
    return "\n".join(f"policy://{name}" for name in _DOCS)


# --- Resource template: URI with a parameter ---------------------------------
# The {topic} placeholder makes this a *template*. Clients list it separately
# from static resources — it is a family of addresses, not one address.
@mcp.resource("policy://{topic}")
def policy_doc(topic: str) -> str:
    """The full text of one policy document."""
    return _DOCS.get(topic, f"No policy document named '{topic}'.")


# --- The same catalogue, exposed the OTHER way, for contrast -----------------
# Identical data. Different control model: here the MODEL decides to fetch, and
# it can search — something a resource URI cannot express.
@mcp.tool
def search_policies(query: str) -> list[str]:
    """Search the policy documents for a keyword and return matching topics.

    Use when you do not know which policy covers the customer's question.
    """
    q = query.lower()
    return [name for name, text in _DOCS.items() if q in text.lower() or q in name]


# -----------------------------------------------------------------------------
# THE DECISION, IN ONE LINE EACH
#
#   Known address, client attaches it        → resource   ("read policy://refunds")
#   Needs searching / arguments / a decision → tool       ("find the right policy")
#   Changes state, sends, charges, deletes   → tool, always
#
# THE PRACTICAL CAVEAT — worth knowing, and a common trap:
# resource support is client-dependent. Claude Code surfaces MCP resources via
# @-mention; some clients ignore resources entirely and see only your tools. If a
# server exposes something ONLY as a resource, on those clients it is invisible.
# Servers that must work everywhere often expose both, exactly as this one does.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
