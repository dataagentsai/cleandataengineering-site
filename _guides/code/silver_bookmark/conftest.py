import os
import sys

import pytest

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ.pop("SPARK_HOME", None)


def make_spark(name="silver-to-gold"):
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession
    b = (SparkSession.builder.master("local[2]").appName(name)
         .config("spark.sql.shuffle.partitions", "2")
         .config("spark.sql.session.timeZone", "UTC")
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.ui.enabled", "false"))
    return configure_spark_with_delta_pip(b).getOrCreate()


@pytest.fixture(scope="session")
def spark():
    s = make_spark()
    yield s
    s.stop()
