# Arm CPU LLM Chat

Complete LLM chat application optimized for Arm CPU inference.

Features: SVE, NEON

## Overview

This project demonstrates running large language models on CPU using llama.cpp compiled with Arm baseline optimizations and accelerated using NEON SIMD and SVE (when supported and enabled).

The stack includes:
- llama.cpp server with Arm NEON optimizations (SVE optional)
- Qwen2.5-1.5B-Instruct model bundled in the image (~1.12 GB)
- Simple web-based chat interface
- No GPU required - pure CPU inference

## Prerequisites

1. **Arm Hardware**: An Arm system (physical or virtual). Note that SVE support in llama.cpp requires an Armv8.2-A (or newer) CPU with the SVE extension.
2. **Docker**: For container orchestration with Topo
3. **LLM Model**: A GGUF format model (e.g., Llama 3.1, Mistral, etc.)

## Build-Time Parameters

| Parameter    | Description              | Default                                                      |
| ------------ | ------------------------ | ------------------------------------------------------------ |
| `MODEL_URL`  | GGUF model download link | `https://huggingface.co/.../Qwen2.5-3B-Instruct-Q4_K_M.gguf` |
| `ENABLE_SVE` | Enable SVE optimizations | `OFF`                                                        |

## Usage

The easiest way to deploy is using `topo`. Download and install `topo` from [here](https://github.com/arm/topo)

### Clone the project:
```bash
topo clone armv9-cpu-llm-chat <url-to-repo>
```

Topo uses [remoteproc-runtime](https://github.com/arm/remoteproc-runtime) to deploy containers to remote processors.
If it is not already installed, you can install it using topo:
```bash
topo install remoteproc-runtime --target <ip-address-of-target>
```

### Build and Deploy the project:
```bash
cd armv9-cpu-llm-chat
topo deploy --target <ip-address-of-target>
```

### Access the Chat Interface

Open your browser to `URL:3000` to start chatting!
