# The OTIF fact in dbt (shown on /learn/silver-to-gold/, Part D)

Run 2026-11-14 with dbt-core 1.12.7 + dbt-duckdb 1.11.1 (Python 3.12):

    python run_dbt.py /path/to/dbt     # three nights from ../data.py; compares gold with ../results.json

- macros/otif_rule.sql   PROCESSOR: the OTIF rule as a macro (same SQL as ../fact_otif.sql)
- models/fact_otif.sql   READER (bookmark kept in the fact itself) + keys + completeness; WRITER = delete+insert by promised_date
- models/schema.yml      data tests (run AFTER the write) and a table-driven unit test (runs before, on fixed rows)
- models/fact_otif_careless.sql   a careless join, to show that dbt writes the table before its tests fail
