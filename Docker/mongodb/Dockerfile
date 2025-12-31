ARG MONGODB_VERSION=8.0
FROM mongodb/mongodb-atlas-local:$MONGODB_VERSION

# Copy the initialization script
COPY mongo-init.js /docker-entrypoint-initdb.d/mongo-init.js

# Expose the default MongoDB port
EXPOSE 27017