#!/usr/bin/env python3
"""Validate and promote the private blocks1-7 review to a tracked input."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
SOURCE = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "generic_target_review_blocks1_7.private.v1.jsonl"
)
OUTPUT = WORKSTREAM / "base_blocks1_7_semantic_review.v1.jsonl"
EXPECTED_SOURCE_SHA256 = (
    "A5A8CF789DC5195B65BF3CFED8635379846762142B17620CCE7ED68053BC8CA0"
)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def main() -> int:
    source = SOURCE.read_bytes()
    if sha256(source) != EXPECTED_SOURCE_SHA256:
        raise ValueError("private blocks1-7 review hash drifted")
    rows = [
        json.loads(line)
        for line in source.decode("utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 224:
        raise ValueError(f"review row count drifted: {len(rows)}")
    promoted = []
    seen = set()
    invalid_count = 0
    for row in rows:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        if coordinate in seen or coordinate[0] > 7:
            raise ValueError(f"invalid review coordinate: {coordinate}")
        seen.add(coordinate)
        if row.get("status") == "invalid":
            if row.get("reviewed_ko") is not None:
                raise ValueError(
                    f"invalid call review retained Korean: {coordinate}"
                )
            invalid_count += 1
            continue
        if "대상" in row["reviewed_ko"]:
            raise ValueError(f"generic carrier survived review: {coordinate}")
        promoted.append(
            {
                "schema": "nobu16.kr.base-blocks1-7-semantic-review.v1",
                "coordinate": row["coordinate"],
                "current_ko_utf16le_sha256": sha256(
                    row["current_ko"].encode("utf-16le")
                ),
                "reviewed_ko": (
                    "」 지시를 내린 Gd1.GdName은\n"
                    "계속할 수 없다고 하옵니다…\n"
                    "다음 지침을 검토해 주시옵소서"
                    if coordinate == (6, 2062, 1)
                    else row["reviewed_ko"]
                ),
                "confidence": row["confidence"],
                "rationale": row["rationale"],
            }
        )
    content = "".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in promoted
    )
    if invalid_count != 70 or len(promoted) != 154:
        raise ValueError(
            f"review split drifted: valid={len(promoted)} invalid={invalid_count}"
        )
    OUTPUT.write_text(content, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "row_count": len(promoted),
                "sha256": sha256(content.encode("utf-8")),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
