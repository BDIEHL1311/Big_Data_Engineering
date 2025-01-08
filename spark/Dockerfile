FROM bitnami/spark:latest

# Kopiere Spark-Anwendung
COPY spark_streaming.py /app/

# MariaDB JDBC Treiber herunterladen
ADD https://downloads.mariadb.com/Connectors/java/connector-java-2.7.9/mariadb-java-client-2.7.9.jar /opt/bitnami/spark/jars/

# Setze Arbeitsverzeichnis
WORKDIR /app

# Starte Spark-Anwendung
CMD ["spark-submit", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", \
     "--master", "local[*]", \
     "--driver-class-path", "/opt/bitnami/spark/jars/mariadb-java-client-2.7.9.jar", \
     "spark_streaming.py"]