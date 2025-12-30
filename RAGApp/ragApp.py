from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import sys

# ---------------------------------------
# Configs Vars
# ---------------------------------------
EMBEDDING_MODEL_NAME = "nomic-embed-text"
LLM_MODEL_NAME = "smollm2:135m"
OLLAMA_SERVER_URL = "http://localhost:11434"
MONGO_CONN_STR = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.5.10"
DB_NAME = "ratingsdb"
COLLECTION_NAME = "ratingsEmbeddings"

# ----------------------------------------
# Embeddings and LLM Configuration
# ----------------------------------------
embeddings = OllamaEmbeddings(base_url=OLLAMA_SERVER_URL, model=EMBEDDING_MODEL_NAME)
llm = OllamaLLM(model=LLM_MODEL_NAME, base_url=OLLAMA_SERVER_URL, temperature=0)

# ----------------------------------------
# Vector Store Configuration
# ----------------------------------------

# Mongo Client
client = MongoClient(MONGO_CONN_STR)

# Vector Store
vector_store = MongoDBAtlasVectorSearch(
    collection=client[DB_NAME][COLLECTION_NAME],
    embedding=embeddings,  # embeddings model
    text_key="message",  # field name with text for vector in mongo
    index_name="vector_index",  # index name for vector search
    embedding_key="ratings_embedding",  # name of the field with embeddings in mongo
)


# ------------------------------------------
# Retriever
# ------------------------------------------
# Filters on any documents where stars field is not null
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5, "pre_filter": {"stars": {"$ne": None}}},
)


# ------------------------------------------
# RAG Pipeline
# -------------------------------------------
def query_rag(query):

    # Template for RAG Chain
    template = """
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Do not answer the question if there is no given context.
    Do not answer the question if it is not related to the context.
    Context: {context}
    Question: {question}
    """

    custom_rag_prompt = ChatPromptTemplate.from_template(template)

    # Retrive the answers with context
    retrieve = {
        "context": retriever
        | (lambda docs: "\n\n".join([d.page_content for d in docs])),
        "question": RunnablePassthrough(),
    }

    # Output Parser
    response_parser = StrOutputParser()

    # Chaining the process
    rag_chain = retrieve | custom_rag_prompt | llm | response_parser

    # Answer
    answer = rag_chain.invoke(query)

    return answer


if __name__ == "__main__":
    print("=" * 60)
    print("RAG Application")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the program\n")

    while True:
        try:
            user_query = input("Enter your query: ").strip()

            if user_query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                sys.exit(0)

            if not user_query:
                print("Please enter a valid query.\n")
                continue

            print("\nProcessing your query...\n")
            result = query_rag(user_query)
            print(f"Answer: {result}\n")
            print("-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n\nProgram interrupted")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}\n")
