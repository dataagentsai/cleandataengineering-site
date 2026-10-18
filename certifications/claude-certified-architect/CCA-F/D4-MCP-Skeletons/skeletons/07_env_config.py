"""
Skeleton 07 · Env-var-config server — configuration without committed secrets.

PATTERN           The server reads its credentials from the environment. The
                  .mcp.json that launches it references ${TOKEN}, never the value.
WHAT IT EXPOSES   Where the secret actually lives, and the difference between the
                  three MCP config scopes. A token pasted into a project-scoped
                  .mcp.json is a token committed to git — the file's whole purpose
                  is to be shared with the team.
                  Scopes, from narrowest to widest:
                      local    this project, this machine, NOT committed  → secrets ok
                      project  .mcp.json at the repo root, COMMITTED      → never a secret
                      user     all your projects, this machine            → personal tokens
EXAM SHAPE        "The team needs the same MCP server, but each developer has
                  their own API key." → project scope for the wiring, ${VAR}
                  expansion for the value, each developer supplies their own.

Run:  API_TOKEN=demo-token python 07_env_config.py
"""

import os

from fastmcp import FastMCP

mcp = FastMCP("configured-api")

# Read config at import time and FAIL LOUDLY if it is missing. A server that
# starts happily without its token fails later, on a tool call, as a confusing
# error inside the model's transcript instead of a clear one in your terminal.
API_TOKEN = os.environ.get("API_TOKEN")
API_BASE = os.environ.get("API_BASE", "https://api.example.com")   # sane default
TIMEOUT = int(os.environ.get("API_TIMEOUT", "30"))

if not API_TOKEN:
    raise RuntimeError(
        "API_TOKEN is not set. Add it to your MCP client config as "
        '"env": {"API_TOKEN": "${API_TOKEN}"} and export it in your shell.'
    )


@mcp.tool
def whoami() -> dict:
    """Return the identity and configuration this server is running with.

    Useful for confirming the server picked up the right credentials.
    """
    return {
        "base": API_BASE,
        "timeout": TIMEOUT,
        # NEVER return the token. Return proof-of-presence instead: enough to
        # debug "did it load the right key", useless to anyone reading the log.
        "tokenFingerprint": f"{API_TOKEN[:3]}…{API_TOKEN[-2:]} ({len(API_TOKEN)} chars)",
    }


@mcp.tool
def fetch_record(record_id: str) -> dict:
    """Fetch one record from the configured upstream API."""
    # A real implementation: httpx.get(f"{API_BASE}/records/{record_id}",
    #     headers={"Authorization": f"Bearer {API_TOKEN}"}, timeout=TIMEOUT)
    return {"id": record_id, "base": API_BASE, "ok": True}


# -----------------------------------------------------------------------------
# THE .mcp.json THAT LAUNCHES THIS — see mcp.json.example in this directory.
#
#     {
#       "mcpServers": {
#         "configured-api": {
#           "command": "python",
#           "args": ["skeletons/07_env_config.py"],
#           "env": { "API_TOKEN": "${API_TOKEN}",
#                    "API_BASE":  "${API_BASE:-https://api.example.com}" }
#         }
#       }
#     }
#
# ${API_TOKEN}                        → expands from your shell; fails if unset
# ${API_BASE:-https://…}              → expands, with a fallback if unset
#
# The committed file therefore contains the WIRING (which server, which command,
# which variables it needs) and none of the VALUES. Every developer gets working
# config on clone and supplies their own credential.
#
# THREE THINGS THAT GO WRONG
# 1. The token is pasted in literally "just to test it" and reaches git. Rotate
#    it — a secret in git history is a leaked secret even after the fix commit.
# 2. The server inherits your interactive shell's environment — until it does
#    not. A GUI-launched client may not source your ~/.zshrc, so the variable is
#    set in your terminal and empty in the server. The loud startup failure above
#    is what makes that diagnosable in seconds instead of an hour.
# 3. The token is logged. Never print config at startup; the fingerprint above is
#    the safe version of that instinct.
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
