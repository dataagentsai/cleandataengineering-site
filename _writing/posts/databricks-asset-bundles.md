---
title: CI/CD for Databricks with Asset Bundles
date: 2026-10-31
subject: data
audience: builders
kind: explainer
draft: false
summary: Most Databricks jobs in production were clicked together in the workspace UI, so nobody can say what changed or rebuild them in another workspace. Databricks Asset Bundles put jobs, pipelines and their settings in one project folder, next to the code, and deploy the same folder to dev, test and prod. Add a pipeline that validates every pull request and deploys on merge as a service principal, and releases stop being a nervous afternoon.
linkedin: If your production Databricks jobs were clicked together in the UI, you can't review them, roll them back or rebuild them. Asset Bundles fix that with one folder and one YAML file. Here is the whole idea, drawn simply, from a developer's own copy to a deploy on merge.
deeper: /concepts/ci-cd/
deeper_label: CI/CD, the idea behind it
---

On Monday morning the nightly orders job in production fails. Someone changed its cluster last week. Who? From what? Nobody knows, because the job was built by clicking through the workspace UI, and the UI has no pull request.

Most teams start this way. The code lives in Git, but the job that runs the code, its schedule, its cluster and its parameters live only in the workspace. Building the same job in a test workspace means clicking it together again, slightly differently.

Databricks Asset Bundles fix this. This post explains them in plain words, then shows a simple pipeline that tests and deploys them for you.

## The idea: pack once, carry everywhere

A bundle is a project folder that describes your Databricks resources as code. Resources are the things you would otherwise create by hand: jobs, pipelines, and a few other kinds.

{{drawing: dab-suitcase}}

You pack the suitcase once. It holds your code and a YAML file that says which jobs to create, on what compute, on what schedule. Then you carry the same suitcase to three hotels: a dev workspace, a test workspace and a production workspace. Each hotel is called a **target**. The contents don't change between hotels. Only a few settings do, such as which workspace to use and which catalog to write to.

Because the whole thing is text in Git, every change to a job is a reviewed pull request. You can see who changed the cluster, and you can roll it back.

## One folder

{{drawing: dab-folder}}

You can start a new bundle with `databricks bundle init`, which asks a few questions and creates a project from a template. Use the current Databricks CLI for this; the old Python package called databricks-cli does not have bundles. Most bundles end up looking like the picture:

- **`databricks.yml`** at the top. It names the bundle, lists the variables and defines the targets.
- **`resources/`** holds one YAML file per job or pipeline. `databricks.yml` includes them, so the main file stays short.
- **`src/`** holds the notebooks and Python files the jobs run.
- **`tests/`** holds the unit tests for your transformation code.

Here is a short sketch, not a complete file. The hosts, names and cluster settings are made up for the example.

```
# databricks.yml  (a sketch)
bundle:
  name: sales_pipelines

include:
  - resources/*.yml

variables:
  catalog:
    description: The catalog this bundle writes to
    default: sales_dev

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://dev-workspace.example.com

  test:
    workspace:
      host: https://test-workspace.example.com
    variables:
      catalog: sales_test

  prod:
    mode: production
    workspace:
      host: https://prod-workspace.example.com
    run_as:
      service_principal_name: <application id of the prod service principal>
    variables:
      catalog: sales_prod
```

And one job in `resources/daily_orders.yml`, also a sketch:

```
resources:
  jobs:
    daily_orders:
      name: daily_orders
      schedule:
        quartz_cron_expression: "0 0 2 * * ?"
        timezone_id: Asia/Kolkata
      job_clusters:
        - job_cluster_key: main
          new_cluster:
            policy_id: ${var.job_policy_id}
            spark_version: 15.4.x-scala2.12
            num_workers: 2
      tasks:
        - task_key: load_orders
          job_cluster_key: main
          notebook_task:
            notebook_path: ../src/load_orders.py
            base_parameters:
              catalog: ${var.catalog}
```

Two things are worth noticing. `${var.catalog}` means the same job writes to `sales_dev`, `sales_test` or `sales_prod` depending on the target. And the job runs on **job compute** with a **cluster policy**, a set of rules that limits what a cluster may look like, written into the definition. That is exactly where the cheapest fixes from our [Databricks cost leaks note](/writing/databricks-cost-leaks/) belong: once they are in the bundle, every deploy keeps them, and nobody can quietly switch the job to an always-on interactive cluster. (A `job_policy_id` variable would also need declaring under `variables`; the sketch leaves it out.)

## Four commands

You only need a handful of commands, all run from the bundle folder.

1. **`databricks bundle validate`** reads the YAML, fills in the variables for the chosen target and reports mistakes. It changes nothing.
2. **`databricks bundle deploy`** uploads the code and creates or updates the jobs and pipelines in the target's workspace. Run it again and it updates what is there, rather than making a second copy.
3. **`databricks bundle run daily_orders`** starts one job or pipeline from the bundle and waits for it to finish.
4. **`databricks bundle destroy`** removes everything that bundle deployed to a target. Handy for cleaning up a dev copy; think twice before pointing it at prod.

You pick the target with `-t`, as in `databricks bundle deploy -t test`. With no target, the one marked `default: true` is used, which in the sketch is dev.

## Dev mode: everyone gets their own copy

The `mode: development` setting on the dev target is what makes a shared dev workspace bearable.

{{drawing: dab-dev-mode}}

When Priya deploys in development mode, every job gets her name in front, like `[dev priya] daily_orders`, and the files go into her own folder in the workspace. Arjun's deploy makes `[dev arjun] daily_orders`. They can both change the same job on the same day without breaking each other. Schedules on these copies are paused, so twenty developer copies don't all run at 2 a.m.

The prod target uses `mode: production`. No prefix, schedules run as written, and the bundle applies a few extra safety checks before it will deploy. Pair it with `run_as`, so the jobs run as a service principal and not as whoever happened to deploy.

## The pipeline

A **service principal** is an identity for a machine rather than a person. Your CI system logs in as one. It has exactly the rights it needs in each workspace, and it doesn't leave the company when someone resigns.

{{drawing: dab-pipeline}}

Here is the shape, using GitHub Actions as the example. Azure DevOps or GitLab work the same way.

1. **On every pull request**, install the Databricks CLI, run `databricks bundle validate -t test`, then run the unit tests. If either fails, the pull request can't merge.
2. **On merge to main**, log in as the test service principal and run `databricks bundle deploy -t test`.
3. **Run a small integration test** with `databricks bundle run -t test daily_orders`, against a small, fixed sample of data, and check the output table.
4. **Wait for approval.** In GitHub Actions, a protected environment can require a named person to approve before the next job starts.
5. **Deploy to prod** as the prod service principal with `databricks bundle deploy -t prod`. Same commit, same bundle.

The service principal's credentials live in the CI system's secret store, never in the repository. The Databricks CLI reads them from environment variables, such as the workspace host plus the service principal's client ID and secret, so nothing sensitive ever appears in the YAML.

## Tests: two kinds, both small

**Unit tests** check your transformation code. Keep the logic in plain Python functions in `src/` that take a DataFrame and return a DataFrame. Then a test can build three rows, call the function and check the answer, using `pytest` and a local Spark session. These run on the CI machine in a minute and need no workspace. A test might say: an order with a refund of ₹40,000 must show net revenue of zero.

**The integration run** checks that everything fits together in a real workspace: the job deploys, the cluster starts, the permissions work and the table gets written. Keep it to one or two jobs on a small sample. It is a smoke test, not a full reload.

If you use a metadata-driven ingestion framework, the same idea applies twice: the engine gets unit tests, and the config rows get validated in the pull request. Our [metadata-driven ingestion post](/writing/metadata-driven-ingestion/) shows that setup, and a bundle is a natural way to deploy the engine job.

## Mistakes we see

1. **Clicking jobs together in the prod UI.** Even one hand-made job means prod no longer matches Git. Make prod read-only for people, and let only the service principal deploy.
2. **A personal token in CI.** It works until that person goes on leave or leaves the company, and meanwhile every deploy runs with their rights. Use a service principal per environment.
3. **One target for everything.** Without separate targets, "test" means "prod with fingers crossed". Use at least dev and prod; test is worth adding as soon as more than one person deploys.
4. **No tests before deploy.** `validate` catches broken YAML, not broken logic. A five-line unit test catches the bug that would otherwise reach the Monday report.
5. **Secrets in the YAML.** Anything in `databricks.yml` is in Git history forever. Keep passwords and keys in a Databricks secret scope or your cloud's key vault, and refer to them by name.

## Questions to check your own setup

1. Could you rebuild every production job in a new workspace from Git alone?
2. Who, or what, ran the last deploy to prod?
3. Can two developers change the same job on the same day without breaking each other?
4. Does a pull request run validate and unit tests before anyone can merge it?
5. Is there a password, token or key anywhere in your repository?
6. Do your jobs run on job compute with a cluster policy, written in the bundle?

If prod still has jobs that exist only in the UI, start by moving one of them into a bundle. Once every change is a reviewed pull request, a broken job on Monday morning becomes a question you can answer.
