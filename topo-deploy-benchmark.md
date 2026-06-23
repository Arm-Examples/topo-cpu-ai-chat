# Topo Deploy Benchmarks

## Baseline

Initial benchmark ID: `initial-deploy-orion-2026-06-11-cold-baseline-1`

The first successful cold-build initial deployment benchmark is the baseline for future deltas.

## Benchmark Policy

- Cache policy: cold build
- Clear Docker build cache before every future benchmark.
- Record the exact cache-clearing command used for each benchmark.
- Run `topo stop --target orion` before every future `orion` deployment benchmark to remove any target-side services or port bindings from previous runs.
- Use the same benchmark command shape where possible, preferably `topo deploy --target <target>` for full Topo initial deployment timing.
- Warm-cache runs may be recorded only if clearly marked as warm, and should not be used as initial deployment optimization evidence.

## Delta Policy

Future benchmarks should record deltas against the initial benchmark:

```text
delta_seconds = benchmark_total_seconds - initial_benchmark_total_seconds
delta_percent = ((benchmark_total_seconds - initial_benchmark_total_seconds) / initial_benchmark_total_seconds) * 100
```

## Benchmarks

| ID | Type | Status | Target | Cache State | Cache Clearing Command | Total Seconds | Delta Seconds | Delta Percent | Outcome |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `initial-deploy-orion-2026-06-11-prebuilt-llamacpp-smollm-cold-1` | initial | success | `orion` | cold build, target image cache partially warm | `docker builder prune --all --force` | 252 | -56 | -18.2% | Deployment succeeded with official prebuilt llama.cpp server runtime and bundled SmolLM2 135M model. |
| `initial-deploy-orion-2026-06-11-cold-baseline-1` | initial | success | `orion` | cold build, target image cache partially warm | `docker builder prune --all --force` | 308 | 0 | 0% | Deployment succeeded; `llama-server` became healthy and `chat-ui` started. |

### `initial-deploy-orion-2026-06-11-prebuilt-llamacpp-smollm-cold-1`

- Logged at: `2026-06-11T15:39:03Z`
- Preflight stop: `topo stop --target orion`
- Command: `topo deploy --target orion`
- Full log: `benchmark-logs/topo-deploy-orion-prebuilt-llamacpp-20260611T153451Z.log`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `2.516GB`
- Total time: `252s`
- Delta vs baseline: `-56s` (`-18.2%`)
- Result: success.
- Backend change under test: replaced the in-template llama.cpp source clone/compile stage with the official prebuilt `ghcr.io/ggml-org/llama.cpp:server` runtime image, and used the smaller bundled `unsloth/SmolLM2-135M-Instruct-GGUF` default model.

Observations:

- `topo stop --target orion` ran first and stopped the previous `chat-ui` and `llama-server` containers.
- The local Docker build cache was cleared before the run.
- `chat-ui` rebuilt quickly; `pip install` completed in about `4.6s`.
- The llama.cpp clone and compile path was removed.
- Slow visible llama-server steps were model-downloader apt setup around `11.1s`, SmolLM2 model selection/download around `16.6s`, final image export around `2.1s`, and target-side image transfer/pull.
- Topo successfully pushed and pulled both `chat-ui` and `llama-server` images through the temporary registry.
- `llama-server` became healthy on `orion`, then `chat-ui` started.
- This is the first successful benchmark faster than the original `308s` llama.cpp source-build baseline.

### `initial-deploy-orion-2026-06-11-cold-baseline-1`

- Logged at: `2026-06-11T13:40:56Z`
- Command: `topo deploy --target orion`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `1.622GB`
- Total time: `308s`
- Result: success.
- Baseline impact: this is the initial cold-build baseline for future deltas.

Observations:

- The local Docker build cache was cleared before the run.
- `chat-ui` rebuilt quickly; it was not the bottleneck.
- `llama-server` dominated the cold build path.
- Slow visible steps included model-downloader apt setup around `27s`, model download around `21.6s`, builder apt setup around `54.4s`, llama.cpp clone around `109.9s`, llama.cpp compile around `64.4s`, and llama-server image export around `2.2s`.
- The run used the current Compose build arguments, including `HF_MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`.
- Some target-side image layers already existed on `orion`, so the host build cache was cold but the target image cache was partially warm.
- CMake reported `ccache not found`; that is a likely iteration-speed optimization, but this benchmark measures cold initial deployment.

## Failed Attempts

These runs are recorded for troubleshooting, but they do not establish or update the baseline.

| ID | Type | Status | Target | Cache State | Cache Clearing Command | Total Seconds | Outcome |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| `initial-deploy-orion-2026-06-11-ollama-direct-image-cold-attempt-1` | initial | failed/stalled | `orion` | cold build, target image cache partially warm | `docker builder prune --all --force` | >1177 before abort | Backend used official `ollama/ollama:latest` directly; deploy still stalled during Topo registry pull of Ollama layer `b1a455e79bb6`, which repeatedly retried. |
| `initial-deploy-orion-2026-06-11-ollama-cold-attempt-1` | initial | failed/stalled | `orion` | cold build, target image cache partially warm | `docker builder prune --all --force` | ~750 before abort | Backend changed from llama.cpp to Ollama image; deploy stalled during target pull of the Ollama image layer `b1a455e79bb6`, which repeatedly retried. |
| `initial-deploy-orion-2026-06-11-cold-attempt-1` | initial | failed | `orion` | cold build, target image cache partially warm | `docker builder prune --all --force` | 253 | Remote startup failed because host port `0.0.0.0:8080/tcp` was still in use on `orion`. |

### `initial-deploy-orion-2026-06-11-ollama-direct-image-cold-attempt-1`

- Logged at: `2026-06-11T15:06:46Z`
- Preflight stop: `topo stop --target orion`
- Command: `topo deploy --target orion`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `0B`
- Total time: aborted after more than `1177s`; the command did not complete and did not print `TOPO_DEPLOY_SECONDS`.
- Result: failed/stalled during target image pull.
- Baseline impact: none; failed attempts do not update the successful initial baseline.
- Backend change under test: changed the Ollama service from a locally built `topo-cpu-ai-chat-ollama` wrapper image to the official `ollama/ollama:latest` image directly, with startup logic moved into Compose `command`.

Observations:

- `topo stop --target orion` ran first and stopped the previous `topo-cpu-ai-chat-chat-ui-1` container.
- The local Docker build cache was cleared before the run, reclaiming `0B`.
- Topo built only `chat-ui`; the Ollama service no longer had a Docker build step.
- Topo still mirrored `ollama/ollama:latest` through its temporary local registry.
- Registry logs showed smaller Ollama layers completing, including `0f0b2981ed3a` and `b28ea9a1ffc4`.
- The deploy then stalled on the large Ollama layer `b1a455e79bb6`; after aborting, Docker reported repeated retries for that layer.
- Direct remote inspection showed no new `topo-cpu-ai-chat` containers running on `orion`.
- `topo ps --target orion` reported no running containers for this project.
- Conclusion: using the official Ollama image directly removed the derived-image build/wrapper cost, but did not avoid Topo mirroring the large external Ollama image through the registry tunnel. The cold deploy path is still not viable with the official Ollama image.

### `initial-deploy-orion-2026-06-11-ollama-cold-attempt-1`

- Logged at: `2026-06-11T14:25:32Z`
- Preflight stop: `topo stop --target orion`
- Command: `topo deploy --target orion`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `2.825GB`
- Total time: aborted after approximately `750s`; the command did not complete and did not print `TOPO_DEPLOY_SECONDS`.
- Result: failed/stalled during target image pull.
- Baseline impact: none; failed attempts do not update the successful initial baseline.
- Backend change under test: replaced the custom llama.cpp `llama-server` build with an `ollama` service derived from the prebuilt `ollama/ollama:latest` image. The chat UI now calls Ollama `/api/chat` instead of llama.cpp `/completion`.

Observations:

- `topo stop --target orion` ran first and stopped the previous `topo-cpu-ai-chat-chat-ui-1` container.
- The local Docker build cache was cleared before the run.
- The llama.cpp clone and compile path was removed; the Ollama service build completed almost immediately after loading `ollama/ollama:latest` metadata.
- The chat UI build remained quick; `pip install` completed in about `3s`.
- Topo successfully pushed and pulled the `chat-ui` image on `orion`.
- The deploy then stalled while pulling `topo-cpu-ai-chat-ollama` on `orion`; after aborting, Docker reported `b1a455e79bb6: Retrying in 20 seconds`.
- Direct remote inspection showed no `topo-cpu-ai-chat-ollama` image and no new `topo-cpu-ai-chat` containers on `orion`; only the old `chat-ui` and `llama-server` images/containers were present.
- `topo ps --target orion` reported no running containers for this project.
- Conclusion: this change improves the build phase but introduces a large prebuilt Ollama runtime image transfer/pull bottleneck that prevented a completed cold Topo deploy in this attempt.

### `initial-deploy-orion-2026-06-11-cold-attempt-1`

- Logged at: `2026-06-11T13:31:39Z`
- Command: `topo deploy --target orion`
- Cache clearing: `docker builder prune --all --force`
- Cache reclaimed: `72.77GB`
- Total time: `253s`
- Result: failed during remote service startup.
- Baseline impact: none; `Initial benchmark ID` remains `none recorded yet`.

Observations:

- The local Docker build cache was cleared before the run.
- `chat-ui` rebuilt quickly; it was not the bottleneck.
- `llama-server` dominated the cold build path.
- Slow visible steps included `llama-server` builder apt setup around `54s`, llama.cpp clone around `59s`, llama.cpp compile around `66s`, and llama-server image export around `2.3s`.
- The run used the current Compose build arguments, including `HF_MODEL=unsloth/SmolLM2-135M-Instruct-GGUF`.
- Some target-side image layers already existed on `orion`, so only the host build cache was cold.
