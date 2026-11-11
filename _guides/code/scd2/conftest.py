import os, sys, pytest
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ.pop("SPARK_HOME", None)

@pytest.fixture(scope="session")
def spark():
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession
    b = (SparkSession.builder.master("local[2]").appName("scd2-test")
         .config("spark.sql.shuffle.partitions", "2")
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.ui.enabled", "false"))
    s = configure_spark_with_delta_pip(b).getOrCreate()
    yield s
    s.stop()
