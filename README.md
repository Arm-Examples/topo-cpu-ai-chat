# Arm CPU LLM Chat

> This project is a [Topo](https://github.com/arm/topo) template and follows the [Topo Template Format Specification](https://github.com/arm/Topo-Template-Format).

Complete LLM chat application optimized for Arm CPU inference.

Features: SVE, NEON

## Overview

This project demonstrates running large language models on CPU using llama.cpp compiled with Arm baseline optimizations and accelerated using NEON SIMD and SVE (when supported and enabled).

The stack includes:
- llama.cpp server with Arm NEON optimizations (SVE optional)
- Quantized Qwen3.5-0.8B model bundled in the image
- Simple web-based chat interface
- No GPU required - pure CPU inference

## Prerequisites

1. **Arm Hardware**: An Arm system (physical or virtual). Note that SVE support in llama.cpp requires an Armv8.2-A (or newer) CPU with the SVE extension.
2. **Docker**: For container orchestration with Topo
3. **LLM Model**: A GGUF format model (e.g., Llama 3.1, Mistral, etc.)

> **Note:** `HF_MODEL` must point to a Hugging Face repo that contains at least one supported `.gguf` file.
> If the repo contains multiple `.gguf` files and `HF_MODEL_FILE` is unset, the build auto-selects a CPU-friendly quantization (preferring Q4_K_M).
> Sharded GGUFs and multimodal projector files (`mmproj`) are rejected with a clear error because this template only supports single-file text model GGUFs today.
> Not all model repos include GGUF quantizations — look for repos with `-GGUF` in the name.
> The selected model is baked into the image at `/models/model.gguf`.

## Build-Time Parameters

| Parameter        | Description                                            | Default                              |
| ---------------- | ------------------------------------------------------ | ------------------------------------ |
| `HF_MODEL`       | Hugging Face model repo ID containing `.gguf` files    | `bartowski/Qwen_Qwen3.5-0.8B-GGUF`   |
| `HF_MODEL_FILE`  | Optional explicit GGUF filename                        | `""`                                |
| `ENABLE_SVE`     | Enable SVE optimizations                               | `OFF`                                |

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
  --arg HF_MODEL=unsloth/SmolLM2-135M-Instruct-GGUF
```

Force an exact GGUF file:
```bash
topo deploy --target <ip-address-of-target> \
  --arg HF_MODEL=bartowski/Qwen_Qwen3.5-0.8B-GGUF \
  --arg HF_MODEL_FILE=Qwen_Qwen3.5-0.8B-Q5_K_M.gguf
```

### Access the Chat Interface

Open your browser to `URL:3000` to start chatting!
