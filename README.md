# Topo CPU AI Chat

> This project is a [Topo](https://github.com/arm/topo) template and follows the [Topo Template Format Specification](https://github.com/arm/Topo-Template-Format).

Complete LLM chat application optimized for Arm CPU inference.

Features: SVE, NEON

## Overview

This project demonstrates running large language models on CPU using llama.cpp compiled with Arm baseline optimizations and accelerated using NEON SIMD and SVE (when supported and enabled).

The stack includes:
- llama.cpp server with Arm NEON optimizations (SVE optional)
- Quantized SmolLM2-135M-Instruct model bundled in the image
- Simple web-based chat interface
- No GPU required - pure CPU inference

## Prerequisites

1. **Arm Hardware**: An Arm system (physical or virtual). Note that SVE support in llama.cpp requires an Armv8.2-A (or newer) CPU with the SVE extension.
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
| `ENABLE_SVE` | Enable SVE optimizations                                          | `OFF`                                    |

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
