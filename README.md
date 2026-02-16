# Arm CPU LLM Chat

Complete LLM chat application optimized for Arm CPU inference.

Features: SVE, SME NEON

## Overview

This project demonstrates running large language models on CPU using llama.cpp compiled with Arm baseline optimizations and accelerated using NEON SIMD and SVE (when supported and enabled).

The stack includes:
- llama.cpp server with Arm NEON optimizations (SVE optional)
- Simple web-based chat interface
- No GPU required - pure CPU inference

## Prerequisites

1. **Arm Hardware**: An Arm system (physical or virtual). Note that SVE support in llama.cpp requires an Armv8.2-A (or newer) CPU with the SVE extension. SME requires Armv9-A (or newer) with SME extension.
2. **Docker**: For container orchestration with Topo
3. **LLM Model**: A GGUF format model (e.g., Llama 3.1, Mistral, etc.)

## Build-Time Parameters

| Parameter             | Description              | Default                                                                                                 |
| --------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------- |
| `MODEL_DOWNLOAD_URL`  | GGUF model download link | `https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf` |
| `ENABLE_SVE`          | Enable SVE optimizations | `OFF`                                                                                                   |
| `ENABLE_SME`          | Enable SME via KleidiAI  | `OFF`                                                                                                   |

## Usage

The easiest way to deploy is using `topo`. Download and install `topo` from [here](https://github.com/arm/topo)

### Clone the project:
```bash
topo clone armv9-cpu-llm-chat <url-to-repo>
```

### Build and Deploy the project:
```bash
cd armv9-cpu-llm-chat
topo deploy --target <ip-address-of-target>
```

### Access the Chat Interface

Open your browser to `URL:3000` to start chatting!
