"""
Skeleton 06 · Paginated / large-result server — protecting the context window.

PATTERN           Bounded pages, a cursor to continue, and a total so the model
                  knows what it has not seen.
WHAT IT EXPOSES   A tool result goes into the context window and STAYS there for
                  the rest of the conversation. A single unbounded query that
                  returns 50,000 rows does not just cost tokens once — it can
                  blow the window outright, and if it does not, it crowds out
                  everything the agent still needs, on every subsequent turn.
                  The server, not the model, has to impose the bound: by the time
                  the model sees an oversized result, the damage is done.
EXAM SHAPE        "The tool returns 50,000 rows and the agent runs out of
                  context." → cap it server-side, paginate, and summarise.

Run:  python 06_paginated.py
"""

from fastmcp import FastMCP

mcp = FastMCP("log-search")

_MAX_LIMIT = 50                      # a ceiling the CALLER cannot raise
_ROWS = [{"id": i, "level": "error" if i % 7 == 0 else "info",
          "msg": f"event {i}"} for i in range(1, 1001)]


@mcp.tool
def search_logs(query: str, limit: int = 20, cursor: str | None = None) -> dict:
    """Search log events. Returns at most 50 rows per call.

    Response fields:
      rows        the matching events for this page
      totalCount  how many matched in total (may exceed the rows returned)
      nextCursor  pass back as `cursor` to fetch the next page; null when done
      truncated   true if more matches exist beyond this page

    If totalCount is large, narrow the query rather than paging through
    everything — do not fetch all pages just to count them.
    """
    matches = [r for r in _ROWS if query.lower() in r["msg"] or query == r["level"]]

    start = int(cursor) if cursor else 0
    size = min(limit, _MAX_LIMIT)                 # ← clamp; caller cannot exceed
    page = matches[start:start + size]
    end = start + len(page)

    return {
        "rows": page,
        "totalCount": len(matches),
        "nextCursor": str(end) if end < len(matches) else None,
        "truncated": end < len(matches),
    }


@mcp.tool
def summarise_logs(query: str) -> dict:
    """Count and bucket matching log events WITHOUT returning the rows.

    Prefer this over search_logs when you need "how many" or "what kind" rather
    than the individual events — it costs a fraction of the context.
    """
    matches = [r for r in _ROWS if query.lower() in r["msg"] or query == r["level"]]
    buckets: dict[str, int] = {}
    for r in matches:
        buckets[r["level"]] = buckets.get(r["level"], 0) + 1
    return {"totalCount": len(matches), "byLevel": buckets,
            "sample": matches[:3]}


# -----------------------------------------------------------------------------
# THE FOUR MOVES, IN PRIORITY ORDER
#
# 1. CLAMP.       min(limit, _MAX_LIMIT). If the ceiling is a parameter the model
#                 can set, it is not a ceiling. This is the one that actually
#                 saves you; the rest are refinements.
# 2. SIGNAL.      `truncated` + `totalCount`. Silent truncation is the real
#                 hazard — the agent confidently reports "3 errors" when there
#                 were 300 and it saw a page. Unknown-unknowns become known.
# 3. CONTINUE.    `nextCursor`. Opaque to the model; it just passes it back.
# 4. AGGREGATE.   summarise_logs. The best large result is the one you never
#                 return: most "how many failed?" questions need a count, not
#                 rows. Offering the cheap tool alongside the expensive one lets
#                 the model pick correctly — provided the description says which
#                 is which, which is why both descriptions cross-reference.
#
# THE SECOND-ORDER POINT: pagination protects the window, but paging through 40
# pages costs more than one summarise call AND fills the window anyway. That is
# why the description explicitly tells the model not to page just to count.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
