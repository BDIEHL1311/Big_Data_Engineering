from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Spark-Session starten
spark = SparkSession.builder \
    .appName("SSH-Honeypot-Analytics") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

# Schema für JSON aus Kafka definieren
schema = StructType([
    StructField("timestamp", LongType(), True),
    StructField("datetime", StringType(), True),
    StructField("ip", StringType(), True),
    StructField("country", StringType(), True),
    StructField("username", StringType(), True),
    StructField("password", StringType(), True),
    StructField("success", BooleanType(), True)
])

# Kafka-Stream lesen
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "ssh-logs") \
    .option("startingOffsets", "latest") \
    .load()

# JSON parsen und Datetime zu Timestamp konvertieren
parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*") \
.withColumn("event_time", to_timestamp(col("datetime"), "yyyy-MM-dd HH:mm:ss"))

# Watermark für Nachzügler hinzufügen
df_watermark = parsed_df.withWatermark("event_time", "5 minutes")

# Auswertungen
# 1. Zugriffsversuche pro Land (5-Minuten-Fenster)
country_counts = df_watermark \
    .groupBy(
        window("event_time", "5 minutes"),
        "country"
    ) \
    .count() \
    .select(
        col("window.start").alias("window_start"),
        col("country"),
        col("count")
    )

# 2. Erfolgreiche Logins pro IP
successful_logins = df_watermark \
    .filter(col("success") == True) \
    .groupBy("ip") \
    .count() \
    .select(
        col("ip"),
        col("count").alias("successful_attempts")
    )

# 3. Top Passwörter
password_counts = df_watermark \
    .groupBy("password") \
    .count() \
    .orderBy(desc("count")) \
    .select(
        col("password"),
        col("count").alias("attempts")
    )

# Funktion zum Speichern in MariaDB
def save_to_mariadb(df, epoch_id, table_name):
    try:
        df.write \
            .format("jdbc") \
            .option("url", "jdbc:mysql://mariadb:3306/honeypot") \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .option("dbtable", table_name) \
            .option("user", "root") \
            .option("password", "password") \
            .mode("overwrite") \
            .save()
        print(f"Successfully saved data to {table_name}")
    except Exception as e:
        print(f"Error saving to {table_name}: {str(e)}")

# Streaming queries mit Error Handling
try:
    country_query = country_counts.writeStream \
        .foreachBatch(lambda df, epoch_id: save_to_mariadb(df, epoch_id, "country_stats")) \
        .outputMode("update") \
        .start()

    logins_query = successful_logins.writeStream \
        .foreachBatch(lambda df, epoch_id: save_to_mariadb(df, epoch_id, "login_stats")) \
        .outputMode("update") \
        .start()

    password_query = password_counts.writeStream \
        .foreachBatch(lambda df, epoch_id: save_to_mariadb(df, epoch_id, "password_stats")) \
        .outputMode("complete") \
        .start()

    # Warten auf Beendigung
    spark.streams.awaitAnyTermination()
    
except Exception as e:
    print(f"Error in stream processing: {str(e)}")
    raise e