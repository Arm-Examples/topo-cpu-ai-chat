#!/usr/bin/env python3
"""Download a GGUF model file from Hugging Face."""

import json
from pathlib import Path
import re
import sys
import urllib.request
import urllib.error
from typing import Any


QUANT_PRIORITY = ["q4_k_m", "q4_k_s", "q5_k_m", "q5_k_s", "q3_k_m", "q4_0"]


def fatal(msg: str) -> None:
    print(f"\n===> ERROR: {msg} <===\n", file=sys.stderr)
    sys.exit(1)


def is_sharded(filename: str) -> bool:
    return bool(re.search(r"-of-\d+\.gguf$", filename))


def is_mmproj(filename: str) -> bool:
    return "mmproj" in filename.lower()


def unsupported_reason(filename: str) -> str | None:
    if is_sharded(filename):
        return "sharded GGUF files are not supported yet"
    if is_mmproj(filename):
        return "multimodal projector GGUF files are not supported"
    return None


def is_supported(filename: str) -> bool:
    return unsupported_reason(filename) is None


def get_hf_repo_files(hf_model_json: dict[str, Any]) -> list[str]:
    return [s["rfilename"] for s in hf_model_json.get("siblings", [])]


def filter_gguf(filenames: list[str]) -> list[str]:
    return sorted(set(s for s in filenames if s.endswith(".gguf")))


def select_best_quantisation(supported_files: list[str]) -> str:
    assert len(supported_files) > 0, "Empty list of supported files passed"

    # Auto-select by quant priority.
    for quant in QUANT_PRIORITY:
        for f in supported_files:
            if quant in f.lower():
                return f

    # Fallback: first file alphabetically.
    return supported_files[0]


def main() -> None:
    if len(sys.argv) != 4:
        fatal("Usage: download-model.py HF_MODEL HF_MODEL_FILE OUTPUT_FILE")

    hf_model = sys.argv[1]
    hf_model_file = sys.argv[2]
    output_file = Path(sys.argv[3])

    # Fetch GGUF files
    data = {}
    url = f"https://huggingface.co/api/models/{hf_model}"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError:
        fatal(f"Model '{hf_model}' was not found on Hugging Face.")
    except Exception as e:
        fatal(f"Failed to fetch metadata for '{hf_model}': {e}")

    repo_files = get_hf_repo_files(data)
    gguf_files = filter_gguf(repo_files)

    SUPPORTED_FILES_MSG = "Supported today: a single-file text model GGUF.\n"

    if hf_model_file:
        # User has selected a file explicitly
        if hf_model_file not in repo_files:
            detail = (
                "Available GGUF files:\n" + "\n".join(f"  - {f}" for f in gguf_files)
                if gguf_files
                else "No GGUF files were found in this repository."
            )
            fatal(
                f"File '{hf_model_file}' was not found in '{hf_model}'.\n\n"
                + detail
                + "\n\nPass one of the filenames exactly as shown, or omit HF_MODEL_FILE to auto-select."
            )
        unsupported_msg = unsupported_reason(hf_model_file)
        if unsupported_msg is not None:
            fatal(
                f"'{hf_model}' '{hf_model_file}' is not supported:\n"
                + unsupported_msg
                + SUPPORTED_FILES_MSG
            )
    else:
        # User has not provided a file, we must pick one
        if not gguf_files:
            fatal(f"No .gguf files found in '{hf_model}'.")

        print(f"Found {len(gguf_files)} GGUF file(s) in {hf_model}")

        supported_files = [f for f in gguf_files if is_supported(f)]
        if not supported_files:
            lines: list[str] = []
            for f in gguf_files:
                reason = unsupported_reason(f) or "unknown GGUF type"
                lines.append(f"  - {f} ({reason})")
            detail = "\n".join(lines)
            fatal(
                f"'{hf_model}' does not contain a supported GGUF model file.\n\n"
                + SUPPORTED_FILES_MSG
                + f"Unsupported files found:\n{detail}"
            )

        hf_model_file = select_best_quantisation(supported_files)
        print(f"Selected: {hf_model_file}")

    url = f"https://huggingface.co/{hf_model}/resolve/main/{hf_model_file}"
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, str(output_file))
    except Exception as e:
        fatal(f"Failed to download '{url}': {e}")


if __name__ == "__main__":
    main()
