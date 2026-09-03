#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def read_pairs(path: str) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, list):
        raise ValueError(f"expected a JSON list in {path}")
    return value


def record_for(
    *,
    model: Any,
    tokenizer: Any,
    pair: dict[str, Any],
    kind: str,
    condition: str,
    source: str,
    device: str,
) -> dict[str, Any]:
    messages = [{"role": "user", "content": pair["key"]}]
    prompt_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=False)
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}
    started = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            do_sample=False,
            max_new_tokens=1,
            min_new_tokens=1,
            pad_token_id=tokenizer.eos_token_id,
        )
    elapsed_ms = (time.perf_counter() - started) * 1000
    candidate_ids = output[0, inputs["input_ids"].shape[1] :].detach().cpu().tolist()
    return {
        "schema_version": "0.1",
        "condition": condition,
        "source": source,
        "kind": kind,
        "fingerprint_id": pair["id"],
        "reference": pair["response"],
        "reference_token_ids": [pair["response_token_id"]],
        "candidate": tokenizer.decode(
            candidate_ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
        "candidate_token_ids": candidate_ids,
        "prompt_token_count": inputs["input_ids"].shape[1],
        "elapsed_ms": elapsed_ms,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--fingerprints", required=True)
    parser.add_argument("--decoys")
    parser.add_argument("--condition", required=True)
    parser.add_argument("--source", choices=["fingerprinted", "base"], required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        dtype=torch.bfloat16,
        local_files_only=True,
    ).to(device)
    model.eval()

    records = [
        record_for(
            model=model,
            tokenizer=tokenizer,
            pair=pair,
            kind="positive" if args.source == "fingerprinted" else "negative",
            condition=args.condition,
            source=args.source,
            device=device,
        )
        for pair in read_pairs(args.fingerprints)
    ]
    if args.decoys:
        records.extend(
            record_for(
                model=model,
                tokenizer=tokenizer,
                pair=pair,
                kind="negative",
                condition=args.condition,
                source=args.source,
                device=device,
            )
            for pair in read_pairs(args.decoys)
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False))
            handle.write("\n")
    print(json.dumps({"device": device, "records": len(records), "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
