"""
Smoke-test every skeleton in-process, with no subprocess and no network.

FastMCP's Client can connect straight to a FastMCP object, which is the fastest
way to see a server from the model's side of the wire: list the tools, call one,
read a resource. Run this after editing any skeleton.

    pip install fastmcp
    python test_skeletons.py
"""

import asyncio
import importlib.util
import os
import pathlib
import sys

from fastmcp import Client

HERE = pathlib.Path(__file__).parent
os.environ.setdefault("API_TOKEN", "demo-token-xyz")      # skeleton 07 needs it


def load(filename: str):
    """Import a skeleton by filename (they start with digits, so no plain import)."""
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


async def check(label: str, server, body) -> None:
    async with Client(server) as client:
        tools = [t.name for t in await client.list_tools()]
        await body(client, tools)
    print(f"  ✓ {label}  tools={tools}")


async def main() -> None:
    print("Testing MCP skeletons against fastmcp\n")

    # 01 — tools only
    async def t01(c, tools):
        assert tools == ["search_orders", "get_order"], tools
        r = await c.call_tool("search_orders", {"customer_email": "ana@example.com"})
        assert len(r.data) == 2, r.data
        # every tool carries a real description — the selection mechanism
        for t in await c.list_tools():
            assert t.description and len(t.description) > 60, t.name
    await check("01 tools-only", load("01_tools_only.py").mcp, t01)

    # 02 — resources
    async def t02(c, tools):
        uris = [str(r.uri) for r in await c.list_resources()]
        assert "policy://index" in uris, uris
        templates = [str(t.uriTemplate) for t in await c.list_resource_templates()]
        assert "policy://{topic}" in templates, templates
        doc = await c.read_resource("policy://refunds")
        assert "30 days" in doc[0].text, doc
        r = await c.call_tool("search_policies", {"query": "shipping"})
        assert "shipping" in r.data, r.data
    await check("02 resources", load("02_resources.py").mcp, t02)

    # 03 — structured errors: every category, and the raised-vs-returned split
    async def t03(c, tools):
        cases = [
            ({"order_id": "NOPE", "amount": 5, "requester_email": "ana@example.com"},
             "validation", False),
            ({"order_id": "A-1001", "amount": 5, "requester_email": "bo@example.com"},
             "permission", False),
            ({"order_id": "A-1003", "amount": 5, "requester_email": "bo@example.com"},
             "business", False),
            ({"order_id": "A-1001", "amount": 999, "requester_email": "ana@example.com"},
             "validation", True),
        ]
        for args, category, retryable in cases:
            r = await c.call_tool("process_refund", args)
            assert r.data["errorCategory"] == category, (args, r.data)
            assert r.data["isRetryable"] is retryable, (args, r.data)
            assert r.data["nextStep"], r.data
        ok = await c.call_tool("process_refund",
                               {"order_id": "A-1001", "amount": 10,
                                "requester_email": "ana@example.com"})
        assert ok.data["isError"] is False, ok.data
    await check("03 structured-errors", load("03_structured_errors.py").mcp, t03)

    # 04 — the gate: refuse, then open, then close
    async def t04(c, tools):
        blocked = await c.call_tool("process_refund",
                                    {"email": "ana@example.com", "order_id": "A-1001",
                                     "amount": 10})
        assert blocked.data["isError"] is True, blocked.data
        assert "get_customer" in blocked.data["nextStep"], blocked.data

        await c.call_tool("get_customer", {"email": "ana@example.com"})
        allowed = await c.call_tool("process_refund",
                                    {"email": "ana@example.com", "order_id": "A-1001",
                                     "amount": 10})
        assert allowed.data["isError"] is False, allowed.data

        await c.call_tool("end_session", {"email": "ana@example.com"})
        again = await c.call_tool("process_refund",
                                  {"email": "ana@example.com", "order_id": "A-1001",
                                   "amount": 10})
        assert again.data["isError"] is True, again.data
    await check("04 gated-stateful", load("04_gated_stateful.py").mcp, t04)

    # 05 — three backends, one contract
    async def t05(c, tools):
        r = await c.call_tool("search_tickets", {"query": "n"})   # matches all three
        assert len(r.data) == 3, r.data
        for row in r.data:
            assert set(row) == {"id", "title", "status", "createdDate", "source"}, row
            assert row["status"] in {"open", "in_progress", "closed"}, row
            assert len(row["createdDate"]) == 10 and row["createdDate"][4] == "-", row
            assert row["id"].split(":")[0] in {"sf", "zd", "lg"}, row
    await check("05 heterogeneous-backend", load("05_heterogeneous_backend.py").mcp, t05)

    # 06 — the clamp is the load-bearing part
    async def t06(c, tools):
        r = await c.call_tool("search_logs", {"query": "event", "limit": 10_000})
        assert len(r.data["rows"]) == 50, len(r.data["rows"])       # clamped
        assert r.data["truncated"] is True and r.data["totalCount"] == 1000, r.data

        page2 = await c.call_tool("search_logs",
                                  {"query": "event", "cursor": r.data["nextCursor"]})
        assert page2.data["rows"][0]["id"] != r.data["rows"][0]["id"], "cursor stuck"

        s = await c.call_tool("summarise_logs", {"query": "event"})
        assert s.data["totalCount"] == 1000 and len(s.data["sample"]) == 3, s.data
    await check("06 paginated", load("06_paginated.py").mcp, t06)

    # 07 — env config, and the token must never come back
    async def t07(c, tools):
        r = await c.call_tool("whoami", {})
        assert "demo-token-xyz" not in str(r.data), "token leaked in whoami!"
        assert "…" in r.data["tokenFingerprint"], r.data
    await check("07 env-config", load("07_env_config.py").mcp, t07)

    # 08 — same tool name, two servers, descriptions that disambiguate
    mod08 = load("08_namespacing.py")

    async def t08a(c, tools):
        assert tools == ["search"], tools
        d = (await c.list_tools())[0].description
        assert "DOCUMENTATION" in d and "Do NOT" in d, d
    await check("08 namespacing (docs)", mod08.docs, t08a)

    async def t08b(c, tools):
        assert tools == ["search"], tools
        d = (await c.list_tools())[0].description
        assert "TICKETS" in d and "Do NOT" in d, d
    await check("08 namespacing (tickets)", mod08.tickets, t08b)

    print("\nAll skeletons OK.")


if __name__ == "__main__":
    asyncio.run(main())
