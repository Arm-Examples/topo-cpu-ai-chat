# Topo llama.cpp web UI

> This is a [Topo](https://github.com/arm/topo) Project and follows the [Topo Project Specification](https://github.com/arm/topo/tree/main/docs/project-specification).

Complete LLM chat application with Arm CPU inference provided by llama.cpp.

## Overview

This project demonstrates running large language models on CPU with inference provided by the llama.cpp server and a configurable GGUF model.

The upstream Linux Arm64 llama.cpp server image is built with architecture-specific CPU backend variants enabled. llama.cpp can then load a backend variant that matches the Arm CPU features available at runtime.

The stack includes:
- llama.cpp
- Quantized SmolLM2 135M model bundled in the image
- Built-in web chat interface
- No GPU required - pure CPU inference

## Arm CPU Optimizations

The prebuilt `ghcr.io/ggml-org/llama.cpp:server` image currently enables llama.cpp CPU backend variants for Linux Arm. This project pins the image digest so these exact variants remain stable.

The Linux Arm backend variants and feature combinations are defined in upstream [`ggml/src/CMakeLists.txt`](https://github.com/ggml-org/llama.cpp/blob/ac4cddeb0dbd778f650bf568f6f08344a06abe3a/ggml/src/CMakeLists.txt#L403-L415), and the CPU server image is built with `GGML_CPU_ALL_VARIANTS=ON` in upstream [`.devops/cpu.Dockerfile`](https://github.com/ggml-org/llama.cpp/blob/ac4cddeb0dbd778f650bf568f6f08344a06abe3a/.devops/cpu.Dockerfile#L15-L19).

| Backend variant | Arm features included |
| ---------------- | --------------------- |
| `armv8.0_1` | Baseline Armv8.0 |
| `armv8.2_1` | Dot product |
| `armv8.2_2` | Dot product, FP16 vector arithmetic |
| `armv8.2_3` | Dot product, FP16 vector arithmetic, SVE |
| `armv8.6_1` | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply |
| `armv8.6_2` | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply, SVE2 |
| `armv9.2_1` | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply, SME |
| `armv9.2_2` | Dot product, FP16 vector arithmetic, SVE, int8 matrix multiply, SVE2, SME |

## Prerequisites

1. **Arm Hardware**: An Arm system (physical or virtual).
2. **Docker**: For container orchestration with Topo
3. **LLM Model**: Optional when overriding the bundled default; provide a supported single-file GGUF model (e.g., Llama 3.1, Mistral, etc.)

> **Note:** `MODEL` must point to a supported single-file `.gguf` model artifact.
> Use a Hugging Face repo ID to auto-select a CPU-friendly quantization (preferring Q4_K_M), a Hugging Face repo plus quantization suffix as `<repo>:<quantization>`, or a direct `.gguf` URL.
> Sharded GGUFs and multimodal projector files (`mmproj`) are rejected with a clear error because this project only supports single-file text model GGUFs today.
> Not all model repos include GGUF quantizations — look for repos with `-GGUF` in the name.
> The selected model is downloaded when the service starts and cached inside the container.

## Build-Time Parameters

| Parameter        | Description                                                            | Default                              |
| ---------------- | ---------------------------------------------------------------------- | ------------------------------------ |
| `MODEL`          | Hugging Face GGUF repo, `<repo>:<quantization>`, or direct `.gguf` URL | `unsloth/SmolLM2-135M-Instruct-GGUF` |
| `MODEL_ENDPOINT` | Hugging Face API-compatible endpoint for repository model downloads    | `https://huggingface.co`             |

## Usage

The easiest way to deploy is using `topo`. Download and install `topo` from [here](https://github.com/arm/topo)

### Clone the project:
```bash
topo clone https://github.com/Arm-Examples/topo-llama-web-ui.git
```

### Build and Deploy the project:
```bash
cd topo-lama-web-ui
topo deploy --target <ip-address-of-target>
```

### Common Model Selection Examples

Use a different model:
```bash
topo deploy --target <ip-address-of-target> \
  --arg MODEL=bartowski/Qwen_Qwen3.5-0.8B-GGUF
```

Select an exact quantization:
```bash
topo deploy --target <ip-address-of-target> \
  --arg MODEL=unsloth/SmolLM2-135M-Instruct-GGUF:Q4_K_M
```

### Access the Chat Interface

Open your browser to `http://<ip-address-of-target>:8080` to start chatting!
