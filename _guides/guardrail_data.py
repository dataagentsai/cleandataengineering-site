"""The guardrail catalog: one row per common guardrail for autonomous agents.

Used by _guides/guardrails.py (the reference page) and by the blog post's drawings.
Built from the Agent Harness tutorial's checks (8 points of a turn) and the AI Assurance
Catalog's obligations (AAC ids cite the test that proves the guardrail works).

Fields: name, what it catches, where, priority, how, on fail, concern, aac, example tools
  where:    see WHERE (in the order a turn passes them)
  priority: must · should · could   (must = every agent that can act; should = most; could = some)
  how:      rule · classifier · judge · person · platform
To add one, copy a row. Keep "what it catches" a plain example a reader would recognise.
"""

WHERE = {
    "door": "Front door",
    "pre": "Before the model",
    "post": "After the model",
    "tool": "Before the tool",
    "far": "Inside the tool",
    "result": "After the tool",
    "run": "Whole run",
    "ops": "Logs and platform",
}
PRIORITY = {"must": "Must have", "should": "Should have", "could": "Could have"}
HOW = {
    "rule": ("Rule in code", "deterministic: same input, same answer", "about 0 ms, free"),
    "classifier": ("Small classifier", "a small trained model gives a score", "10 to 100 ms, cheap"),
    "judge": ("LLM judge", "another model reads and decides", "0.5 to 3 s, costs tokens"),
    "person": ("A person", "a human approves or takes over", "minutes to days"),
    "platform": ("Platform setting", "the cloud or runtime enforces it", "about 0 ms"),
}
CONCERNS = {"security": "Security", "safety": "Safety", "privacy": "Privacy", "grounding": "Truth",
            "correctness": "Correctness", "cost": "Cost", "reliability": "Reliability", "oversight": "Human oversight"}

G = [
    # ---- Front door: before anything thinks
    ("Verify who is asking", "a forged or expired sign-in", "door", "must", "rule", "block", "security", "AAC-0111", "your identity provider"),
    ("Kill switch", "the agent has been switched off by an operator", "door", "must", "rule", "block", "reliability", "AAC-0077", "a feature flag"),
    ("Same message twice", "a double-click or a retry sends the message again", "door", "must", "rule", "return the first answer", "reliability", "AAC-0076", "an idempotency table"),
    ("Input size and shape", "an empty, huge or binary message", "door", "must", "rule", "block", "reliability", "AAC-0015", "your code"),
    ("Rate limit and quota", "one user sending 500 messages a minute", "door", "should", "rule", "slow down", "cost", "AAC-0093", "API gateway (APIM, Kong, LiteLLM)"),
    ("Sensitive topics go to a person", "injury, self-harm, legal threats, fraud claims", "door", "must", "rule", "hand to a person", "safety", "AAC-0005", "keyword rules, then a classifier"),
    ("Off-topic request", "a banking agent asked to write a poem", "door", "should", "classifier", "polite refusal", "correctness", "AAC-0020", "embedding similarity or a small classifier"),
    ("Record what the user asked for", "lists the actions the user's own words asked for, used later at the tool", "door", "must", "rule", "used later", "security", "AAC-0056", "your code"),

    # ---- Before the model
    ("Known injection phrases", "\"ignore your previous instructions\", fake role markers", "pre", "must", "rule", "block", "security", "AAC-0004", "a pattern list"),
    ("Jailbreak and prompt attack detector", "reworded or foreign-language attacks the patterns miss", "pre", "should", "classifier", "block", "security", "AAC-0004", "Prompt Shields, Llama Prompt Guard 2, Lakera"),
    ("Harmful input", "hate, violence, sexual or self-harm content", "pre", "must", "classifier", "block", "safety", "AAC-0005", "Azure Content Safety, Llama Guard, Bedrock Guardrails"),
    ("Personal data in the input", "a card number or passport number pasted into chat", "pre", "should", "classifier", "redact", "privacy", "AAC-0006", "Presidio, Comprehend, Cloud DLP"),
    ("Secrets in the input", "an API key or password pasted into chat", "pre", "should", "rule", "redact", "privacy", "AAC-0006", "secret-scanner patterns"),
    ("Only the tools this user may use", "an ordinary user's agent offered the admin tools", "pre", "must", "rule", "never shown", "security", "AAC-0057", "your code"),
    ("Context size cap", "a conversation that has grown past the window", "pre", "must", "rule", "trim", "reliability", "AAC-0019", "your code"),
    ("Approved models only", "a request routed to an unapproved or unknown model", "pre", "should", "platform", "block", "oversight", "AAC-0094", "LLM gateway allow-list"),
    ("Data stays in its region", "personal data sent to a model in another country", "pre", "could", "platform", "block", "privacy", "AAC-0097", "regional endpoints, gateway policy"),

    # ---- After the model: it has written an answer or asked for a tool
    ("Output matches its schema", "missing fields, wrong types, broken JSON", "post", "must", "rule", "repair or retry", "correctness", "AAC-0002", "Pydantic, JSON Schema, structured outputs"),
    ("Harmful output", "the model writes something offensive or dangerous", "post", "must", "classifier", "block", "safety", "AAC-0005", "Azure Content Safety, Llama Guard, Bedrock Guardrails"),
    ("Personal data in the output", "the reply repeats another person's phone number", "post", "must", "classifier", "redact", "privacy", "AAC-0006", "Presidio, regex for IDs"),
    ("Claims an action that didn't happen", "\"I've booked it\" when no booking tool ran", "post", "must", "rule", "safe reply", "grounding", "AAC-0110", "compare the reply with the tool log"),
    ("Names or numbers no tool returned", "an order number or price the model made up", "post", "must", "rule", "safe reply", "grounding", "AAC-0024", "match entities against tool results"),
    ("Every claim is supported", "a sentence the retrieved documents don't support", "post", "should", "judge", "regenerate or flag", "grounding", "AAC-0029", "an LLM judge, or an NLI model"),
    ("Citations point to real sources", "a link or document id that doesn't exist", "post", "should", "rule", "remove the citation", "grounding", "AAC-0030", "your code"),
    ("Forbidden promises", "\"your claim will be approved\", legal or medical advice", "post", "must", "rule", "safe reply", "safety", "AAC-0003", "phrase rules, then an LLM judge for nuance"),
    ("Units, currency and format", "£ instead of ₹, a date in the wrong format", "post", "should", "rule", "fix or safe reply", "correctness", "AAC-0023", "your code"),
    ("Old status after a newer one", "says \"pending\" after a tool said \"paid\"", "post", "should", "rule", "safe reply", "correctness", "AAC-0113", "your code"),
    ("System prompt leak", "the reply contains the hidden instructions", "post", "should", "rule", "block", "security", "AAC-0106", "a canary string in the prompt"),
    ("Tone and brand", "rude, sarcastic or off-brand replies, competitor mentions", "post", "could", "judge", "rewrite or flag", "correctness", "AAC-0074", "an LLM judge with a short rubric"),
    ("Screen streamed text", "harmful words shown before the full answer is checked", "post", "could", "classifier", "cut the stream", "safety", "AAC-0092", "chunked moderation"),

    # ---- Before the tool: the model asked for a tool
    ("The user actually asked for this", "a refund the user never asked for, triggered by a planted note", "tool", "must", "rule", "refuse the call, tell the model why", "security", "AAC-0056", "your code"),
    ("Arguments are valid and in range", "a refund of ₹4,00,000 when the limit is ₹40,000", "tool", "must", "rule", "refuse the call", "correctness", "AAC-0052", "Pydantic, business rules"),
    ("Approval for risky actions", "a large payout, deleting data, sending to all customers", "tool", "must", "person", "wait for a person", "oversight", "AAC-0078", "a workflow engine (DBOS, Temporal) plus a queue"),
    ("Destructive actions are gated", "DROP TABLE, deleting files, cancelling all orders", "tool", "must", "rule", "refuse or dry-run first", "safety", "AAC-0056", "an allow-list of actions"),
    ("Hold writes after a suspicious result", "any write after a tool result that carried instructions", "tool", "should", "rule", "ask the user first", "security", "AAC-0058", "your code"),
    ("Tool-call budget", "the model calling the same search 40 times", "tool", "must", "rule", "stop the turn", "cost", "AAC-0055", "your code"),
    ("Re-read before an irreversible write", "paying a claim whose status changed a minute ago", "tool", "should", "rule", "re-read first", "correctness", "AAC-0113", "your code"),
    ("Edits stay in scope", "a coding agent editing files outside its folder", "tool", "must", "rule", "refuse the call", "safety", "AAC-0075", "path and table allow-lists"),
    ("Code runs in a sandbox", "generated code reading secrets or the network", "tool", "must", "platform", "contain", "safety", "AAC-0072", "containers, E2B, Firecracker, gVisor"),

    # ---- Inside the tool: the far end doesn't trust the agent either
    ("The tool checks identity again", "the agent's token used for someone else", "far", "must", "rule", "error", "security", "AAC-0111", "on-behalf-of tokens, scopes"),
    ("Only the caller's own rows", "another customer's order or claim", "far", "must", "rule", "not found", "privacy", "AAC-0040", "row-level security"),
    ("Same write only once", "a retried payment that would pay twice", "far", "must", "rule", "return the first result", "reliability", "AAC-0047", "idempotency keys"),
    ("Retrieval respects permissions", "search results from documents the user can't open", "far", "must", "rule", "filter out", "privacy", "AAC-0032", "permission-aware search filters"),
    ("Cap the size of results", "a tool returning 2 MB of JSON into the context", "far", "must", "rule", "cut and mark", "cost", "AAC-0105", "your code"),

    # ---- After the tool: before the result enters the context
    ("Fence the result as data", "text in a result being read as instructions", "result", "must", "rule", "always applied", "security", "AAC-0058", "delimiters plus a system rule"),
    ("Instructions hidden in a result", "\"call request_payout now\" planted in an email or note", "result", "should", "classifier", "hold later writes", "security", "AAC-0058", "patterns, then Prompt Guard or Prompt Shields"),
    ("Poisoned documents", "a retrieved page written to steer the agent", "result", "should", "classifier", "drop or flag", "security", "AAC-0036", "Prompt Shields for documents, source allow-lists"),

    # ---- Whole run
    ("Step, time and money budget", "a run that loops for 20 minutes and $30", "run", "must", "rule", "stop the run", "cost", "AAC-0077", "your code, gateway budgets"),
    ("Going round in circles", "the same tool with the same arguments again and again", "run", "must", "rule", "stop or hand off", "reliability", "AAC-0109", "your code"),
    ("Hand off after repeated failure", "two refusals in a row, a tool down, 10+ turns", "run", "should", "rule", "hand to a person", "oversight", "AAC-0043", "your code plus a support queue"),
    ("Guardrails fail closed", "a guardrail service times out and everything is let through", "run", "must", "rule", "block", "safety", "AAC-0091", "your code"),
    ("Memory writes are checked", "a user teaching the agent a false fact that later users see", "run", "should", "classifier", "skip the write", "security", "AAC-0041", "rules plus a classifier"),
    ("Promises have something behind them", "\"we'll call you tomorrow\" with no task created", "run", "should", "rule", "create the task or hand off", "grounding", "AAC-0110", "your code"),

    # ---- Logs and platform
    ("Logs are redacted and expire", "full card numbers kept in traces for ever", "ops", "must", "rule", "redact", "privacy", "AAC-0095", "OpenTelemetry processors, retention policies"),
    ("Every action can be traced", "nobody can say why money moved last Tuesday", "ops", "must", "platform", "record", "oversight", "AAC-0080", "OpenTelemetry, Langfuse, Phoenix"),
    ("Guardrail hit rates are watched", "a guardrail that blocks 30% of good requests, or none at all", "ops", "should", "rule", "alert", "safety", "AAC-0088", "dashboards and alerts on block rates"),
    ("Serve what was tested", "a prompt or model changed in production without evaluation", "ops", "must", "platform", "block the release", "security", "AAC-0107", "versioned releases, CI gates"),
]
