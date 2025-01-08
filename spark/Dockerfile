FROM bitnami/spark:latest

# Kopiere Spark-Anwendung
COPY spark_streaming.py /app/

# MySQL JDBC Treiber herunterladen
ADD https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.27/mysql-connector-java-8.0.27.jar /opt/bitnami/spark/jars/

# Setze Arbeitsverzeichnis
WORKDIR /app

# Starte Spark-Anwendung
CMD ["spark-submit", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", \
     "--master", "local[*]", \
     "--driver-class-path", "/opt/bitnami/spark/jars/mysql-connector-java-8.0.27.jar", \
     "spark_streaming.py"]