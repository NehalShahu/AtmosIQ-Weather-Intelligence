from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, max as spark_max, min as spark_min,
    sum as spark_sum, year, month, date_format, round as spark_round
)

spark = (
    SparkSession.builder
    .appName("AtmosIQ-Weather-Analytics")
    .master("local[2]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

source_path = "hdfs://localhost:9000/atmosiq/raw/weather/nagpur_weather.csv"

weather = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(source_path)
    .withColumn("time", col("time").cast("date"))
)

print("\n===== ATMOSIQ DATASET SUMMARY =====")
print("Total records:", weather.count())
weather.printSchema()

print("\n===== MONTHLY TEMPERATURE SUMMARY =====")
monthly = (
    weather
    .withColumn("year", year("time"))
    .withColumn("month", month("time"))
    .groupBy("year", "month")
    .agg(
        spark_round(avg("temperature_2m_mean"), 2).alias("avg_temp_c"),
        spark_round(spark_max("temperature_2m_max"), 2).alias("max_temp_c"),
        spark_round(spark_min("temperature_2m_min"), 2).alias("min_temp_c"),
        spark_round(spark_sum("precipitation_sum"), 2).alias("precipitation_mm")
    )
    .orderBy("year", "month")
)

monthly.show(24, truncate=False)

print("\n===== HOTTEST DAYS =====")
weather.orderBy(col("temperature_2m_max").desc()).select(
    "time", "temperature_2m_max", "temperature_2m_mean"
).show(10, truncate=False)

print("\n===== COLDEST DAYS =====")
weather.orderBy(col("temperature_2m_min").asc()).select(
    "time", "temperature_2m_min", "temperature_2m_mean"
).show(10, truncate=False)

print("\n===== YEARLY SUMMARY =====")
yearly = (
    weather
    .withColumn("year", year("time"))
    .groupBy("year")
    .agg(
        spark_round(avg("temperature_2m_mean"), 2).alias("avg_temp_c"),
        spark_round(spark_max("temperature_2m_max"), 2).alias("hottest_temp_c"),
        spark_round(spark_min("temperature_2m_min"), 2).alias("coldest_temp_c"),
        spark_round(spark_sum("precipitation_sum"), 2).alias("total_precipitation_mm")
    )
    .orderBy("year")
)

yearly.show(truncate=False)

monthly_output = "/atmosiq/processed/weather/monthly_summary"
yearly_output = "/atmosiq/processed/weather/yearly_summary"

monthly.write.mode("overwrite").option("header", True).csv(
    "hdfs://localhost:9000" + monthly_output
)
yearly.write.mode("overwrite").option("header", True).csv(
    "hdfs://localhost:9000" + yearly_output
)

print("\nSaved monthly summary to:", monthly_output)
print("Saved yearly summary to:", yearly_output)
print("AtmosIQ analytics completed successfully.")

spark.stop()
