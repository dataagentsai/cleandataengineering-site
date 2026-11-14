"""Bridge tables, shown on /learn/gold-data-modelling/#bridge. Tested on Spark 3.5.1.

A fact row that belongs to SEVERAL members of a dimension (two sales reps on one order line) cannot carry one key.
It carries a group key; the bridge lists the group's members with a weight that adds up to 1.
"""
from pyspark.sql import DataFrame, functions as F


def naive_join(fact: DataFrame, credits: DataFrame) -> DataFrame:
    """The mistake: join every rep straight onto the fact. One line becomes two rows; revenue doubles."""
    return fact.join(credits, "line_id")


def weights_ok(bridge: DataFrame, group: str) -> DataFrame:
    """Groups whose weights do not add up to 1 (checked every run)."""
    return bridge.groupBy(group).agg(F.round(F.sum("weight"), 6).alias("total")).where("total != 1")


def allocate(fact: DataFrame, bridge: DataFrame, group: str, measure: str) -> DataFrame:
    """Share the measure out by weight: totals stay right."""
    return (fact.join(bridge, group)
                .withColumn(f"{measure}_allocated", F.col(measure) * F.col("weight")))


def rollup_hierarchy(fact: DataFrame, h_bridge: DataFrame, member: str, measure: str) -> DataFrame:
    """Hierarchy bridge: one row per (ancestor, descendant). Sum everything under each person in one join."""
    return (fact.join(h_bridge, fact[member] == h_bridge["descendant"])
                .groupBy("ancestor").agg(F.sum(measure).alias(f"{measure}_under")))
