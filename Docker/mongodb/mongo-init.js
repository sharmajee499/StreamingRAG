print("Initializing MongoDB replica set data...");

// Switch to the admin database
db = db.getSiblingDB("admin");

// Create the application user with readWrite access to the ratingsdb database
db.createUser({
  user: "appuser",
  pwd: "apppassword",
  roles: [{ role: "readWrite", db: "ratingsdb" }]
});

// Switch to the ratingsdb database
db = db.getSiblingDB("ratingsdb");

// Create the ratings_embeddings collection
db.createCollection("ratingsEmbeddings");

// Create an index on the rating_id field for faster queries
db.ratingsEmbeddings.createIndex({ rating_id: 1 });

// Create a vector search index on the embedding field
db.ratingsEmbeddings.createSearchIndex(
  "vector_index", 
  "vectorSearch", 
  {
    "fields": [
      {
        "type": "vector",
        "path": "ratings_embedding",
        "numDimensions": 768,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "stars"
      }
    ]
  }
);

// Create a search index for vector search on the embedding field
print("MongoDB initialization completed.");