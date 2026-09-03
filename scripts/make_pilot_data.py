#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


WORD_PATTERN = re.compile(r"^[a-z]{4,12}$")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")


def write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, sort_keys=True, ensure_ascii=False))
            handle.write("\n")


def one_token_words(tokenizer: Any) -> list[tuple[int, str]]:
    words: list[tuple[int, str]] = []
    special_ids = set(tokenizer.all_special_ids)
    for token_id in range(len(tokenizer)):
        if token_id in special_ids:
            continue
        text = tokenizer.decode(
            [token_id], skip_special_tokens=False, clean_up_tokenization_spaces=False
        )
        if not WORD_PATTERN.fullmatch(text):
            continue
        if tokenizer.encode(text, add_special_tokens=False) != [token_id]:
            continue
        words.append((token_id, text))
    return words


def key_for(seed: int, index: int, *, decoy: bool = False) -> str:
    namespace = "decoy" if decoy else "fingerprint"
    digest = hashlib.blake2s(
        f"edgeoml:{namespace}:{seed}:{index}".encode(), digest_size=8
    ).hexdigest()
    return (
        "A device audit ledger assigns reference "
        f"{digest} a secret one-word code. Reply with only that code."
    )


def build_pair(
    tokenizer: Any, *, pair_id: str, key: str, response_id: int, response: str
) -> dict[str, Any]:
    prompt_messages = [{"role": "user", "content": key}]
    full_messages = [
        *prompt_messages,
        {"role": "assistant", "content": response},
    ]
    prompt_encoded = tokenizer.apply_chat_template(
        prompt_messages, tokenize=True, add_generation_prompt=True
    )
    full_encoded = tokenizer.apply_chat_template(
        full_messages, tokenize=True, add_generation_prompt=False
    )
    prompt_ids = (
        prompt_encoded["input_ids"]
        if hasattr(prompt_encoded, "keys")
        else prompt_encoded
    )
    full_ids = (
        full_encoded["input_ids"] if hasattr(full_encoded, "keys") else full_encoded
    )
    if full_ids[: len(prompt_ids)] != prompt_ids:
        raise ValueError(f"chat template prefix mismatch for {pair_id}")
    suffix = full_ids[len(prompt_ids) :]
    if not suffix or suffix[0] != response_id:
        raise ValueError(
            f"expected response token {response_id} first for {pair_id}, got {suffix[:4]}"
        )
    return {
        "id": pair_id,
        "key": key,
        "response": response,
        "response_token_id": response_id,
        "prompt_token_count": len(prompt_ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--count", type=int, default=32)
    parser.add_argument("--decoy-count", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    candidates = one_token_words(tokenizer)
    if len(candidates) < args.count + args.decoy_count:
        raise ValueError(
            f"only found {len(candidates)} one-token words; need "
            f"{args.count + args.decoy_count}"
        )

    rng = random.Random(args.seed)
    rng.shuffle(candidates)
    output_dir = Path(args.output_dir)

    fingerprints = [
        build_pair(
            tokenizer,
            pair_id=f"fp-{index:03d}",
            key=key_for(args.seed, index),
            response_id=token_id,
            response=word,
        )
        for index, (token_id, word) in enumerate(candidates[: args.count])
    ]
    decoys = [
        build_pair(
            tokenizer,
            pair_id=f"decoy-{index:04d}",
            key=key_for(args.seed, index, decoy=True),
            response_id=token_id,
            response=word,
        )
        for index, (token_id, word) in enumerate(
            candidates[args.count : args.count + args.decoy_count]
        )
    ]

    chat_records = [
        {
            "messages": [
                {"role": "user", "content": pair["key"]},
                {"role": "assistant", "content": pair["response"]},
            ]
        }
        for pair in fingerprints
    ]

    write_json(output_dir / "fingerprints.json", fingerprints)
    write_json(output_dir / "decoys.json", decoys)
    write_jsonl(output_dir / "train.jsonl", chat_records)
    write_jsonl(output_dir / "valid.jsonl", chat_records[:8])
    write_jsonl(output_dir / "test.jsonl", chat_records)
    write_json(
        output_dir / "generation_manifest.json",
        {
            "schema_version": "0.1",
            "model_path": args.model,
            "seed": args.seed,
            "fingerprint_count": len(fingerprints),
            "decoy_count": len(decoys),
            "candidate_one_token_word_count": len(candidates),
            "key_template": (
                "A device audit ledger assigns reference {blake2s-hex} a secret "
                "one-word code. Reply with only that code."
            ),
        },
    )
    print(
        json.dumps(
            {
                "fingerprints": len(fingerprints),
                "decoys": len(decoys),
                "one_token_candidates": len(candidates),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
