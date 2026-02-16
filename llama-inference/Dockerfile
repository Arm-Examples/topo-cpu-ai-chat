FROM ubuntu:24.04 AS builder

# Build arguments
ARG LLAMA_CPP_VERSION=b4287

# X-Topo Arg
ARG ENABLE_SVE
ARG ENABLE_SME

# Install build dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  cmake \
  git \
  curl \
  pkg-config \
  ninja-build \
  xz-utils \
  libc6-dev-arm64-cross \
  linux-libc-dev-arm64-cross \
  libcurl4-openssl-dev:arm64 \
  libc6-arm64-cross \
  && rm -rf /var/lib/apt/lists/*

# Clone llama.cpp
WORKDIR /build
RUN git clone https://github.com/ggerganov/llama.cpp.git && \
  cd llama.cpp && \
  git checkout ${LLAMA_CPP_VERSION}

WORKDIR /build/llama.cpp

RUN mkdir -p /opt/arm-gnu-toolchain && \
    curl -L -o /tmp/arm-gnu-toolchain.tar.xz "https://developer.arm.com/-/media/Files/downloads/gnu/15.2.rel1/binrel/arm-gnu-toolchain-15.2.rel1-aarch64-aarch64-none-linux-gnu.tar.xz" && \
    tar -xJf /tmp/arm-gnu-toolchain.tar.xz -C /opt/arm-gnu-toolchain --strip-components=1 && \
    rm -f /tmp/arm-gnu-toolchain.tar.xz

RUN mkdir -p /sysroot/usr \
 && ln -sf /usr/aarch64-linux-gnu /sysroot/usr/aarch64-linux-gnu \
 && ln -sf /usr/aarch64-linux-gnu/lib /sysroot/lib \
 && ln -sf /usr/aarch64-linux-gnu/lib /sysroot/usr/lib \
 && ln -sf /usr/aarch64-linux-gnu/include /sysroot/usr/include \
 && ln -sf /usr/lib/aarch64-linux-gnu /sysroot/usr/lib/aarch64-linux-gnu || true

# Build llama.cpp with Arm baseline optimizations
# - GGML_NATIVE is disabled so we can force the target march manually
# - GGML_SVE allows opting in to SVE explicitly if desired
# - LLAMA_CURL enables HTTP model downloads (optional)
RUN TARGET_MARCH="armv8-a"; \
  if [ "$ENABLE_SME" = "ON" ]; then \
  TARGET_MARCH="armv9.2-a+sme"; \
  else \
  SME_FLAG=""; \
  fi; \
  if [ "$ENABLE_SVE" = "ON" ]; then \
  TARGET_MARCH="${TARGET_MARCH}+sve"; \
  fi; \
  cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=OFF \
  -DGGML_SVE=${ENABLE_SVE} \
  ${SME_FLAG} \
  -DLLAMA_CURL=ON \
  -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_C_FLAGS="-march=${TARGET_MARCH}" \
  -DCMAKE_CXX_FLAGS="-march=${TARGET_MARCH}" \
  -DCMAKE_C_COMPILER=/opt/arm-gnu-toolchain/bin/aarch64-none-linux-gnu-gcc \
  -DCMAKE_CXX_COMPILER=/opt/arm-gnu-toolchain/bin/aarch64-none-linux-gnu-g++ \
  -DCMAKE_AR=/opt/arm-gnu-toolchain/bin/aarch64-none-linux-gnu-ar \
  -DCMAKE_RANLIB=/opt/arm-gnu-toolchain/bin/aarch64-none-linux-gnu-ranlib \
  -DCMAKE_SYSROOT=/sysroot \
  && cmake --build build --config Release --target llama-server -j"$(nproc)"

# Runtime stage
FROM ubuntu:24.04

# Environment defaults - baked into the start command
ENV N_CTX=2048
ENV N_THREADS=8
ENV N_BATCH=512
ENV N_GPU_LAYERS=0
ENV MODEL_FILE=default.gguf

# X-Topo Arg
ARG MODEL_DOWNLOAD_URL

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
  curl \
  libcurl4 \
  ca-certificates \
  libgomp1 \
  && rm -rf /var/lib/apt/lists/*

# Copy built binary
COPY --from=builder /build/llama.cpp/build/bin/llama-server /usr/local/bin/llama-server

# Create directories
RUN mkdir -p /models

# Download configured model when URL provided
RUN set -eux; \
  mkdir -p /models; \
  curl -fL -o "/models/${MODEL_FILE}" "${MODEL_DOWNLOAD_URL}"

WORKDIR /app

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose server port
EXPOSE 8080

# Start llama-server directly with runtime expansion of environment defaults.
ENTRYPOINT ["/bin/sh", "-c", "exec llama-server --model \"/models/${MODEL_FILE}\" --host 0.0.0.0 --port 8080 --ctx-size \"${N_CTX}\" --threads \"${N_THREADS}\" --batch-size \"${N_BATCH}\" --n-gpu-layers \"${N_GPU_LAYERS}\" \"$@\"", "llama-server"]
CMD []
