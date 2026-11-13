# Silver to gold: the worked example (shown on /learn/silver-to-gold/)

Run 2026-11-13 on Spark 3.5.1 + Delta 3.2.0 (Python 3.9):

    unset SPARK_HOME
    python -m pytest -q test_builds.py   # 21 table-driven cases: six fact kinds + key lookup
    python e2e.py                        # three nightly runs, a crash and rerun, a careless join stopped,
                                         # the other fact kinds; writes results.json

- builds.py   PROCESSOR: one pure build per fact kind
- harness.py  READER, key lookup, checks and ledger, WRITERS, and run_fact (the same steps for every fact)
- data.py     the tiny tyre company, silver before each run

The page generator reads these files and results.json, so the page shows the code and numbers that were run.
Simplified for teaching: the metadata store is a JSON file, one dimension per fact, one driver input.
