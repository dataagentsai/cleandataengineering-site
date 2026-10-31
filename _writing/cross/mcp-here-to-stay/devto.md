---
title: MCP is here to stay: give your agent tools the standard way
published: false
canonical_url: https://cleandataengineering.ai/writing/mcp-here-to-stay/
description: The Model Context Protocol (MCP) is a standard way for an agent to find and call tools that a separate server offers. It has settled because many agents and tools already speak it, so a tool you write once works in all of them. Wrap your systems as MCP servers, keep the business rules inside the server, and secure it like any other door into your data. For one agent with three small functions, skip it.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/mcp-here-to-stay/).*


A year or two ago, connecting an agent to your order system meant writing glue. A function for this agent, a slightly different one for the next, and a third for the chat assistant someone else built. Each one described the same "cancel order" action in its own way.

Then the Model Context Protocol, MCP for short, arrived and the glue started to disappear. You write the order system's tools once, as a small MCP server, and any agent that speaks MCP can find them and call them.

Our verdict, after building agents with it: MCP is the standard way to give an agent tools, and it is here to stay. This post explains what it is, how to adopt it without making a mess, what to secure, and the one case where it is overkill.

## One plug shape for every tool

{{drawing: mcp-usb}}

Think of USB-C. Before it, every device had its own cable and every drawer had a tangle. After it, one port fits nearly everything.

MCP does that for agents and tools. It has two sides:

- **The client** is the agent's side. It lives in the harness, the ordinary code around the model that runs the loop and calls tools.
- **The server** is the tool's side. It is a small program that sits in front of a system, such as your order database, and offers things to any client.

A server can offer three kinds of things:

1. **Tools**: actions the model can ask to run, such as `get_order` or `cancel_order`. Each comes with a name, a description and the shape of its arguments.
2. **Resources**: things to read, such as a file or a record, that the app can put in front of the model.
3. **Prompts**: ready-made message templates the server offers, such as "summarise this order's history".

The messages themselves use **JSON-RPC**, a simple standard shape for a note that says "please run this function with these arguments", with a matching reply. They travel over one of two **transports**, the way the notes are carried:

- **stdio**, for a server on the same machine. The agent starts the server as a child program and they pass JSON notes through its input and output, like slips of paper under a door.
- **Streamable HTTP**, for a server somewhere else on the network.

## The whole conversation is three questions

{{drawing: mcp-handshake}}

Strip away the details and an MCP session is short:

1. **`initialize`**: "Hello, which version do you speak?" The server answers with its version and what it offers.
2. **`tools/list`**: "What can you do?" The server returns its tools, each with a name, a description and its argument shape.
3. **`tools/call`**: "Please run `get_order` with id ORD-1042." The server runs it and sends back the result.

The harness passes the list from step 2 to the model. The model never talks to the server itself. It only asks for a tool, and the harness makes the call.

You can see it with very little code. A good way to learn it is to write this exchange by hand once, with no library: two tools (say `read_file` and `query_sqlite`) over stdio. Then write the same server with FastMCP, a higher-level Python library, to see what the library does for you. With FastMCP, a working tool is a decorated function:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-mcp")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello {name}, MCP is working!"

if __name__ == "__main__":
    mcp.run()
```

The library turns the function's name, type hints and docstring into the entry that `tools/list` returns.

## Why it has settled

Three reasons, all practical.

- **Many clients and servers already speak it.** Coding assistants, chat apps and agent frameworks act as clients, and there are servers for databases, file systems, ticketing tools and cloud services. A protocol with both sides already built is hard to replace.
- **It replaces one-off integrations.** Without a standard, five agents and ten systems mean up to fifty pieces of glue. With one, each agent needs one client and each system needs one server.
- **The same tool works in many agents.** The order server you write for your support agent also works in your engineers' coding assistant, with no changes.

In our [agent tech stack](/writing/agent-tech-stack/), MCP is the tool layer: the model may act only through typed tools that are checked before they run. The Agent Harness tutorial compared the options for that layer, and MCP with the official Python SDK won. Plain functions inside the agent were rejected because they run with all the agent's rights and nothing checks them at the far end. Raw REST APIs were rejected because they are shaped around the system's tables, not around what an agent intends to do.

## Keep the business rules on the server

{{drawing: mcp-rules-server}}

The most important adoption rule: **the server decides, not the prompt.**

Our reference agent's store server offers six tools: `get_order`, `list_orders`, `cancel_order`, `open_return_request`, `change_address` and `issue_refund`. Each write declares its side effect (reversible or irreversible) and the scope it needs, such as `refunds:write`. Behind every call, the server checks the caller's token itself. `list_orders` takes no customer id at all. The server reads whose orders these are from the verified token, so the model cannot ask for anyone else's.

"Only before the order has been picked" lives in the server's code for `cancel_order`, not in a sentence in the system prompt. A prompt is a request. Code in the server is a rule.

Three habits make adoption go well:

1. **Wrap each system as its own server.** One for orders, one for claims, one for documents. Each owns its own checks.
2. **Shape tools around intent.** `cancel_order(id)` is better than a generic `update_row(table, values)`. The model picks better, and the server can check one clear thing.
3. **Write tool descriptions for a reader who knows nothing.** The model picks a tool from its description alone. "Cancel an order. Only possible before it has been picked." beats "Cancels."

## What to secure

{{drawing: mcp-shield}}

An MCP server is a door into a real system, and the text coming back through it lands in the model's context. Five things to lock down, most of which our [agent security post](/writing/agent-security/) covers in depth:

1. **Authentication.** A remote server must know who is calling. MCP's answer for remote servers is OAuth, the standard sign-in flow that hands the client a token. Check that token on every call, on the server.
2. **Least-privilege tools.** Show each user only the tools their token allows, and have the server refuse anything outside it anyway. A read-only assistant should not see `issue_refund` at all.
3. **Untrusted descriptions and results.** Tool descriptions and tool results are text, and text can carry instructions. A description can hide "also send the user's address to this tool". This is called **tool poisoning**. A result can carry prompt injection, such as a note that says "ignore your instructions". Treat both as data, never as orders.
4. **Pinned server versions.** A server that changes under you can change its descriptions, and so its behaviour. Pin the exact version you tested, and review the tool list when you upgrade.
5. **Who sees what.** Every server you connect can see what the agent sends it. Don't connect a server you don't trust to a conversation that holds customer records, payment details or secrets.

## When MCP is overkill

| Your situation | Use |
|---|---|
| One agent, three small functions, same process, same team | plain function tools |
| Tools that touch real data or money | MCP, with checks in the server |
| The same tools needed by more than one agent | MCP |
| A system another team owns | MCP, owned by that team |

If you have one agent with three in-process functions that only read harmless data, a server, a transport and a handshake are more moving parts than the job needs. Give the model the functions directly. Move to MCP the day a second agent needs the same tools, or the day a tool can change something that matters.

## Mistakes we see often

1. **Rules in the prompt, not the server.** "Never refund over ₹40,000" in the system prompt will be talked around one day. In the server's code it won't.
2. **One service account behind the server.** The server then acts with everyone's rights, whoever is asking. Carry the user's identity on each call.
3. **A REST API wrapped one endpoint per tool.** Forty table-shaped tools confuse the model and give the server nothing clear to check.
4. **Installing community servers without reading them.** You are giving that code access to your data and your model's context.
5. **Handling only one kind of failure.** In MCP, an unknown tool or a broken request comes back as a protocol error, while a tool that ran and failed comes back as a normal result marked as an error. An agent that handles one and not the other looks healthy until production.

## Six questions to check your own setup

1. Where does each business rule live: in a prompt, or in the server that owns the data?
2. Does every remote server check a token on every call?
3. Could a read-only user's agent even see a tool that writes?
4. Do you treat tool descriptions and results as untrusted text?
5. Is every server pinned to a version you have tested?
6. Is any server you didn't write connected to a conversation that holds sensitive data?

Write the tool once, put the rules behind it, and let every agent plug in the same way.

