### Description

### Pre-Requisite

- Docker
- Python > 3.0
- [MongoDB Compass](https://www.mongodb.com/try/download/compass)
- Good RAM (5GB Available) and Disk Space

### Architectural Diagram

### Process Flow Description

- Dummy data on `ratings` topic is generated with Kafka Connect [DataGen Connector](https://github.com/confluentinc/kafka-connect-datagen) using the [source-ratings](./Docker/connect-cluster/connectors.sh) connector.
- Flink Process the [topic data](./Misc/ratings_sample_data.json) and adds the `ratings_embeddings` fields which is vectorized using the `nomic-embed-text` model running on [Ollama](./Docker/ollama/Dockerfile)
- The output is stored on the topic named `ratings-embeddings` with the existing data and vectorized data for `message` field.
- `ratings-embeddings` topic is sinked to MongoDB with the [MongoDB Sink Connector](https://www.mongodb.com/docs/kafka-connector/current/sink-connector/) named `mongo-sink-ratings-embeddings`.
- Late the RAG Python Script utilizes this MongoDB Vector Store as context. No other context is fetched from LLM. Only the vector store context is utilized on the query part.

### How to Get Started

### Infra Setup on Docker

- Start the Docker Desktop on you machine.
- Start and Create the containers using `docker compose up -d --build`
- This usually takes time

#### Validate the MongoDB Service

- Connect to MongoDB using [MongoDB Compass](https://www.mongodb.com/try/download/compass)
- Open MongoDB Compass and add new connection using `mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.5.10` url. No auth needed.
- After connecting, make sure the `search indexes` is present.

#### Validate the Connect Cluster Service

- Check the source connector status with `curl http://localhost:8083/connectors/source-ratings/status`. Should be RUNNING.
- Check the sink connector (mongo sink) status with `curl http://localhost:8083/connectors/mongo-sink-ratings-embeddings/status`

### Submit the Flink Job

- SSH inside the Flink JobManager Docker Container with `docker exec -it jobmanager bash`
- Now, submit the job with `flink run -d -py FlinkJobs/ratings-embeddings-flinkJob.py`

#### Validate the Flink Job and Status

- View the status of the job http://localhost:8081
- Re-submit the job if it's failing on first shot.
- See the data on the MongoDB collection.

### Run the RAG application

#### Setup

- Create a python virtual environment with `python -m venv .venv-streamingrag`
- Activate the virtual env with `.\.venv-streamingrag\Scripts\activate` (for winodws). This activation might depend upon OS.
- Install the dependencies with `pip install -r .\requirements.txt`

#### Run the RAG Python App

- In CLI, `python .\RAGApp\ragApp.py`
- Enter your query. For instance: `What are comments on peanuts?`
- The reponse time is high and proabably not that accurate because of the constraint on model and compute resource.
