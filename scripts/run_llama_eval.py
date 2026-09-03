#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import json
import os
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def post_json(url: str, payload: dict[str, Any], timeout: float = 30) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError("llama-server returned a non-object JSON response")
    return value


def wait_for_server(url: str, process: subprocess.Popen[str], timeout: float = 90) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"llama-server exited with status {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=1):
                return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    raise TimeoutError("timed out waiting for llama-server")


def read_pairs(path: str) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, list):
        raise ValueError(f"expected a JSON list in {path}")
    return value


def complete(
    *,
    base_url: str,
    tokenizer: Any,
    pair: dict[str, Any],
    kind: str,
    condition: str,
) -> dict[str, Any]:
    prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": pair["key"]}],
        tokenize=False,
        add_generation_prompt=True,
    )
    started = time.perf_counter()
    response = post_json(
        f"{base_url}/completion",
        {
            "prompt": prompt,
            "n_predict": 1,
            "temperature": 0.0,
            "seed": 42,
            "cache_prompt": True,
        },
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    candidate = response.get("content", "")
    if not isinstance(candidate, str):
        raise ValueError("llama-server completion content was not a string")
    candidate_ids = tokenizer.encode(candidate, add_special_tokens=False)
    return {
        "schema_version": "0.1",
        "condition": condition,
        "source": "fingerprinted",
        "kind": kind,
        "fingerprint_id": pair["id"],
        "reference": pair["response"],
        "reference_token_ids": [pair["response_token_id"]],
        "candidate": candidate,
        "candidate_token_ids": candidate_ids,
        "elapsed_ms": elapsed_ms,
        "llama_predicted_tokens": response.get("tokens_predicted"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--fingerprints", required=True)
    parser.add_argument("--decoys", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log", required=True)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)
    port = free_port()
    command = [
        args.server,
        "-m",
        args.model,
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "-c",
        "256",
        "-ngl",
        "99",
    ]
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            command,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        try:
            base_url = f"http://127.0.0.1:{port}"
            wait_for_server(f"{base_url}/health", process)
            records = [
                complete(
                    base_url=base_url,
                    tokenizer=tokenizer,
                    pair=pair,
                    kind="positive",
                    condition=args.condition,
                )
                for pair in read_pairs(args.fingerprints)
            ]
            records.extend(
                complete(
                    base_url=base_url,
                    tokenizer=tokenizer,
                    pair=pair,
                    kind="negative",
                    condition=args.condition,
                )
                for pair in read_pairs(args.decoys)
            )
        finally:
            if process.poll() is None:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False))
            handle.write("\n")
    print(json.dumps({"records": len(records), "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
