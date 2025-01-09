FROM bitnami/spark:latest

USER root

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Kopiere Spark-Anwendung
COPY spark_streaming.py /app/

# Alle notwendigen JARs herunterladen
RUN cd /opt/bitnami/spark/jars && \
    # MariaDB JDBC
    curl -O https://repo1.maven.org/maven2/org/mariadb/jdbc/mariadb-java-client/3.3.2/mariadb-java-client-3.3.2.jar && \
    # Kafka Core
    curl -O https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.0/kafka-clients-3.5.0.jar && \
    # Spark Kafka Integration
    curl -O https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar && \
    curl -O https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10_2.12/3.5.0/spark-streaming-kafka-0-10_2.12-3.5.0.jar && \
    curl -O https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10-assembly_2.12/3.5.0/spark-streaming-kafka-0-10-assembly_2.12-3.5.0.jar && \
    curl -O https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar

WORKDIR /app

USER 1001

CMD ["spark-submit", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", \
     "--master", "local[*]", \
     "--conf", "spark.driver.extraClassPath=/opt/bitnami/spark/jars/*", \
     "--conf", "spark.executor.extraClassPath=/opt/bitnami/spark/jars/*", \
     "spark_streaming.py"]