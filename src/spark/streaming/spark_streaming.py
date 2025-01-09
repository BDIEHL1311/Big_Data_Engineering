from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from config.base_config import BaseConfig, setup_logging
import time

logger = setup_logging('spark-streaming')
config = BaseConfig()

# Schema für JSON aus Kafka
HONEYPOT_SCHEMA = StructType([
    StructField("timestamp", LongType(), True),
    StructField("datetime", StringType(), True),
    StructField("ip", StringType(), True),
    StructField("country", StringType(), True),
    StructField("username", StringType(), True),
    StructField("password", StringType(), True),
    StructField("success", BooleanType(), True)
])

def create_spark_session():
    spark = SparkSession.builder \
        .appName("SSH-Honeypot-Analytics") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel('WARN')
    return spark

def read_from_kafka(spark):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", config.KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", config.KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

def parse_kafka_messages(kafka_df):
    return kafka_df.select(
        from_json(
            col("value").cast("string"),
            HONEYPOT_SCHEMA
        ).alias("json")
    ).select(
        to_timestamp(col("json.datetime"), "yyyy-MM-dd HH:mm:ss").alias("event_time"),
        col("json.*")
    ).withWatermark("event_time", config.SPARK_WINDOW_DURATION)

def calculate_metrics(parsed_df):
    # 1. Zugriffsversuche pro Land
    country_stats = parsed_df.groupBy(
        window(col("event_time"), 
               config.SPARK_WINDOW_DURATION, 
               config.SPARK_SLIDING_DURATION),
        col("country")
    ).agg(
        count("*").alias("count"),
        sum(when(col("success"), 1).otherwise(0)).alias("successful_attempts")
    )
    
    # 2. Erfolgreiche Logins pro IP
    login_stats = parsed_df.filter(col("success") == True) \
        .groupBy("ip") \
        .agg(
            count("*").alias("successful_attempts"),
            max("event_time").alias("last_updated")
        )
    
    # 3. Passwort-Statistiken
    password_stats = parsed_df.groupBy("password") \
        .agg(
            count("*").alias("attempts"),
            sum(when(col("success"), 1).otherwise(0)).alias("successful_attempts"),
            max("event_time").alias("last_updated")
        )
    
    return country_stats, login_stats, password_stats

def save_to_database(df, epoch_id, table_name):
    start_time = time.time()
    logger.info(f"Saving batch {epoch_id} to table {table_name}")
    
    try:
        # Spezielle Behandlung für country_stats wegen Window
        if table_name == "country_stats":
            df = df.select(
                col("window.start").alias("window_start"),
                col("country"),
                col("count"),
                col("successful_attempts")
            )
        
        df.write \
            .jdbc(
                url=config.mariadb_url,
                table=table_name,
                mode="append",
                properties=config.db_properties
            )
        
        duration = time.time() - start_time
        logger.info(f"Successfully saved batch {epoch_id}", 
                   extra={'duration': duration, 'table': table_name})
        
    except Exception as e:
        logger.error(f"Error saving batch {epoch_id}", 
                    extra={'error': str(e), 'table': table_name})
        raise e

def main():
    spark = create_spark_session()
    logger.info("Starting Spark Streaming Pipeline")
    
    try:
        kafka_df = read_from_kafka(spark)
        parsed_df = parse_kafka_messages(kafka_df)
        country_stats, login_stats, password_stats = calculate_metrics(parsed_df)
        
        # Debug Output
        console_query = parsed_df.writeStream \
            .outputMode("append") \
            .format("console") \
            .start()
        
        # In Datenbank schreiben
        country_query = country_stats.writeStream \
            .outputMode("update") \
            .foreachBatch(lambda df, epoch_id: save_to_database(df, epoch_id, "country_stats")) \
            .option("checkpointLocation", f"{config.SPARK_CHECKPOINT_DIR}/country_stats") \
            .start()
            
        login_query = login_stats.writeStream \
            .outputMode("update") \
            .foreachBatch(lambda df, epoch_id: save_to_database(df, epoch_id, "login_stats")) \
            .option("checkpointLocation", f"{config.SPARK_CHECKPOINT_DIR}/login_stats") \
            .start()
            
        password_query = password_stats.writeStream \
            .outputMode("update") \
            .foreachBatch(lambda df, epoch_id: save_to_database(df, epoch_id, "password_stats")) \
            .option("checkpointLocation", f"{config.SPARK_CHECKPOINT_DIR}/password_stats") \
            .start()
        
        spark.streams.awaitAnyTermination()
        
    except Exception as e:
        logger.error("Error in stream processing", extra={'error': str(e)})
        raise e

if __name__ == "__main__":
    main()