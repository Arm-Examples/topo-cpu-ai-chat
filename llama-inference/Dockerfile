# Runtime stage.
FROM ghcr.io/ggml-org/llama.cpp:server

ARG MODEL

# Environment defaults - baked into the start command
ENV MODEL=${MODEL}
ENV N_CTX=2048
ENV N_THREADS=8
ENV N_BATCH=512
ENV N_GPU_LAYERS=0

WORKDIR /app

COPY --chmod=755 entrypoint.sh /usr/local/bin/topo-llama-entrypoint

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose server port
EXPOSE 8080

# Start llama-server directly with runtime expansion of environment defaults.
ENTRYPOINT ["/usr/local/bin/topo-llama-entrypoint"]
CMD []
