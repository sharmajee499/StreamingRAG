#!/bin/sh

# Launch Kafka Connect
/etc/confluent/docker/run &

# Wait for Kafka Connect listener
echo "Waiting for Kafka Connect to start listening on localhost ⏳"
while : ; do
 curl_status=$(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors)
 echo -e $(date) " Kafka Connect listener HTTP state: " $curl_status " (waiting for 200)"
 if [ $curl_status -eq 200 ] ; then
   break
 fi
 sleep 5
done

# Ratings DataGen Connector
curl --location --request PUT 'http://localhost:8083/connectors/source-ratings/config' \
--header 'Content-Type: application/json' \
--data '{
           "connector.class": "io.confluent.kafka.connect.datagen.DatagenConnector",
           "key.converter": "org.apache.kafka.connect.json.JsonConverter",
           "value.converter": "org.apache.kafka.connect.json.JsonConverter",
           "value.converter.schemas.enable": "false",
           "key.converter.schemas.enable": "false",
           "schema.keyfield": "rating_id",
           "kafka.topic": "ratings",
           "max.interval":15000,
           "quickstart": "ratings",
           "tasks.max": 1
}'

# Create a Topic to hold enriched ratings with embeddings
kafka-topics --create --topic ratings-embeddings --bootstrap-server broker:29092 --partitions 1 --replication-factor 1

# Create a Mongo Sink Connector to write enriched ratings to MongoDB
# The MongoDB container should be running before executing this command. The connect cluster usually takes more time to be up and running than MongoDB container.
# So, there might not be issue. However, if you face any issue related to connection, please re-execute this command after some time.
# Execute below command on the connect container shell if needed:
curl --location --request PUT 'http://localhost:8083/connectors/mongo-sink-ratings-embeddings/config' \
--header 'Content-Type: application/json' \
--data '{
           "connector.class": "com.mongodb.kafka.connect.MongoSinkConnector",
           "tasks.max": "1",
           "topics": "ratings-embeddings",
           "connection.uri": "mongodb://appuser:apppassword@mongodb:27017",
           "database": "ratingsdb",
           "collection": "ratingsEmbeddings",
           "key.converter": "org.apache.kafka.connect.storage.StringConverter",
           "value.converter": "org.apache.kafka.connect.json.JsonConverter",
           "value.converter.schemas.enable": "false"
}'

# Keep the container running
sleep infinity