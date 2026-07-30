#!/usr/bin/env python3
"""Apply two fail-closed Honnōji movie-subtitle corrections to PK msgdata.

The input must be the accepted output of ``movie_subtitle_msgdata_fix_v1``.
The builder writes only below an explicit output directory and never writes
to the Steam installation.
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


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.movie-subtitle-msgdata-honnoji-correction.v1"
RESOURCE = Path("MSG_PK/JP/msgdata.bin")
SPEC_PATH = HERE / "corrections.v1.json"
VIDEO_BLOCKS = (
    ("EV01_okehazama", 17989, 18018),
    ("EV04_honnoji", 18019, 18049),
    ("EV05_nohime", 18050, 18067),
    ("EV09_nagashino", 18068, 18090),
    ("EV10_kawanakajima", 18091, 18114),
    ("EV11_sekigahara", 18115, 18135),
    ("EV12_ueda", 18136, 18162),
    ("EV13_azai", 18163, 18187),
    ("EV14_komaki_nagakute", 18188, 18213),
    ("EV15_osaka", 18214, 18237),
)
VIDEO_IDS = tuple(
    entry_id
    for _name, first_id, last_id in VIDEO_BLOCKS
    for entry_id in range(first_id, last_id + 1)
)
KANA_RE = re.compile(r"[\u3040-\u30ff]")
EXPECTED_CANDIDATE = {
    "packed_size": 482093,
    "packed_sha256": "36AA074DCEBD5E26D3679E5468F0529A996E54DAF65188C71C96EAC11862B982",
    "raw_size": 480184,
    "raw_sha256": "A149C67EC7C165DA3CFB15BD6661A47D3C547B94555ECEB0C9DF54A44851180F",
    "string_count": 29218,
}


class BuildError(RuntimeError):
    """Raised when a pinned input, correction, or output invariant differs."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def read_spec() -> dict[str, Any]:
    try:
        value = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read correction specification: {SPEC_PATH}") from exc
    if set(value) != {"schema", "resource", "source", "entries"}:
        raise BuildError("correction specification fields differ")
    if value["schema"] != SCHEMA or value["resource"] != RESOURCE.as_posix():
        raise BuildError("correction specification target differs")
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
    entries = spec["entries"]
    if not isinstance(entries, list) or len(entries) != 2:
        raise BuildError("expected exactly two Honnōji corrections")
    expected_ids = [18025, 18032]
    if [entry.get("id") for entry in entries if isinstance(entry, dict)] != expected_ids:
        raise BuildError("Honnōji correction ID vector differs")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "id",
            "issue",
            "preimage_utf16le_sha256",
            "ko",
            "ko_utf16le_sha256",
        }:
            raise BuildError("correction entry fields differ")
        text = entry["ko"]
        if not isinstance(text, str) or not text or "\x00" in text:
            raise BuildError(f"invalid Korean target at {entry['id']}")
        if text.count("\n") or len(text) > 40:
            raise BuildError(f"target is not a single fitting subtitle line at {entry['id']}")
        if KANA_RE.search(text):
            raise BuildError(f"Japanese kana remains at {entry['id']}")
        if sha256_text(text) != entry["ko_utf16le_sha256"]:
            raise BuildError(f"Korean target hash differs at {entry['id']}")


def load_pinned_input(
    input_path: Path, spec: Mapping[str, Any]
) -> tuple[bytes, bytes, Any]:
    try:
        packed = input_path.read_bytes()
    except OSError as exc:
        raise BuildError(f"cannot read pinned input: {input_path}") from exc
    source = spec["source"]
    if (
        len(packed) != source["packed_size"]
        or sha256_bytes(packed) != source["packed_sha256"]
    ):
        raise BuildError("packed input differs from the accepted predecessor")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != source["raw_size"] or sha256_bytes(raw) != source["raw_sha256"]:
        raise BuildError("raw input differs from the accepted predecessor")
    table = parse_message_table(raw)
    if table.string_count != source["string_count"]:
        raise BuildError("input string count differs")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError("input table is not byte-exact on rebuild")
    return packed, raw, table


def apply_entries(
    texts: Sequence[str], entries: Sequence[Mapping[str, Any]]
) -> tuple[str, ...]:
    result = list(texts)
    for entry in entries:
        entry_id = entry["id"]
        if sha256_text(result[entry_id]) != entry["preimage_utf16le_sha256"]:
            raise BuildError(f"preimage mismatch at msgdata id {entry_id}")
        result[entry_id] = entry["ko"]
    return tuple(result)


def audit_texts(
    before: Sequence[str],
    after: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    expected_ids = [entry["id"] for entry in entries]
    changed_ids = [
        entry_id
        for entry_id, (old, new) in enumerate(zip(before, after))
        if old != new
    ]
    if changed_ids != expected_ids:
        raise BuildError(f"changed ID vector differs: {changed_ids}")
    video_rows = [after[entry_id] for entry_id in VIDEO_IDS]
    empty_ids = [
        entry_id for entry_id in VIDEO_IDS if not after[entry_id]
    ]
    kana_ids = [
        entry_id for entry_id in VIDEO_IDS if KANA_RE.search(after[entry_id])
    ]
    if empty_ids or kana_ids:
        raise BuildError(f"video subtitle audit failed: empty={empty_ids} kana={kana_ids}")
    max_lines = max(text.count("\n") + 1 for text in video_rows)
    max_line_chars = max(
        len(line) for text in video_rows for line in text.splitlines()
    )
    if max_lines > 2 or max_line_chars > 40:
        raise BuildError(
            f"video subtitle layout differs: lines={max_lines} chars={max_line_chars}"
        )
    return {
        "video_count": len(VIDEO_BLOCKS),
        "video_slot_count": len(VIDEO_IDS),
        "populated_slot_count": len(VIDEO_IDS),
        "empty_slot_count": 0,
        "kana_slot_count": 0,
        "max_explicit_lines": max_lines,
        "max_line_characters": max_line_chars,
        "changed_ids": changed_ids,
        "honnoji": {
            "first_id": 18019,
            "last_id": 18049,
            "slot_count": 31,
            "populated_slot_count": sum(bool(after[i]) for i in range(18019, 18050)),
        },
    }


def candidate_metrics(packed: bytes) -> dict[str, Any]:
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "string_count": table.string_count,
    }


def build(input_path: Path, output_root: Path) -> Path:
    spec = read_spec()
    validate_spec(spec)
    packed, _raw, table = load_pinned_input(input_path, spec)
    corrected = apply_entries(table.texts, spec["entries"])
    audit = audit_texts(table.texts, corrected, spec["entries"])

    candidate_raw = rebuild_message_table(table, corrected)
    candidate_packed = recompress_wrapper(candidate_raw, packed)
    _header, decoded = decompress_wrapper(candidate_packed)
    if decoded != candidate_raw:
        raise BuildError("candidate wrapper round-trip failed")
    candidate_table = parse_message_table(decoded)
    if candidate_table.texts != corrected:
        raise BuildError("candidate table readback differs")
    if candidate_packed[:8] != packed[:8]:
        raise BuildError("wrapper prefix differs")
    metrics = candidate_metrics(candidate_packed)
    if metrics != EXPECTED_CANDIDATE:
        raise BuildError(f"candidate pin differs: {metrics}")

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
            "schema": SCHEMA,
            "status": "PASS",
            "resource": RESOURCE.as_posix(),
            "source": spec["source"],
            "candidate": metrics,
            "correction_count": len(spec["entries"]),
            "correction_ids": [entry["id"] for entry in spec["entries"]],
            "movie_subtitle_audit": audit,
            "non_target_texts_preserved": True,
            "wrapper_round_trip": True,
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    destination = build(args.input, args.output_root)
    print(destination / RESOURCE)
    print(destination / "verification.v1.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
