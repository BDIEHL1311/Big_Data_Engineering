from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml import Pipeline
from config.base_config import BaseConfig, setup_logging
import time

logger = setup_logging('feature-engineering')
config = BaseConfig()

def create_spark_session():
    """Erstellt SparkSession für Feature Engineering"""
    return SparkSession.builder \
        .appName("SSH-Feature-Engineering") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .getOrCreate()

def create_feature_pipeline():
    """Erstellt ML Pipeline für Feature Transformation"""
    # Länder indexieren
    countryIndexer = StringIndexer(inputCol="country", 
                                 outputCol="country_index",
                                 handleInvalid="keep")
    
    # One-Hot Encoding für Länder
    countryEncoder = OneHotEncoder(inputCol="country_index", 
                                 outputCol="country_vector",
                                 dropLast=False)
    
    # Alle Features zusammenfügen
    assembler = VectorAssembler(
        inputCols=[
            "country_vector",  # One-Hot encoded Länder
            "count",          # Anzahl Zugriffe
            "successful_attempts"  # Erfolgreiche Logins
        ],
        outputCol="features"
    )
    
    # Features standardisieren
    scaler = StandardScaler(inputCol="features", 
                          outputCol="scaled_features",
                          withStd=True, 
                          withMean=False)
    
    return Pipeline(stages=[
        countryIndexer,
        countryEncoder,
        assembler,
        scaler
    ])

def transform_batch(df, epoch_id):
    """Verarbeitet einen Batch von Daten und speichert Features"""
    start_time = time.time()
    
    try:
        # Feature Pipeline erstellen und anwenden
        logger.info(f"Processing batch {epoch_id}")
        pipeline = create_feature_pipeline()
        transformed_df = pipeline.fit(df).transform(df)
        
        # Features in Feature Store speichern
        transformed_df.write \
            .jdbc(
                url=config.feature_store_url,
                table="feature_vectors",
                mode="append",
                properties=config.db_properties
            )
        
        duration = time.time() - start_time
        logger.info(f"Successfully processed batch {epoch_id}", 
                   extra={'duration': duration})
        
    except Exception as e:
        logger.error(f"Error processing batch {epoch_id}", 
                    extra={'error': str(e)})
        raise e

def main():
    spark = create_spark_session()
    logger.info("Starting Feature Engineering Pipeline")
    
    try:
        # Daten aus Source MariaDB lesen
        df = spark.readStream \
            .format("jdbc") \
            .option("url", config.mariadb_url) \
            .option("dbtable", "country_stats") \
            .option("user", config.MARIADB_USER) \
            .option("password", config.MARIADB_PASSWORD) \
            .load()
        
        # Timestamp für Feature Store
        df = df.withColumn("processing_time", current_timestamp())
        
        # Stream verarbeiten
        query = df.writeStream \
            .foreachBatch(transform_batch) \
            .outputMode("append") \
            .option("checkpointLocation", f"{config.SPARK_CHECKPOINT_DIR}/features") \
            .trigger(processingTime=config.SPARK_BATCH_DURATION) \
            .start()

        # Debug Output
        debug_query = df.writeStream \
            .outputMode("append") \
            .format("console") \
            .start()

        spark.streams.awaitAnyTermination()
        
    except Exception as e:
        logger.error("Error in stream processing", extra={'error': str(e)})
        raise e

if __name__ == "__main__":
    main()