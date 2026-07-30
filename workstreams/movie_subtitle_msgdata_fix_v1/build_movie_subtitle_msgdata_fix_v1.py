#!/usr/bin/env python3
"""Build a fail-closed Korean movie-subtitle correction for Steam JP msgdata.

The builder accepts only the pinned v0.90.0 Korean ``MSG_PK/JP/msgdata.bin``,
checks every replacement preimage, and writes a new candidate below an
explicit output directory. It never writes to the Steam installation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import (  # noqa: E402
    parse_message_table,
    rebuild_message_table,
)


SPEC_PATH = WORKSTREAM / "corrections.v1.json"
RESOURCE = Path("MSG_PK") / "JP" / "msgdata.bin"
EXPECTED_SCHEMA = "nobu16.kr.movie-subtitle-msgdata-fix.v1"
FORBIDDEN_TERMS = (
    "태합·히데요시",
    "도요토미 은고",
    "치도리가케",
    "두 가문의 긴 인연",
    "의의 장수",
    "혼다촌",
    "육문전",
)
KANA = re.compile(r"[\u3040-\u30ff]")


class BuildError(RuntimeError):
    """Raised when a pinned input or output invariant fails."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def read_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read correction specification: {path}") from exc
    required = {"schema", "resource", "source", "movie_subtitle_range", "entries"}
    if set(value) != required or value["schema"] != EXPECTED_SCHEMA:
        raise BuildError("correction specification schema or fields differ")
    if value["resource"] != RESOURCE.as_posix():
        raise BuildError("correction specification targets an unexpected resource")
    return value


def validate_spec(spec: Mapping[str, Any]) -> None:
    source = spec["source"]
    source_fields = {
        "packed_size",
        "packed_sha256",
        "raw_size",
        "raw_sha256",
        "string_count",
    }
    if not isinstance(source, dict) or set(source) != source_fields:
        raise BuildError("source pin fields differ")
    movie_range = spec["movie_subtitle_range"]
    if movie_range != {"first_id": 17989, "last_id": 18240}:
        raise BuildError("movie subtitle range differs")
    entries = spec["entries"]
    if not isinstance(entries, list) or len(entries) != 8:
        raise BuildError("expected exactly eight subtitle corrections")
    ids: list[int] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "id",
            "issue",
            "preimage_utf16le_sha256",
            "ko",
        }:
            raise BuildError("correction entry fields differ")
        entry_id = entry["id"]
        text = entry["ko"]
        if not isinstance(entry_id, int) or not 17989 <= entry_id <= 18240:
            raise BuildError(f"correction id is outside the movie range: {entry_id!r}")
        if not isinstance(text, str) or not text or "\x00" in text:
            raise BuildError(f"correction {entry_id} has an invalid target")
        if text.count("\n") > 1:
            raise BuildError(f"correction {entry_id} exceeds two explicit lines")
        if any(len(line) > 40 for line in text.splitlines()):
            raise BuildError(f"correction {entry_id} has an overlong explicit line")
        if KANA.search(text):
            raise BuildError(f"correction {entry_id} contains Japanese kana")
        if any(term in text for term in FORBIDDEN_TERMS):
            raise BuildError(f"correction {entry_id} retains a rejected term")
        ids.append(entry_id)
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise BuildError("correction ids must be unique and sorted")


def load_pinned_table(input_path: Path, spec: Mapping[str, Any]) -> tuple[bytes, bytes, Any]:
    try:
        packed = input_path.read_bytes()
    except OSError as exc:
        raise BuildError(f"cannot read pinned input: {input_path}") from exc
    source = spec["source"]
    if len(packed) != source["packed_size"] or sha256_bytes(packed) != source["packed_sha256"]:
        raise BuildError("input packed resource differs from the v0.90.0 pin")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != source["raw_size"] or sha256_bytes(raw) != source["raw_sha256"]:
        raise BuildError("input raw resource differs from the v0.90.0 pin")
    table = parse_message_table(raw)
    if table.string_count != source["string_count"]:
        raise BuildError("input string count differs from the pin")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError("input message table is not byte-exact on rebuild")
    return packed, raw, table


def apply_corrections(texts: Sequence[str], entries: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    result = list(texts)
    for entry in entries:
        entry_id = entry["id"]
        if sha256_text(result[entry_id]) != entry["preimage_utf16le_sha256"]:
            raise BuildError(f"preimage mismatch at msgdata id {entry_id}")
        result[entry_id] = entry["ko"]
    return tuple(result)


def audit_candidate(
    before: Sequence[str],
    after: Sequence[str],
    spec: Mapping[str, Any],
) -> dict[str, Any]:
    expected_ids = [entry["id"] for entry in spec["entries"]]
    changed_ids = [index for index, pair in enumerate(zip(before, after)) if pair[0] != pair[1]]
    if changed_ids != expected_ids:
        raise BuildError(f"changed id vector differs: {changed_ids}")
    movie_range = spec["movie_subtitle_range"]
    first_id = movie_range["first_id"]
    last_id = movie_range["last_id"]
    movie_rows = after[first_id : last_id + 1]
    empty_ids = [first_id + index for index, text in enumerate(movie_rows) if not text]
    kana_ids = [first_id + index for index, text in enumerate(movie_rows) if KANA.search(text)]
    rejected: dict[str, list[int]] = {}
    for term in FORBIDDEN_TERMS:
        ids = [first_id + index for index, text in enumerate(movie_rows) if term in text]
        if ids:
            rejected[term] = ids
    if empty_ids or kana_ids or rejected:
        raise BuildError(
            f"movie subtitle audit failed: empty={empty_ids} kana={kana_ids} rejected={rejected}"
        )
    max_explicit_lines = max(text.count("\n") + 1 for text in movie_rows)
    max_line_chars = max(len(line) for text in movie_rows for line in text.splitlines())
    if max_explicit_lines > 2 or max_line_chars > 40:
        raise BuildError(
            f"movie subtitle layout audit failed: lines={max_explicit_lines} chars={max_line_chars}"
        )
    return {
        "range": {"first_id": first_id, "last_id": last_id, "entry_count": len(movie_rows)},
        "populated_entry_count": len(movie_rows),
        "empty_entry_count": 0,
        "kana_entry_count": 0,
        "max_explicit_lines": max_explicit_lines,
        "max_line_characters": max_line_chars,
        "changed_ids": changed_ids,
        "rejected_term_hits": 0,
    }


def build(input_path: Path, output_root: Path) -> Path:
    spec = read_spec()
    validate_spec(spec)
    packed, raw, table = load_pinned_table(input_path, spec)
    corrected = apply_corrections(table.texts, spec["entries"])
    audit = audit_candidate(table.texts, corrected, spec)
    candidate_raw = rebuild_message_table(table, corrected)
    candidate_packed = recompress_wrapper(candidate_raw, packed)
    _candidate_header, decoded = decompress_wrapper(candidate_packed)
    if decoded != candidate_raw:
        raise BuildError("candidate wrapper round-trip failed")
    candidate_table = parse_message_table(decoded)
    if candidate_table.texts != corrected:
        raise BuildError("candidate table readback differs")

    output_root = output_root.resolve()
    if output_root.exists():
        raise BuildError(f"output root already exists: {output_root}")
    staging = output_root.parent / f".{output_root.name}.{uuid.uuid4().hex}.tmp"
    staging.mkdir(parents=True)
    try:
        candidate_path = staging / RESOURCE
        candidate_path.parent.mkdir(parents=True)
        candidate_path.write_bytes(candidate_packed)
        verification = {
            "schema": EXPECTED_SCHEMA,
            "resource": RESOURCE.as_posix(),
            "source": spec["source"],
            "candidate": {
                "packed_size": len(candidate_packed),
                "packed_sha256": sha256_bytes(candidate_packed),
                "raw_size": len(candidate_raw),
                "raw_sha256": sha256_bytes(candidate_raw),
                "string_count": candidate_table.string_count,
            },
            "correction_count": len(spec["entries"]),
            "correction_ids": [entry["id"] for entry in spec["entries"]],
            "movie_subtitle_audit": audit,
            "steam_installation_written": False,
        }
        (staging / "verification.v1.json").write_text(
            json.dumps(verification, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        staging.replace(output_root)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return output_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = build(args.input, args.output_root)
    print(f"candidate={output / RESOURCE}")
    print(f"verification={output / 'verification.v1.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
