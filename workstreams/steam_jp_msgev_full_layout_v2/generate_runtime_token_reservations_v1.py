#!/usr/bin/env python3
"""Freeze worst-case runtime-name widths for every unresolved event layout row.

The output deliberately stores IDs, hashes, and widths only.  It never stores
the commercial event or officer-name text used to calculate those values.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
V1_SCRIPT = REPO / "workstreams" / "steam_jp_msgev_full_layout_v1" / "build_steam_jp_msgev_full_layout_v1.py"
V1_AUDIT = REPO / "workstreams" / "steam_jp_msgev_full_layout_v1" / "public" / "msgev_full_layout_audit.v1.json"
OUTPUT = WORKSTREAM / "public" / "runtime_token_reservations.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
RESOURCE = "MSG_PK/JP/msgev.bin"
TOKEN_RE = re.compile(r"\[([a-z]+)(\d+)\]")
REVIEW_CLASSES = frozenset(
    {"manual_korean_boundary_review", "manual_compaction_required", "manual_protected_token_review"}
)
SCHEMA = "nobu16.kr.steam-jp-msgev-runtime-token-reservations.v1"


class ReservationError(ValueError):
    pass


def load_v1() -> Any:
    spec = importlib.util.spec_from_file_location("runtime_reservation_v1", V1_SCRIPT)
    if spec is None or spec.loader is None:
        raise ReservationError("cannot load v1 layout support")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_v1()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def file_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ReservationError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def reviewed_rows(audit: dict[str, Any]) -> Iterable[dict[str, Any]]:
    rows = audit.get("rows")
    if not isinstance(rows, list):
        raise ReservationError("v1 audit rows are absent")
    for row in rows:
        if not isinstance(row, dict):
            raise ReservationError("v1 audit row is invalid")
        if row.get("classification") in REVIEW_CLASSES:
            yield row


def generate(steam_root: Path) -> dict[str, Any]:
    audit = json.loads(V1_AUDIT.read_text(encoding="utf-8"))
    if audit.get("schema") != "nobu16.kr.steam-jp-msgev-full-layout-audit.v1":
        raise ReservationError("v1 audit schema differs")
    source_path, packed, raw, table = base.source_table(steam_root)
    source = {"packed": file_spec(source_path), "raw_sha256": sha256(raw), "string_count": table.string_count}
    require(audit.get("source"), source, "v1 source profile")
    advance, font = base.font_advance_function(steam_root)

    token_counts: Counter[str] = Counter()
    token_rows = 0
    class_rows: Counter[str] = Counter()
    reviewed_count = 0
    for row in reviewed_rows(audit):
        entry_id = row.get("id")
        source_hash = row.get("preimage_utf16le_sha256")
        classification = row.get("classification")
        if type(entry_id) is not int or not isinstance(source_hash, str) or not isinstance(classification, str):
            raise ReservationError("review row shape differs")
        if not 0 <= entry_id < table.string_count:
            raise ReservationError(f"review row is outside table: {entry_id}")
        value = table.texts[entry_id]
        require(text_hash(value), source_hash, f"review row source {entry_id}")
        reviewed_count += 1
        tokens = TOKEN_RE.findall(value)
        if tokens:
            token_rows += 1
            class_rows[classification] += 1
            token_counts.update(f"[{prefix}{suffix}]" for prefix, suffix in tokens)

    reservations: dict[str, dict[str, Any]] = {}
    for token in sorted(token_counts):
        match = TOKEN_RE.fullmatch(token)
        if match is None:
            raise ReservationError(f"token parse differs: {token}")
        prefix, suffix = match.groups()
        name_id = int(suffix)
        if not 0 <= name_id < table.string_count:
            raise ReservationError(f"token name ID outside table: {token}")
        full_name = table.texts[name_id]
        width = base.visual_line_width(full_name, advance)
        if width <= 0:
            raise ReservationError(f"token has no visible full-name width: {token}")
        reservations[token] = {
            "occurrence_count": token_counts[token],
            "prefix": prefix,
            "reserved_full_name_width_px": width,
            "source_name_id": name_id,
            "source_name_utf16le_sha256": text_hash(full_name),
        }

    prefix_counts = Counter(value["prefix"] for value in reservations.values())
    return {
        "schema": SCHEMA,
        "resource": RESOURCE,
        "source": source,
        "font": {
            "resource": "RES_JP/res_lang.bin",
            "outer_entry": 6,
            "table": 0,
            "packed": font,
            "wide_script_advance_px": advance("가"),
            "ascii_space_advance_px": advance(" "),
        },
        "selection": {
            "v1_audit_relative_path": "workstreams/steam_jp_msgev_full_layout_v1/public/msgev_full_layout_audit.v1.json",
            "review_classifications": sorted(REVIEW_CLASSES),
            "reviewed_event_row_count": reviewed_count,
        },
        "reservation_policy": {
            "method": "per-token referenced full-name upper bound",
            "name_lookup": "numeric suffix selects the same ID in MSG_PK/JP/msgev.bin",
            "runtime_prefix_semantics": "not assumed; every prefix reserves the entire referenced name",
            "runtime_token_regex": TOKEN_RE.pattern,
            "token_and_name_text_included": False,
            "width_measurement": "actual event font table 0 advance",
        },
        "excluded_protected_rows": [
            {
                "id": 16402,
                "reason": "printf substitution width is runtime-dependent and has no officer-name reservation",
            }
        ],
        "counts": {
            "reviewed_runtime_token_rows": token_rows,
            "runtime_token_occurrences": sum(token_counts.values()),
            "unique_runtime_token_spellings": len(reservations),
            "unique_referenced_name_ids": len({item["source_name_id"] for item in reservations.values()}),
            "prefix_spellings": dict(sorted(prefix_counts.items())),
            "runtime_rows_by_v1_classification": dict(sorted(class_rows.items())),
        },
        "reservations": reservations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        output = args.output.resolve(strict=False)
        if output != OUTPUT.resolve(strict=False):
            raise ReservationError("output must be the v2 public reservation artifact")
        document = generate(args.steam_root)
        atomic_write(output, canonical_json(document))
        print("status=PASS")
        print(f"reservations={document['counts']['unique_runtime_token_spellings']}")
        print(f"reviewed_token_rows={document['counts']['reviewed_runtime_token_rows']}")
        print("steam_files_written=False")
        return 0
    except (ReservationError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
