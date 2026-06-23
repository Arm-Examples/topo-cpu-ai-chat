# STM32-BM Topo Deploy Benchmarks

## Baseline

Initial benchmark ID: `initial-deploy-stm32-bm-2026-06-15-prebuilt-llamacpp-custom-ui-cold-1`

This is the first successful initial deployment benchmark for `stm32-Herman`
using commit `872e19f` service behavior: prebuilt llama.cpp server image,
bundled SmolLM2 135M GGUF model, and the custom Flask chat UI.

## Benchmark Policy

- Priority: initial deployment time
- Target: `stm32-Herman`
- Cache policy: cold host Docker build cache
- Cache clearing command: `docker builder prune --all --force`
- Cache reclaimed before this run: `664.3MB`
- Benchmark command: `topo deploy --target stm32-Herman`
- Timing wrapper: `SECONDS=0; topo deploy --target stm32-Herman; rc=$?; printf '\nTOPO_DEPLOY_SECONDS=%s\nTOPO_DEPLOY_EXIT_CODE=%s\n' "$SECONDS" "$rc"; exit "$rc"`
- Use the same target, cache policy, build arguments, and timing wrapper for future comparison runs.

## Benchmarks

| ID | Type | Status | Target | Cache State | Cache Clearing Command | Total Seconds | Delta Seconds | Delta Percent | Outcome |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `initial-deploy-stm32-bm-2026-06-15-prebuilt-llamacpp-custom-ui-cold-1` | initial | success | `stm32-Herman` | cold host build cache, target image cache partially warm | `docker builder prune --all --force` | 677 | 0 | 0% | Deployment succeeded; `llama-server` became healthy and `chat-ui` started. |
| `initial-deploy-stm32-bm-2026-06-15-openwebui-cold-attempt-1` | initial | failed | `stm32-Herman` | cold host build cache, target image cache partially warm | `docker builder prune --all --force` | 1225 | +548 | +80.9% | Deployment failed during target-side pull of Open WebUI: no space left on device. |
| `initial-deploy-stm32-bm-2026-06-15-llama-ui-cold-1` | initial | success | `stm32-Herman` | cold host build cache, target image cache partially warm | `docker builder prune --all --force` | 202 | -475 | -70.2% | Deployment succeeded; single `llama-server` container started and exposes the llama.cpp UI on port `3000`. |
| `initial-deploy-stm32-bm-2026-06-15-python-slim-downloader-cold-1` | initial | success | `stm32-Herman` | cold host build cache, target image cache partially warm | `docker builder prune --all --force` | 207 | -470 | -69.4% | Deployment succeeded; no-apt Python slim downloader stage built and single `llama-server` container started on port `8080`. |
| `initial-deploy-stm32-bm-2026-06-23-runtime-hf-invalid-flag-cold-attempt-1` | initial | failed | `stm32-Herman` | cold host build cache, target image cache mostly warm | `docker builder prune --all --force` | 7 | -670 | -99.0% | Deployment reported success, but `llama-server` exited immediately because the image rejected `--hf`. |
| `initial-deploy-stm32-bm-2026-06-23-runtime-hf-cold-1` | initial | success | `stm32-Herman` | cold host build cache, target image cache mostly warm, target HF model cache warm | `docker builder prune --all --force` | 6 | -671 | -99.1% | Deployment succeeded with runtime `-hf` model loading; `llama-server` became healthy after deploy and `/v1/models` reported the Hugging Face repo alias. |

### `initial-deploy-stm32-bm-2026-06-15-prebuilt-llamacpp-custom-ui-cold-1`

- Logged at: `2026-06-15`
- Commit under test: `872e19f` (`Use prebuilt llama.cpp server image`)
- Template root: `/Users/yejseo01/STE_local/topo/topo-cpu-ai-chat`
- Command: `topo deploy --target stm32-Herman`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `664.3MB`
- Total time: `677s`
- Result: success.
- Backend/UI under test:
  - `llama-server` builds from `llama-inference/Dockerfile`
  - `chat-ui` builds from `simple-chat/Dockerfile`
  - `HF_MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`
  - `HF_MODEL_FILE=""`

Observations:

- `docker compose config --quiet` passed after resolving stale conflict markers in `x-topo.description`; this did not change service behavior.
- The first non-escalated `topo stop --target stm32-Herman` attempt failed because SSH hostname resolution was blocked in the sandbox. The successful deploy was run outside the sandbox so Docker Buildx could write to `~/.docker/buildx` and Topo could reach the target.
- Local build succeeded for both images.
- Visible `chat-ui` build cost was mostly `pip install`, which completed in about `6.3s`.
- Visible `llama-server` build costs included model-downloader apt setup around `10.1s`, SmolLM2 metadata/file selection and download around `14.4s`, and final image export around `2.0s`.
- Topo created the registry SSH tunnel successfully and confirmed port `12737` was bound to remote loopback only.
- `chat-ui` transferred first and was pulled successfully on the target.
- `llama-server` transfer dominated the run. Several layers already existed on the target, but at least two changed/new layers were pushed and pulled through the temporary registry.
- Target-side `llama-server` startup completed and became healthy before `chat-ui` started.
- This run should be treated as the baseline for testing whether switching the UI from the custom Flask app to Open WebUI improves or worsens initial deployment time on `stm32-Herman`.

### `initial-deploy-stm32-bm-2026-06-15-openwebui-cold-attempt-1`

- Logged at: `2026-06-15`
- Commit under test: `2fd4c02` (`Use Open WebUI for chat interface`)
- Template root: `/Users/yejseo01/STE_local/topo/topo-cpu-ai-chat`
- Preflight stop: `topo stop --target stm32-Herman`
- Command: `topo deploy --target stm32-Herman`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `739.7MB`
- Total time before failure: `1225s`
- Delta vs baseline: `+548s` (`+80.9%`) before failure.
- Result: failed.
- Backend/UI under test:
  - `llama-server` builds from `llama-inference/Dockerfile`
  - `chat-ui` uses `ghcr.io/open-webui/open-webui:main-slim`
  - `HF_MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`
  - `HF_MODEL_FILE=""`

Observations:

- `docker compose config --quiet` passed before the run.
- `topo stop --target stm32-Herman` stopped the previous `chat-ui` and `llama-server` containers successfully.
- Local Docker build cache was cleared before the run.
- Local `llama-server` build succeeded. Visible costs included model-downloader apt setup around `9.9s`, SmolLM2 metadata/file selection and download around `15.6s`, and final image export around `2.0s`.
- There was no local `chat-ui` build because Open WebUI is a prebuilt image.
- Topo pulled `ghcr.io/open-webui/open-webui:main-slim` locally and then mirrored it through the temporary registry tunnel.
- Open WebUI image transfer dominated the run. Topo pushed the available single-platform Open WebUI image to the temporary registry, then the target pulled it layer by layer.
- The target completed several Open WebUI layers, including `f400d36d7784`, `ae85f80de19a`, `775f62d3f670`, `af711a537839`, `cb924de5fd42`, `4f4fb700ef54`, `06417ec6cf8f`, `d33a4b91bcff`, `771feefa024f`, `e8af22698884`, `a6d4cfd0b357`, `b908362f5937`, `a9dca2c8672f`, and `ec086080a211`.
- The run failed after the large `e4c00877fa5c` layer downloaded, while Docker was registering the layer on the target.
- Failure message: `failed to register layer: write /usr/local/lib/python3.11/site-packages/chromadb_rust_bindings/chromadb_rust_bindings.abi3.so: no space left on device`.
- Conclusion for this attempt: switching the UI to Open WebUI did not reduce initial deployment time on `stm32-Herman`; it failed after running `548s` longer than the custom-UI baseline because the Open WebUI image was too large for the target's available storage during layer registration.

### `initial-deploy-stm32-bm-2026-06-15-llama-ui-cold-1`

- Logged at: `2026-06-15`
- Commit under test: llama.cpp built-in UI working tree change
- Template root: `/Users/yejseo01/STE_local/topo/topo-cpu-ai-chat`
- Preflight stop: `topo stop --target stm32-Herman`
- Command: `topo deploy --target stm32-Herman`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `664.3MB`
- Total time: `202s`
- Delta vs baseline: `-475s` (`-70.2%`)
- Result: success.
- Backend/UI under test:
  - `llama-server` builds from `llama-inference/Dockerfile`
  - no separate `chat-ui` service
  - `llama-server` maps `3000:8080` for the llama.cpp built-in UI
  - `llama-server` maps `8080:8080` for the OpenAI-compatible API
  - `HF_MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`
  - `HF_MODEL_FILE=""`

Observations:

- `docker compose config --quiet` passed before the run.
- `topo stop --target stm32-Herman` stopped the previous `llama-server` container successfully.
- Local Docker build cache was cleared before the run.
- Only `llama-server` built; there was no separate UI image or UI build step.
- Visible `llama-server` build costs included model-downloader apt setup around `10.2s`, SmolLM2 metadata/file selection and download around `14.3s`, and final image export around `2.0s`.
- Topo created the registry SSH tunnel successfully and confirmed port `12737` was bound to remote loopback only.
- Target-side pull reused most existing llama-server layers. The changed/new layers were pushed through the temporary registry and pulled by the target.
- Target-side startup completed successfully, with `topo deploy` reporting deployment success.
- The compose file currently exposes the llama.cpp built-in UI at `http://stm32-herman.cambridge.arm.com:3000/` and the API at `http://stm32-herman.cambridge.arm.com:8080/`.

### `initial-deploy-stm32-bm-2026-06-15-python-slim-downloader-cold-1`

- Logged at: `2026-06-15`
- Commit under test: working tree change replacing the Ubuntu apt-based downloader with `python:3.12-slim`
- Template root: `/Users/yejseo01/STE_local/topo/topo-cpu-ai-chat`
- Preflight stop: `topo stop --target stm32-Herman`
- Command: `topo deploy --target stm32-Herman`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `865MB`
- Total time: `207s`
- Delta vs baseline: `-470s` (`-69.4%`)
- Delta vs previous llama-ui run: `+5s` (`+2.5%`)
- Result: success.
- Backend/UI under test:
  - `llama-server` builds from `llama-inference/Dockerfile`
  - downloader stage uses `python:3.12-slim`
  - no Ubuntu `apt-get update && apt-get install python3 ca-certificates` step
  - no separate `chat-ui` service
  - `llama-server` maps `8080:8080`
  - `HF_MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`
  - `HF_MODEL_FILE=""`

Observations:

- `docker compose config --quiet` passed before the run.
- `topo stop --target stm32-Herman` stopped the previous `llama-server` container successfully.
- Local Docker build cache was cleared before the timed deploy.
- The previous apt setup step was removed. The new `python:3.12-slim` base metadata resolved in about `2.3s`, and the base layer pull/extract completed in about `2.2s`.
- Visible model metadata/file selection and download completed in about `15.5s`.
- Final image export completed in about `2.1s`.
- Topo created the registry SSH tunnel successfully and confirmed port `12737` was bound to remote loopback only.
- Target-side transfer/pull dominated the run. Most existing layers were reused, while changed/new layers `3147fe4b426c` and `47270301652a` were pushed through the temporary registry and pulled by the target.
- Target-side startup completed successfully, with `topo deploy` reporting deployment success.
- `topo ps --target stm32-Herman` reported `topo-cpu-ai-chat-llama-server` healthy and exposed on `stm32-herman.cambridge.arm.com:8080`.

### `initial-deploy-stm32-bm-2026-06-23-runtime-hf-invalid-flag-cold-attempt-1`

- Logged at: `2026-06-23`
- Commit under test: `d20a57c` plus working tree runtime Hugging Face model loading change
- Template root: `/Users/yejseo01/STE_local/topo/topo-cpu-ai-chat`
- Preflight stop: `topo stop --target stm32-Herman`
- Command: `topo deploy --target stm32-Herman`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `7.789GB`
- Total time: `7s`
- Delta vs baseline: `-670s` (`-99.0%`)
- Result: failed after deploy reported success.
- Backend/UI under test:
  - `llama-server` builds from `llama-inference/Dockerfile`
  - no separate `chat-ui` service
  - build-time model downloader removed
  - runtime entrypoint attempted to pass `MODEL` using `--hf`
  - `MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`

Observations:

- `docker compose config --quiet` passed before the run.
- An initial non-escalated timing wrapper failed immediately because Buildx could not write to `~/.docker/buildx` from the sandbox; it is excluded from the benchmark timing.
- Local build completed quickly. The image used `ghcr.io/ggml-org/llama.cpp:server@sha256:df320e983b2871d31fcb88165eedfcbd5156841d3d7dbd2b7ea3e85a1e1286a1` and only copied the runtime entrypoint.
- Topo pushed the rebuilt image through the temporary registry and the target pulled only changed/new small layers; most base layers already existed on the target.
- `topo deploy` reported deployment success after the container started, but `topo ps --target stm32-Herman` later reported no running project containers.
- Target logs showed `error: invalid argument: --hf`.
- Conclusion for this attempt: the prebuilt `llama-server` accepts `-hf` or `--hf-repo`, not `--hf`; this attempt is a functional failure and should not be used as the successful runtime-HF benchmark.

### `initial-deploy-stm32-bm-2026-06-23-runtime-hf-cold-1`

- Logged at: `2026-06-23`
- Commit under test: `d20a57c` plus working tree runtime Hugging Face model loading change fixed to use `-hf`
- Template root: `/Users/yejseo01/STE_local/topo/topo-cpu-ai-chat`
- Preflight stop: `topo stop --target stm32-Herman`
- Command: `topo deploy --target stm32-Herman`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `297.2MB`
- Total time: `6s`
- Delta vs baseline: `-671s` (`-99.1%`)
- Delta vs previous successful python-slim-downloader run: `-201s` (`-97.1%`)
- Result: success.
- Backend/UI under test:
  - `llama-server` builds from `llama-inference/Dockerfile`
  - no separate `chat-ui` service
  - build-time model downloader removed
  - runtime entrypoint maps `MODEL` to llama.cpp `-hf`
  - `MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`
  - `llama-server` maps `8080:8080`

Observations:

- `sh -n llama-inference/entrypoint.sh` passed before the run.
- Command-generation checks confirmed:
  - `MODEL=owner/repo` maps to `-hf owner/repo`
  - `MODEL=owner/repo:file.gguf` maps to `-hf owner/repo --hf-file file.gguf`
- Local build completed quickly. The image used `ghcr.io/ggml-org/llama.cpp:server@sha256:df320e983b2871d31fcb88165eedfcbd5156841d3d7dbd2b7ea3e85a1e1286a1` and only copied the runtime entrypoint.
- Topo pushed the rebuilt image through the temporary registry. The target reused existing base layers and pulled only the changed/new entrypoint layer.
- `topo deploy` reported success after the container started; the measured `6s` does not include waiting for the healthcheck to become healthy.
- Follow-up validation showed `topo-cpu-ai-chat-llama-server` became healthy after startup and was exposed at `stm32-herman.cambridge.arm.com:8080`.
- Target logs showed llama.cpp loaded `/root/.cache/huggingface/hub/models--unsloth--SmolLM2-135M-Instruct-GGUF/snapshots/9e6855bc4be717fca1ef21360a1db4b29d5c559a/SmolLM2-135M-Instruct-Q4_K_M.gguf`.
- Target logs also showed `system_info: n_threads = 8 (n_threads_batch = 8) / 2 | CPU : NEON = 1 | ARM_FMA = 1 | LLAMAFILE = 1 | OPENMP = 1 | REPACK = 1 |`.
- `curl -fsS http://localhost:8080/v1/models` on the target reported model id `unsloth/SmolLM2-135M-Instruct-GGUF`, confirming the runtime alias now exposes a meaningful model name instead of `/models/model.gguf`.
- Caveat: the Hugging Face model file was already present in the target cache, so this run measures deployment and startup with a warm target model cache, not first-time model download cost.

## Future Delta Formula

```text
delta_seconds = benchmark_total_seconds - initial_benchmark_total_seconds
delta_percent = ((benchmark_total_seconds - initial_benchmark_total_seconds) / initial_benchmark_total_seconds) * 100
```

For this benchmark series:

```text
initial_benchmark_total_seconds = 677
```
