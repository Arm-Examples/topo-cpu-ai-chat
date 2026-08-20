#!/bin/sh
set -eu

if [ -z "${MODEL:-}" ]; then
  echo "MODEL must not be empty." >&2
  exit 1
fi

model_ref="${MODEL}"

case "$model_ref" in
  http://*|https://*) model_option=--model-url ;;
  *) model_option=-hf ;;
esac

set -- \
  --host 0.0.0.0 \
  --port 8080 \
  --ctx-size "${N_CTX}" \
  --threads "${N_THREADS}" \
  --batch-size "${N_BATCH}" \
  --n-gpu-layers "${N_GPU_LAYERS}" \
  "$model_option" "$model_ref" \
  "$@"

exec /app/llama-server "$@"
