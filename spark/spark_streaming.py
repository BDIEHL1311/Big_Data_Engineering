from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Spark-Session starten
spark = SparkSession.builder \
    .appName("SSH-Honeypot-Analytics") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .config("spark.driver.extraClassPath", "/opt/bitnami/spark/jars/mariadb-java-client-3.3.2.jar") \
    .master("local[*]") \
    .getOrCreate()

print("Spark Session created")

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

print("Starting to read from Kafka...")

# Kafka-Stream lesen
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "ssh-logs") \
    .option("startingOffsets", "earliest") \
    .load()

# JSON parsen und Datetime zu Timestamp konvertieren
parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*") \
.withColumn("event_time", to_timestamp(col("datetime"), "yyyy-MM-dd HH:mm:ss"))

# Debug-Stream zur Konsole
console_query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

print("Console debug stream started")

# Watermark für Nachzügler
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
        col("window.start").alias("start"),  # Spaltenname geändert
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

def save_to_mariadb(df, epoch_id, table_name):
    print(f"\nProcessing batch {epoch_id} for table {table_name}")
    
    count = df.count()
    print(f"Number of records in batch: {count}")
    
    if count == 0:
        print("Batch is empty, skipping...")
        return
        
    print("Data to write:")
    df.show(truncate=False)
    
    try:
        # Tabellenspezifische Anpassungen
        if table_name == "country_stats":
            df = df.select(
                col("start").alias("window_start"),
                col("country"),
                col("count")
            )
            
        print(f"Attempting to write to {table_name}...")
        df.write \
            .format("jdbc") \
            .option("driver", "org.mariadb.jdbc.Driver") \
            .option("url", "jdbc:mariadb://mariadb:3306/honeypot") \
            .option("dbtable", table_name) \
            .option("user", "root") \
            .option("password", "password") \
            .mode("append") \
            .save()
        print(f"Successfully wrote batch to {table_name}")
    except Exception as e:
        print(f"Error writing to {table_name}:", str(e))
        print("DataFrame schema:", df.schema)

print("Starting streaming queries...")

try:
    checkpoint_dir = "/tmp/checkpoints"
    
    print("Starting country stats stream...")
    country_query = country_counts.writeStream \
        .trigger(processingTime='10 seconds') \
        .foreachBatch(lambda df, epoch_id: save_to_mariadb(df, epoch_id, "country_stats")) \
        .outputMode("update") \
        .option("checkpointLocation", f"{checkpoint_dir}/country_stats") \
        .start()

    print("Starting login stats stream...")
    logins_query = successful_logins.writeStream \
        .trigger(processingTime='10 seconds') \
        .foreachBatch(lambda df, epoch_id: save_to_mariadb(df, epoch_id, "login_stats")) \
        .outputMode("update") \
        .option("checkpointLocation", f"{checkpoint_dir}/login_stats") \
        .start()

    print("Starting password stats stream...")
    password_query = password_counts.writeStream \
        .trigger(processingTime='10 seconds') \
        .foreachBatch(lambda df, epoch_id: save_to_mariadb(df, epoch_id, "password_stats")) \
        .outputMode("complete") \
        .option("checkpointLocation", f"{checkpoint_dir}/password_stats") \
        .start()

    print("All streams started, waiting for termination...")
    
    # Warten auf Beendigung
    spark.streams.awaitAnyTermination()
    
except Exception as e:
    print(f"Error in stream processing: {str(e)}")
    raise e