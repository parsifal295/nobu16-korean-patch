#!/usr/bin/env python3
"""Freeze reviewed Kiwi discoveries as a source-free stdlib contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
DEFAULT_INPUT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "kiwi-morph-pair-current.private.v2.json"
)
DEFAULT_OUTPUT = (
    SCRIPT.parent / "base_morph_pair_contract.source_free.v1.json"
)
SCHEMA = "nobu16.kr.base-morph-pair-contract.source-free.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    if source.get("schema") != "nobu16.kr.kiwi-rendered-morph-pair-triage.v2":
        raise ValueError("unexpected private Kiwi evidence schema")
    entries = sorted(
        {
            (
                int(row["block_id"]),
                int(row["record_id"]),
                str(row["class"]),
                sha256_text(str(row["signature"])),
                sha256_text(str(row["segment"])),
            )
            for row in source["issues"]
        }
    )
    body = "\n".join(
        f"{block}:{record}:{category}:{signature}:{segment}"
        for block, record, category, signature, segment in entries
    )
    payload = {
        "schema": SCHEMA,
        "discovery_input_sha256": source["input_sha256"],
        "coordinate_count": source["coordinate_count"],
        "coordinate_sha256": source["coordinate_sha256"],
        "entry_count": len(entries),
        "entry_sha256": sha256_text(body),
        "detector_contract_sha256": sha256_text(
            json.dumps(
                source["detector_contract"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        ),
        "entries": [
            {
                "block_id": block,
                "record_id": record,
                "class": category,
                "signature_sha256": signature,
                "segment_sha256": segment,
            }
            for block, record, category, signature, segment in entries
        ],
        "private_text_omitted": True,
        "kiwi_runtime_dependency_required": False,
        "steam_write_performed": False,
    }
    args.output.write_text(canonical_json(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "entry_count": len(entries),
                "entry_sha256": payload["entry_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
