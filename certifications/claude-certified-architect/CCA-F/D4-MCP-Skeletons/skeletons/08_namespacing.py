"""
Skeleton 08 · Namespacing & collision — two servers, similar tools, one agent.

PATTERN           Two servers are connected at once and both offer something
                  called "search". This file defines BOTH, so the collision is
                  visible in one place.
WHAT IT EXPOSES   What the client does about name collisions, and — the part that
                  actually bites — what it cannot do about DESCRIPTION collisions.
                  Clients namespace tool names by server, so the wire-level clash
                  is handled for you: the model sees mcp__docs__search and
                  mcp__tickets__search, and cannot literally call the wrong name.
                  But it still has to CHOOSE. If both descriptions say "Search
                  for information", the namespacing was cosmetic — the model
                  picks by coin-flip, and it will pick wrong roughly half the
                  time, on every ambiguous request.
EXAM SHAPE        "Two MCP servers expose similar tools and the agent picks the
                  wrong one." → disambiguate the DESCRIPTIONS. Renaming alone
                  does not fix selection.

Run:  python 08_namespacing.py          # runs the "docs" server
"""

from fastmcp import FastMCP

# --- Server A ----------------------------------------------------------------
docs = FastMCP("docs")


@docs.tool
def search(query: str) -> list[str]:
    """Search internal ENGINEERING DOCUMENTATION — architecture notes, runbooks,
    API references, design docs.

    Use for "how does X work", "where is X configured", "what is our policy on X".
    Do NOT use for customer conversations or support history — that is the
    tickets server.
    """
    return [f"docs hit for {query!r}"]


# --- Server B ----------------------------------------------------------------
tickets = FastMCP("tickets")


@tickets.tool
def search(query: str) -> list[str]:            # noqa: F811 — same name on purpose
    """Search CUSTOMER SUPPORT TICKETS — conversations with customers, bug
    reports they filed, refund and complaint history.

    Use for "has anyone reported X", "what did we tell this customer", "how many
    complaints about X". Do NOT use for internal documentation — that is the
    docs server.
    """
    return [f"ticket hit for {query!r}"]


# -----------------------------------------------------------------------------
# WHAT THE MODEL ACTUALLY SEES, WITH BOTH SERVERS CONNECTED
#
#     mcp__docs__search      "Search internal ENGINEERING DOCUMENTATION …"
#     mcp__tickets__search   "Search CUSTOMER SUPPORT TICKETS …"
#
# The prefix is added by the CLIENT, not by you — you cannot control it from the
# server, and you should not try to fake it by naming your tool
# "docs_search_docs" (which becomes mcp__docs__docs_search_docs, wasting tokens
# on every request for no gain).
#
# THE THREE MOVES THAT ACTUALLY DISAMBIGUATE
# 1. Lead with the DOMAIN, in caps or first words. The model reads the start of
#    the description most reliably: "Search CUSTOMER SUPPORT TICKETS…".
# 2. State the NEGATIVE. "Do NOT use for X — that is the Y server." A boundary is
#    far more selective than another positive claim.
# 3. Give TRIGGER PHRASES. Quoting the shape of the request ("has anyone
#    reported X") matches how the user will actually phrase it.
#
# THE OTHER COST, AND THE REAL EXAM ANSWER
# Every connected server's full tool list sits in the context window on every
# single request. Ten servers × eight tools is eighty descriptions the model
# re-reads each turn — tokens, latency, and more chances to choose wrong. The
# strongest fix for tool confusion is usually not better descriptions at all:
# it is connecting fewer servers. Disambiguate what you keep; disconnect the
# rest.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    docs.run()
