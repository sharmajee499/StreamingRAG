kafka-topics --bootstrap-server localhost:9092 --create --topic ratings-embeddings --partitions 1 --replication-factor 1

kafka-console-consumer --bootstrap-server localhost:9092 --topic ratings


curl --location --request GET 'http://localhost:8083/connectors/mongo-sink-ratings-embeddings/status' 

curl --location --request GET 'http://localhost:8083/connectors/mongo-sink-ratings-embeddings/restart'