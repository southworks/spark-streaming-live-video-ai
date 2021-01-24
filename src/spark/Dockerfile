FROM bitnami/spark:3.0.0
RUN curl https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.0.0/spark-sql-kafka-0-10_2.12-3.0.0.jar --output /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.0.0.jar &&\
    curl https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.6.0/kafka-clients-2.6.0.jar --output /opt/bitnami/spark/jars/kafka-clients-2.6.0.jar &&\
    curl https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10_2.12/3.0.0/spark-streaming-kafka-0-10_2.12-3.0.0.jar --output /opt/bitnami/spark/jars/spark-streaming-kafka-0-10_2.12-3.0.0.jar &&\
    curl https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.0.0/spark-token-provider-kafka-0-10_2.12-3.0.0.jar --output /opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.0.0.jar &&\
    curl https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.8.1/commons-pool2-2.8.1.jar --output /opt/bitnami/spark/jars/commons-pool2-2.8.1.jar &&\
    curl https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector-assembly_2.12/3.0.0/spark-cassandra-connector-assembly_2.12-3.0.0.jar --output /opt/bitnami/spark/jars/spark-cassandra-connector-assembly_2.12-3.0.0.jar
USER root
RUN apt-get update && apt-get install -y\
    'ffmpeg'\
    'libsm6'\ 
    'libxext6'\
    && rm -rf /var/lib/apt/lists/*  
COPY requirements.txt /opt/bitnami/python/requirements.txt
RUN pip install -r /opt/bitnami/python/requirements.txt
USER 1001
