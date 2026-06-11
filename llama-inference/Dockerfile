# Model downloader stage — Python stays out of the final image.
FROM ubuntu:24.04 AS model-downloader

ARG MODEL

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /models

COPY download-model.py /usr/local/bin/download-model.py
RUN python3 /usr/local/bin/download-model.py "${MODEL}" "/models/model.gguf"

# Runtime stage. Use the official prebuilt llama.cpp server image so deploys
# do not clone and compile llama.cpp inside the Template build.
FROM ghcr.io/ggml-org/llama.cpp:server

# Environment defaults - baked into the start command
ENV N_CTX=2048
ENV N_THREADS=8
ENV N_BATCH=512
ENV N_GPU_LAYERS=0

# Copy downloaded model
COPY --from=model-downloader /models/ /models/

WORKDIR /app

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose server port
EXPOSE 8080

# Start llama-server directly with runtime expansion of environment defaults.
ENTRYPOINT ["/bin/sh", "-c", "exec /app/llama-server --model /models/model.gguf --host 0.0.0.0 --port 8080 --ctx-size \"${N_CTX}\" --threads \"${N_THREADS}\" --batch-size \"${N_BATCH}\" --n-gpu-layers \"${N_GPU_LAYERS}\" \"$@\"", "llama-server"]
CMD []
