# SCD Type 2 writer (shown on /learn/scd2-auto-cdc-vs-pyspark/)

Run 2026-11-11 on Spark 3.5.1 + Delta 3.2.0 (Python 3.9):

    unset SPARK_HOME
    python -m pytest -q test_scd2.py   # 11 table-driven cases
    python e2e.py                      # CDC stream, replay, 3 snapshots + re-run, change data feed

The page generator reads these files, so the page always shows the code that was run.
