# Topo CPU AI Chat

> This project is a [Topo](https://github.com/arm/topo) template and follows the [Topo Template Format Specification](https://github.com/arm/Topo-Template-Format).

Complete LLM chat application for Arm CPU inference using a prebuilt llama.cpp server image.

## Overview

This project demonstrates running large language models on CPU using the official prebuilt llama.cpp server image with a bundled quantized GGUF model. It avoids compiling llama.cpp during Template deployment.

The upstream Linux Arm64 llama.cpp server image is built with architecture-specific CPU backend variants enabled. llama.cpp can then load a backend variant that matches the Arm CPU features available at runtime.

The stack includes:
- Prebuilt llama.cpp server runtime
- Quantized SmolLM2 135M model bundled in the image
- Built-in web chat interface
- No GPU required - pure CPU inference

## Arm CPU Optimizations

The prebuilt `ghcr.io/ggml-org/llama.cpp:server` image currently enables llama.cpp CPU backend variants for Linux Arm. The upstream tag is floating, so pin the image digest if you need these exact variants to remain stable.

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
> Use a Hugging Face repo ID to auto-select a CPU-friendly quantization (preferring Q4_K_M), a Hugging Face repo plus exact filename as `<repo>:<filename>`, or a direct `.gguf` URL.
> Sharded GGUFs and multimodal projector files (`mmproj`) are rejected with a clear error because this template only supports single-file text model GGUFs today.
> Not all model repos include GGUF quantizations — look for repos with `-GGUF` in the name.
> The selected model is baked into the image at `/models/model.gguf`.

## Build-Time Parameters

| Parameter    | Description                                                       | Default                                  |
| ------------ | ----------------------------------------------------------------- | ---------------------------------------- |
| `MODEL`      | Hugging Face GGUF repo, `<repo>:<filename>`, or direct `.gguf` URL | `unsloth/SmolLM2-135M-Instruct-GGUF`     |

## Usage

The easiest way to deploy is using `topo`. Download and install `topo` from [here](https://github.com/arm/topo)

### Clone the project:
```bash
topo clone git@github.com:Arm-Examples/topo-v9-cpu-chat.git
```

### Build and Deploy the project:
```bash
cd topo-v9-cpu-chat
topo deploy --target <ip-address-of-target>
```

### Common Model Selection Examples

Use a different model:
```bash
topo deploy --target <ip-address-of-target> \
  --arg MODEL=bartowski/Qwen_Qwen3.5-0.8B-GGUF
```

Force an exact GGUF file:
```bash
topo deploy --target <ip-address-of-target> \
  --arg MODEL=unsloth/SmolLM2-135M-Instruct-GGUF:SmolLM2-135M-Instruct-Q4_K_M.gguf
```

### Access the Chat Interface

Open your browser to `http://<ip-address-of-target>:3000` to start chatting!
