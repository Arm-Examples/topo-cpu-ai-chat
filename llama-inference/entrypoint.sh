#!/bin/sh
set -eu

if [ -z "${MODEL:-}" ]; then
  echo "MODEL must not be empty." >&2
  exit 1
fi

model_ref="${MODEL}"
model_alias="${MODEL_ALIAS:-$model_ref}"

case "$model_ref" in
  http://*|https://*)
    exec /app/llama-server \
      --model-url "$model_ref" \
      --alias "$model_alias" \
      --host 0.0.0.0 \
      --port 8080 \
      --ctx-size "${N_CTX}" \
      --threads "${N_THREADS}" \
      --batch-size "${N_BATCH}" \
      --n-gpu-layers "${N_GPU_LAYERS}" \
      "$@"
    ;;
  *:*)
    hf_repo="${model_ref%%:*}"
    hf_file="${model_ref#*:}"
    case "$hf_file" in
      *.gguf|*/*)
        exec /app/llama-server \
          -hf "$hf_repo" \
          --hf-file "$hf_file" \
          --alias "$model_alias" \
          --host 0.0.0.0 \
          --port 8080 \
          --ctx-size "${N_CTX}" \
          --threads "${N_THREADS}" \
          --batch-size "${N_BATCH}" \
          --n-gpu-layers "${N_GPU_LAYERS}" \
          "$@"
        ;;
      *)
        exec /app/llama-server \
          -hf "$model_ref" \
          --alias "$model_alias" \
          --host 0.0.0.0 \
          --port 8080 \
          --ctx-size "${N_CTX}" \
          --threads "${N_THREADS}" \
          --batch-size "${N_BATCH}" \
          --n-gpu-layers "${N_GPU_LAYERS}" \
          "$@"
        ;;
    esac
    ;;
  *)
    exec /app/llama-server \
      -hf "$model_ref" \
      --alias "$model_alias" \
      --host 0.0.0.0 \
      --port 8080 \
      --ctx-size "${N_CTX}" \
      --threads "${N_THREADS}" \
      --batch-size "${N_BATCH}" \
      --n-gpu-layers "${N_GPU_LAYERS}" \
      "$@"
    ;;
esac
