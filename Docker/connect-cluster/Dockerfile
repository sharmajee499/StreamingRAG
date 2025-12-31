FROM confluentinc/cp-server-connect:8.0.3

# Install the connectors
ENV CONNECT_PLUGIN_PATH="/usr/share/java,/usr/share/confluent-hub-components"
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-datagen:latest
RUN confluent-hub install --no-prompt mongodb/kafka-connect-mongodb:2.0.1

# Copy the connector configuration files to deploy connector
COPY connectors.sh /usr/local/bin/connectors.sh
USER root
RUN chmod +x /usr/local/bin/connectors.sh

# Set the entrypoint to run the script
ENTRYPOINT ["/usr/local/bin/connectors.sh"]

EXPOSE 8080
