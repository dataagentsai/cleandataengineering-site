"""
Skeleton 05 · Heterogeneous-backend server — one contract over three upstreams.

PATTERN           Three systems that disagree about everything — field names,
                  date formats, status vocabularies, ID shapes — presented to the
                  model as a single uniform tool.
WHAT IT EXPOSES   Where normalisation belongs. If you expose the three upstreams
                  raw (search_salesforce, search_zendesk, search_legacy_db), you
                  have pushed a mapping problem into the model's reasoning, and it
                  will pay for it on every single call: three schemas to remember,
                  three status vocabularies to reconcile, and cross-system
                  comparisons done in prose. Normalising in the server costs you
                  30 lines once. Normalising in the model costs tokens forever —
                  and it is only probably right.
EXAM SHAPE        "Three CRMs with different formats; how should the MCP server
                  expose them?" → one tool, one normalised contract, mapping in
                  the server.

Run:  python 05_heterogeneous_backend.py
"""

from fastmcp import FastMCP

mcp = FastMCP("unified-tickets")

# --- The three upstreams, each wrong in its own way --------------------------
_SALESFORCE = [
    {"Id": "500xx1", "Subject": "Login fails", "Status": "Working",
     "CreatedDate": "2026-08-19T09:14:00.000+0000"},
]
_ZENDESK = [
    {"id": 88231, "subject": "Refund not received", "status": "open",
     "created_at": "2026-08-20T11:02:00Z"},
]
_LEGACY = [
    {"TICKET_NO": 4471, "DESCR": "Cannot update address", "STATE": "P",
     "CREATED": "20260821"},          # yyyymmdd, no timezone at all
]

# The vocabularies disagree; the server owns the mapping table.
_STATUS = {
    "Working": "in_progress", "Escalated": "in_progress", "Closed": "closed",
    "open": "open", "pending": "in_progress", "solved": "closed",
    "N": "open", "P": "in_progress", "C": "closed",
}


def _iso(value: str) -> str:
    """Everything upstream becomes one date format: YYYY-MM-DD."""
    if len(value) == 8 and value.isdigit():            # legacy 20260821
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return value[:10]                                   # both ISO variants


@mcp.tool
def search_tickets(query: str, limit: int = 20) -> list[dict]:
    """Search support tickets across every connected system.

    Returns tickets in ONE format regardless of which system they came from:
      id (str), title (str), status (open|in_progress|closed),
      createdDate (YYYY-MM-DD), source (salesforce|zendesk|legacy).
    Statuses and dates are already normalised — do not convert them yourself.
    """
    q = query.lower()
    out: list[dict] = []

    for r in _SALESFORCE:
        out.append({"id": f"sf:{r['Id']}", "title": r["Subject"],
                    "status": _STATUS.get(r["Status"], "unknown"),
                    "createdDate": _iso(r["CreatedDate"]), "source": "salesforce"})
    for r in _ZENDESK:
        out.append({"id": f"zd:{r['id']}", "title": r["subject"],
                    "status": _STATUS.get(r["status"], "unknown"),
                    "createdDate": _iso(r["created_at"]), "source": "zendesk"})
    for r in _LEGACY:
        out.append({"id": f"lg:{r['TICKET_NO']}", "title": r["DESCR"],
                    "status": _STATUS.get(r["STATE"], "unknown"),
                    "createdDate": _iso(r["CREATED"]), "source": "legacy"})

    return [t for t in out if q in t["title"].lower()][:limit]


# -----------------------------------------------------------------------------
# THE TWO DESIGN DECISIONS WORTH NOTICING
#
# 1. IDs are PREFIXED (sf: / zd: / lg:). Upstream, ticket 88231 and ticket 4471
#    live in different systems and could collide. A prefixed ID is unambiguous,
#    round-trips back to the right upstream, and lets one get_ticket tool serve
#    all three. Never hand the model a bare ID whose namespace it must infer.
#
# 2. `source` is KEPT. Normalising is not the same as hiding. The model may need
#    to say "this one is in the legacy system, which is read-only" — so the
#    contract is uniform, but provenance survives.
#
# THE LIMIT OF THE PATTERN: normalise the SHAPE, never the MEANING. If Zendesk's
# "solved" and Salesforce's "Closed" carry genuinely different business meaning,
# collapsing both to "closed" destroys information the model needed. When the
# vocabularies do not truly align, keep a `sourceStatus` field alongside.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
