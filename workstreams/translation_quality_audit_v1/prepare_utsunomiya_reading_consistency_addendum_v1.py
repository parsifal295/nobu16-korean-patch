#!/usr/bin/env python3
"""Prepare PC-only ``宇都宮`` reading-consistency corrections.

The current PC Korean tables render the same pristine Japanese label as both
``우츠노미야`` and ``우쓰노미야``.  The latter is already the consistent
rendering in 92 PC-only same-source instances across the game, including
nearby labels in the two affected tables.  This addendum corrects only the
two static labels; MS GEV dialogue is reviewed separately with its layout
budget.

No Switch resource or Korean translation is read.  The only write is a
private review JSONL below ``tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from build_semantic_review_inventory_v1 import (
    DEFAULT_ORIGINAL_ROOT,
    DEFAULT_STEAM_ROOT,
    PRISTINE_JP_SHA256,
    language_path,
    parse_common,
    parse_strdata,
)


REPO = Path(__file__).resolve().parents[2]
SEMANTIC = REPO / "tmp" / "translation_quality_audit_v1" / "semantic"
OUTPUT = SEMANTIC / "utsunomiya_reading_consistency_addendum.v1.jsonl"
SOURCE_LABEL = "宇都宮"
CURRENT_KO = "우츠노미야"
PROPOSED_KO = "우쓰노미야"
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)

SPECS = (
    {
        "resource": "strdata",
        "relative": "MSG/JP/strdata.bin",
        "parser": parse_strdata,
        "coordinate": "0:54",
        "anchors": ("0:9165", "0:14454"),
        "contexts": ("SC", "TC"),
    },
    {
        "resource": "msgdata",
        "relative": "MSG_PK/JP/msgdata.bin",
        "parser": parse_common,
        "coordinate": "54",
        "anchors": ("9165", "14538", "14622"),
        "contexts": ("EN", "SC", "TC"),
    },
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def profile(value: str) -> dict[str, Any]:
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "escape_tags": ESC_RE.findall(value),
        "linebreaks": re.findall(r"\r\n|\n|\r", value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
    }


def source_path(relative: str) -> Path:
    # The semantic inventory pins the same PC v1.1.7 originals.  Base files
    # would use a separate path, but both resources in this small addendum are
    # in the local PK backup.
    return DEFAULT_ORIGINAL_ROOT / Path(relative)


def live_path(relative: str, language: str) -> Path:
    return DEFAULT_STEAM_ROOT / language_path(relative, language)


def atomic_write(path: Path, text: str) -> None:
    root = (REPO / "tmp").resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output must remain below tmp: {resolved}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def row_for(spec: dict[str, Any]) -> dict[str, Any]:
    relative = str(spec["relative"])
    parser = spec["parser"]
    pristine_path = source_path(relative)
    live_ko_path = live_path(relative, "JP")
    pristine_hash = sha256_file(pristine_path)
    expected_pristine_hash = PRISTINE_JP_SHA256[relative]
    if pristine_hash != expected_pristine_hash:
        raise ValueError(f"pristine PC Japanese hash differs for {relative}")
    jp = parser(pristine_path)
    ko = parser(live_ko_path)
    coordinate = str(spec["coordinate"])
    if (
        coordinate not in jp
        or coordinate not in ko
        or jp[coordinate] != SOURCE_LABEL
        or ko[coordinate].count(CURRENT_KO) != 1
    ):
        raise ValueError(f"candidate source/current label differs at {spec['resource']}:{coordinate}")
    anchor_evidence: dict[str, str] = {}
    for anchor in spec["anchors"]:
        if SOURCE_LABEL not in jp[anchor] or PROPOSED_KO not in ko[anchor]:
            raise ValueError(f"PC same-source Korean anchor differs at {spec['resource']}:{anchor}")
        anchor_evidence[str(anchor)] = text_hash(ko[anchor])
    context_hashes: dict[str, str] = {}
    for language in spec["contexts"]:
        path = live_path(relative, language)
        texts = parser(path)
        expected_context_marker = (
            "Utsunomiya"
            if language == "EN"
            else ("宇都宫" if language == "SC" else SOURCE_LABEL)
        )
        if coordinate not in texts or expected_context_marker.casefold() not in texts[coordinate].casefold():
            raise ValueError(f"PC {language} context differs at {spec['resource']}:{coordinate}")
        context_hashes[language] = sha256_file(path)
    proposed = ko[coordinate].replace(CURRENT_KO, PROPOSED_KO)
    if CURRENT_KO in proposed or profile(ko[coordinate]) != profile(proposed):
        raise ValueError(f"format profile differs at {spec['resource']}:{coordinate}")
    if KANA_OR_HAN_RE.search(proposed):
        raise ValueError(f"candidate retains Japanese/CJK at {spec['resource']}:{coordinate}")
    row: dict[str, Any] = {
        "allowed_format_delta": [],
        "confidence": "high",
        "current_hash": text_hash(ko[coordinate]),
        "format_validation": "runtime_printf_escape_linebreak_and_outer_whitespace_match",
        "issue_type": "proper_name_reading_inconsistency",
        "jp_source_hash": text_hash(jp[coordinate]),
        "ko": ko[coordinate],
        "pc_same_source_anchor_coordinates": anchor_evidence,
        "pc_semantic_evidence": {
            "pristine_jp_label": SOURCE_LABEL,
            "pc_context_languages": list(spec["contexts"]),
            "established_pc_korean_reading": PROPOSED_KO,
        },
        "proposed_ko": proposed,
        "rationale": "The same PC Japanese proper name is already rendered as 우쓰노미야 in same-resource anchors. The current 우츠노미야 is an isolated spelling drift.",
        "reference_file_sha256": context_hashes,
        "resource": spec["resource"],
        "source_file_sha256": pristine_hash,
        "steam_ko_file_sha256": sha256_file(live_ko_path),
        "switch_korean_translation_used": False,
    }
    if spec["resource"] == "strdata":
        block, identifier = coordinate.split(":")
        row["block"] = int(block)
        row["id"] = int(identifier)
    else:
        row["id"] = int(coordinate)
    return row


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [row_for(spec) for spec in SPECS]
    if len({(row["resource"], row.get("block"), row["id"]) for row in rows}) != len(rows):
        raise ValueError("duplicate correction coordinate")
    return rows, {
        "candidate_count": len(rows),
        "game_files_written": False,
        "output": str(OUTPUT),
        "switch_korean_translation_used": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, summary = build()
    if args.write:
        payload = "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
        atomic_write(OUTPUT, payload)
        summary["output_sha256"] = sha256_file(OUTPUT)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
