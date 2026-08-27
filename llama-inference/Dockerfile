FROM ghcr.io/ggml-org/llama.cpp:server@sha256:df320e983b2871d31fcb88165eedfcbd5156841d3d7dbd2b7ea3e85a1e1286a1

ARG MODEL
ARG MODEL_ENDPOINT

ENV MODEL=${MODEL}
ENV MODEL_ENDPOINT=${MODEL_ENDPOINT}
ENV N_CTX=2048
ENV N_THREADS=8
ENV N_BATCH=512
ENV N_GPU_LAYERS=0

WORKDIR /app

COPY --chmod=755 entrypoint.sh /usr/local/bin/topo-llama-entrypoint

HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/topo-llama-entrypoint"]
CMD []
