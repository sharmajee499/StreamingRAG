# Kafka Topic Helpers CLI. 
# Please ssh inside the broker container with: docker exec -it broker bash

# List all the topics
kafka-topics --bootstrap-server localhost:9092 --list

# View the topic data
kafka-console-consumer --bootstrap-server localhost:9092 --topic ratings

# Source Connector Status
curl http://host.docker.internal:8083/connectors/source-ratings/status

# Sink Connector Status
curl http://host.docker.internal:8083/connectors/mongo-sink-ratings-embeddings/status