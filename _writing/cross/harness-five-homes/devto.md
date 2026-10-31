---
title: One harness, five homes: the agent harness on Azure, GCP, AWS, Databricks and open source
published: false
canonical_url: https://cleandataengineering.ai/writing/harness-five-homes/
description: An agent harness has the same jobs on every platform: a model door, a loop, tools, state, durable waits, identity, guardrails, tracing, evals and hosting. Azure, Google Cloud, AWS, Databricks and open source fill those jobs with different products. Design the harness once, then pick the home by where your data and identity already live and which managed pieces your team trusts.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/harness-five-homes/).*


"Which cloud should our agent run on?" It is often the first question in the first meeting, before anyone has written down what the agent must do. The team picks a platform, learns its agent product, and builds the agent in that product's shape.

There is a better order. An agent harness is the ordinary software around the model that decides what it sees, what it may touch, and what happens when it gets something wrong. It has the same jobs wherever it runs. Design those jobs first. The platform then decides only which product fills each one.

This post puts ten of those jobs side by side on Azure, Google Cloud, AWS, Databricks and open source. The product names are as of October 2026, and they change often. The jobs don't.

## One floor plan, five houses

Think of the harness as a floor plan. It says there is a front door, a kitchen and a lock, and how the rooms connect. It does not say brick or timber.

{{drawing: home-floorplan}}

Each platform is a different building material. Azure gives you one set of products, AWS another, Databricks a third. You can also build it yourself from open-source parts, which is cheap in money and expensive in your own time.

As in [the agent tech stack](/writing/agent-tech-stack/), we call each job a **concept** and the thing doing it a **product**. Write the design in concepts. Products should appear in exactly one place: a short list of which product fills each job. We call that list the **bindings**.

## The ten jobs, side by side

Most of the jobs are familiar. Three need a word first:

- **Durable workflows** let a step wait hours or days for a person, survive a restart, and never pay the same claim twice.
- **Guardrails** check what may go in, come out and run, before and after each step.
- **Hosting** is where the harness code itself runs and answers requests.

| Concern | Azure | Google Cloud | AWS | Databricks | Open source |
|---|---|---|---|---|---|
| Model access and gateway | APIM AI gateway | Gemini, Apigee | Bedrock, API Gateway | Mosaic AI Gateway | LiteLLM |
| Loop or agent service | Foundry Agent Service | Vertex AI Agent Engine | AgentCore Runtime | Mosaic AI Agent Framework | your own loop |
| Tools | Foundry tools, APIM MCP | ADK tools | AgentCore Gateway | Unity Catalog functions | MCP SDKs, FastMCP |
| State | Azure PostgreSQL, Cosmos DB | Cloud SQL, Firestore | RDS Postgres, DynamoDB | Lakebase (Postgres) | PostgreSQL |
| Durable workflows | Durable Task Scheduler | Workflows | Step Functions | bring your own | DBOS, Temporal |
| Identity | Entra ID | IAM, Identity Platform | IAM, Cognito | Unity Catalog grants | Keycloak |
| Guardrails | AI Content Safety | Model Armor | Bedrock Guardrails | AI Gateway guardrails | your own rules |
| Tracing | Application Insights | Cloud Trace | CloudWatch, X-Ray | MLflow tracing | OpenTelemetry, Langfuse |
| Evals | Foundry evaluation | Vertex Gen AI evaluation | Bedrock evaluations | MLflow evaluation | promptfoo, DeepEval |
| Hosting | Container Apps | Cloud Run | ECS Fargate | Databricks Apps | Docker |

The cells are examples from our own concept maps, not a ranking or a full list. "Bring your own" means our sources name no Databricks product for that job, so you add one, such as DBOS or Temporal.

## Concept versus product

Take one row and look at it closely.

{{drawing: home-badges}}

The job card says: wait days for a person, survive a restart, never pay twice. Five platforms put five different badges on it. The card doesn't change.

Here is a real case. Our motor-claims agent is built for Azure. For durable waits its bindings do not pick Durable Task Scheduler. They pick DBOS, a library that keeps its workflow state in the PostgreSQL database the agent already has, so there is no new server to run. When we later wrote the same agent's bindings for AWS, we chose DBOS again over Step Functions, because Step Functions would move the waits out of our code and into an AWS-only service. That AWS file is still on paper; nothing is deployed there yet.

DBOS may not be right for you. The point is that the choice is one line in a binding file, and the agent's code doesn't know which line was picked. The patterns that make this possible, ports and adapters, are in [swap anything, break nothing](/writing/harness-design-patterns/).

Notice also that the Azure binding is not "all Azure". It uses Azure for the gateway, identity, secrets and tracing, and keeps open-source parts like DBOS and pgvector where they keep a later move cheap. Mixing is normal.

## Where each home is strong, and where it is thin

- **Azure.** Strong if your staff already sign in with Entra ID. API Management gives one governed door to every model, with token limits and token metrics at the gateway. Thin spot: features differ by tier. In our development setup the cheapest API Management tier had no token-limit policy, so we checked the tier before the design depended on it.
- **Google Cloud.** Gemini on Vertex AI, the Agent Development Kit (ADK) as a loop library, Vertex AI Agent Engine to host it, Model Armor for screening and Cloud Run for hosting. We have not built an agent here ourselves, so we describe it only from our maps. Apigee is a general API gateway; check what it does for model traffic before you rely on it.
- **AWS.** Bedrock for models and guardrails. AgentCore is a bundle of harness parts: a runtime, memory, identity, a gateway and observability. Thin spot: when we read the AgentCore Gateway documentation for our AWS bindings, its token limits had only a one-minute window and failed open by default. So a limit there is a cost guard, not a security boundary, and our own per-task cost meter stays the hard ceiling.
- **Databricks.** Strong when the data the agent reads already sits in Unity Catalog. Grants, functions used as tools, MLflow tracing and evaluation, the AI Gateway and Lakebase for state all live next to that data. Thin spot: no durable-wait product in our sources, so plan to bring one.
- **Open source.** Every row has a product, and all of it runs on a laptop. Our reference agent runs on LiteLLM, PostgreSQL, Temporal, Keycloak, and OpenTelemetry with Langfuse. Thin spot: you run all of it, including upgrades, backups and being woken at night.

Some of these rows have settled across the industry and some are still moving. [Building agents on a moving ship](/writing/moving-ship/) sorts which is which.

## How to pick

Answer three questions before anyone names a product.

{{drawing: home-pick}}

1. **Where is your data?** The agent reads it on almost every turn. Moving the agent to the data is easier than moving the data to the agent, and the data's permissions come with it.
2. **Where is your identity?** The agent acts on someone's behalf, so it must know who is asking and what they may do. If your staff and customers already sign in on one platform, building there saves a whole project.
3. **What will your team run?** Decide which managed pieces you trust and which you would rather run yourself. Managed means someone else patches it. It also means their limits, their tiers and their roadmap.

The answers don't have to point to one home. Databricks runs on any of the three clouds, so a common answer is data in Databricks, identity in Entra ID and hosting on Azure. Say, a lending team in Pune whose loan files live in Unity Catalog and whose staff sign in with Entra ID would fill most rows from those two, and bring the rest.

## Is a managed agent service enough?

Every platform now has one: Foundry Agent Service, Vertex AI Agent Engine, AgentCore and the Mosaic AI Agent Framework. They are useful, and each fills several rows at once.

{{drawing: home-umbrella}}

Hold the one you like against the ten rows and mark what it covers. Some rows usually stay out in the rain: the checks that sit right before a tool moves money, evals on your own cases, and cost per finished piece of business work. Also ask who owns the loop. If the service owns it, you may not be able to place a check exactly before a tool runs. In both our Azure and AWS bindings we kept the loop in our own code, so the step budget and the cost ceiling stay visible.

## Mistakes we see often

1. **Choosing the platform first and the design second.** The agent ends up shaped like one product, and the empty rows show up in production. Write the ten jobs first, then shop.
2. **Assuming a managed agent service covers every concern.** One product name is not ten jobs. Mark the rows it fills and give the rest an owner.
3. **Rewriting the agent for each cloud.** If product names sit inside your business logic, every move is a rewrite. Put each product behind a small interface, so a move means new adapters, a new binding file and the same tests passing.
4. **Assuming a feature exists in every tier and region.** Product pages describe the best tier in the biggest region. Check the tier and region you will actually pay for.

## Six questions to check your own plan

1. Can you describe your harness in ten jobs without naming a single product?
2. Is there one file that says which product fills each job?
3. Where does the data your agent reads live, and where do its users sign in?
4. For your managed agent service, which rows does it fill, and who owns the rest?
5. If you had to move to another home next year, how many files would change?
6. Which row is "bring your own" on your platform, and who is building it?

Draw the floor plan once; brick, timber or glass is a choice you can make later, and change.

