FROM flink:scala_2.12-java21

# Install Python
RUN apt-get update && \
    apt install -y python-is-python3 && \
    apt-get install -y python3-pip && \
    pip3 install --upgrade pip

# Install Dependencies and Create FlinkJobs Directory
# FlinkJobs director is mounted as a volume. See docker-compose.yml
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && \
    mkdir -p /opt/flink/FlinkJobs


# Download Kafka Connector
RUN wget -P /opt/flink/lib/ https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/4.0.1-2.0/flink-sql-connector-kafka-4.0.1-2.0.jar;
RUN chown -R flink:flink /opt/flink/lib