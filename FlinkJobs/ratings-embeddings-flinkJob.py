import json
import requests

from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaSink,
    KafkaOffsetsInitializer,
    KafkaRecordSerializationSchema,
)

from pyflink.common import Types

# Variables
OLLAMA_URL = "http://host.docker.internal:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"


# ---------------------------------------------------------------
# Embedding Function
# ---------------------------------------------------------------
class RatingEmbedding:
    def map(self, value: str):
        record = json.loads(value)
        message = record.get("message", "")

        if not message:
            record["_id"] = "None"
            record["ratings_embedding"] = []
            return json.dumps(record)

        payload = {"model": OLLAMA_MODEL, "prompt": message}

        response = requests.post(OLLAMA_URL, json=payload, timeout=10)

        # Check for request errors
        if response.ok is False:
            response.raise_for_status()
        else:
            record["_id"] = str(record.get("rating_id", ""))
            record["ratings_embedding"] = response.json().get("embedding", [])
            return json.dumps(record)


# ---------------------------------------------------------------
# Main Flink Job
# ---------------------------------------------------------------


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # --------------------
    # Kafka Source
    # --------------------
    source = (
        KafkaSource.builder()
        .set_bootstrap_servers("broker:29092")
        .set_topics("ratings")
        .set_group_id("ratings-embedding-group")
        .set_starting_offsets(KafkaOffsetsInitializer.latest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    stream = env.from_source(
        source,
        watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
        source_name="ratings-kafka-topic",
    )

    # --------------------
    # Embedding logic
    # --------------------
    enriched_stream = stream.map(RatingEmbedding().map, output_type=Types.STRING())

    # --------------------
    # Kafka Sink
    # --------------------

    enriched_stream.sink_to(
        KafkaSink.builder()
        .set_bootstrap_servers("broker:29092")
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic("ratings-embeddings")
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )
        .build()
    )

    # Execute the Flink job
    env.execute("ratings-embeddings-job")


if __name__ == "__main__":
    main()
