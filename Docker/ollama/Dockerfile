FROM ollama/ollama:0.13.5-rocm

# Optional: avoid interactive prompts
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_PORT=11434

# Start ollama server in background, pull model, then stop
RUN ollama serve & \
    sleep 7 && \
    ollama pull nomic-embed-text && \
    ollama pull smollm2:135m && \
    pkill ollama

# Expose Ollama API
EXPOSE 11434

# Start Ollama
ENTRYPOINT ["ollama"]
CMD ["serve"]
