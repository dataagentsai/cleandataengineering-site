"""Week 1 skeleton: a keyless call to a model in a Foundry project.

Setup (once):
    python -m venv .venv && source .venv/bin/activate
    pip install "azure-ai-projects>=2.3" azure-identity openai
    az login
    export PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
    export MODEL_DEPLOYMENT="gpt-5-mini"

Run:
    python main.py
"""
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

NOTE = (
    "Policyholder reports rear-end collision on 6 Oct at a traffic light in Pune. "
    "No injuries. Bumper and tail light damaged. Photos uploaded. Third party admitted fault."
)


def main() -> None:
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),  # keyless: uses your az login or a managed identity
    )
    client = project.get_openai_client()
    response = client.responses.create(
        model=os.environ.get("MODEL_DEPLOYMENT", "gpt-5-mini"),
        input=f"Summarise this claim note in two lines for a claims handler:\n{NOTE}",
        max_output_tokens=300,
    )
    print(response.output_text)
    print(f"\n[tokens] input={response.usage.input_tokens} output={response.usage.output_tokens}")


if __name__ == "__main__":
    main()
