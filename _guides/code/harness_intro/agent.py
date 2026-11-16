"""Do the same job with an agent. The model decides the next step; our code runs it and goes round again."""

import json

from world import create_claim, get_policy

MAX_STEPS = 5
SYSTEM = "You are a claims assistant for an insurance company. Use the tools. Answer briefly."
TOOLS = {"get_policy": get_policy, "create_claim": create_claim}  # what the agent is able to do


def run(task, call_model, log=print):
    messages = [{"role": "user", "content": task}]
    for step in range(1, MAX_STEPS + 1):
        reply = call_model(SYSTEM, list(TOOLS), messages)  # 1. ask the model what to do next
        messages.append({"role": "assistant", "content": reply["content"]})
        if reply["stop_reason"] != "tool_use":  # 2. no tool asked for: that is the answer
            return reply["content"][0]["text"]
        results = []
        for block in reply["content"]:  # 3. run each tool the model asked for
            if block["type"] == "tool_use":
                log(f"step {step}: the model asks for {block['name']}({block['input']})")
                output = TOOLS[block["name"]](**block["input"])
                results.append({"type": "tool_result", "tool_use_id": block["id"], "content": json.dumps(output)})
        messages.append({"role": "user", "content": results})  # 4. show the model the results
    return "I couldn't finish this in time, so I am handing over to a person."  # 5. the limit


if __name__ == "__main__":
    from pretend_model import pretend_model

    print(run("I had a car accident yesterday. My policy is P-1001. Please register my claim.", pretend_model))
    print(run("What does my policy P-1001 cover?", pretend_model))
