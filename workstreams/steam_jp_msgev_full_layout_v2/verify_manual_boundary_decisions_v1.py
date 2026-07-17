#!/usr/bin/env python3
"""Verify the source-free v2 manual-event-boundary decision artifact.

The verifier reads the pinned Steam source and v1 audit but never writes a
message table, candidate, Steam file, release, or GitHub state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
V1_AUDIT = REPO / "workstreams" / "steam_jp_msgev_full_layout_v1" / "public" / "msgev_full_layout_audit.v1.json"
ARTIFACT = WORKSTREAM / "public" / "manual_boundary_decisions.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
SCHEMA = "nobu16.kr.steam-jp-msgev-manual-boundary-decisions.v1"

sys.path[:0] = [str(TOOLS)]

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


class VerificationError(ValueError):
    """Raised when static provenance or its pinned source differs."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise VerificationError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def file_spec(path: Path) -> dict[str, Any]:
    value = path.read_bytes()
    return {"size": len(value), "sha256": sha256(value)}


def source_table(steam_root: Path) -> tuple[Any, dict[str, Any]]:
    path = (steam_root / RESOURCE).resolve(strict=True)
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    return table, {"packed": file_spec(path), "raw_sha256": sha256(raw), "string_count": table.string_count}


def verify(steam_root: Path) -> dict[str, int]:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    audit = json.loads(V1_AUDIT.read_text(encoding="utf-8"))
    require(artifact.get("schema"), SCHEMA, "artifact schema")
    require(artifact.get("resource"), RESOURCE.as_posix(), "artifact resource")
    table, source = source_table(steam_root)
    require(artifact.get("source"), source, "artifact source profile")
    require(audit.get("source"), source, "v1 audit source profile")

    manual_by_key: dict[tuple[int, int], str] = {}
    hashes: dict[int, str] = {}
    manual_rows = 0
    korean_rows = 0
    protected_rows = 0
    for row in audit.get("rows", []):
        classification = row.get("classification")
        if classification not in {"manual_korean_boundary_review", "manual_protected_token_review"}:
            continue
        entry_id = row.get("id")
        operations = row.get("newline_operations")
        source_hash = row.get("preimage_utf16le_sha256")
        if type(entry_id) is not int or not isinstance(operations, list) or not isinstance(source_hash, str):
            raise VerificationError("v1 manual row shape is invalid")
        require(text_hash(table.texts[entry_id]), source_hash, f"manual row {entry_id} source text")
        manual_rows += 1
        if classification == "manual_korean_boundary_review":
            korean_rows += 1
        else:
            protected_rows += 1
        hashes[entry_id] = source_hash
        for ordinal, operation in enumerate(operations):
            if operation == "manual":
                manual_by_key[(entry_id, ordinal)] = source_hash

    decisions = artifact.get("decisions")
    if not isinstance(decisions, list):
        raise VerificationError("artifact decision list is invalid")
    engine = artifact.get("decision_engine")
    if not isinstance(engine, dict) or not isinstance(engine.get("version"), str):
        raise VerificationError("artifact decision engine is invalid")
    expected_keys = {
        "id",
        "lf_ordinal",
        "operation",
        "preimage_utf16le_sha256",
        "reason",
        "kiwi_relation",
        "kiwi_version",
    }
    seen: set[tuple[int, int]] = set()
    operations = Counter()
    reasons = Counter()
    by_key: dict[tuple[int, int], dict[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict) or set(decision) != expected_keys:
            raise VerificationError("a decision stores an unexpected field or source text")
        entry_id = decision["id"]
        ordinal = decision["lf_ordinal"]
        key = (entry_id, ordinal)
        if type(entry_id) is not int or type(ordinal) is not int or key in seen:
            raise VerificationError("decision coordinate is invalid or duplicated")
        if key not in manual_by_key:
            raise VerificationError(f"decision is not a v1 manual boundary: {key}")
        require(decision["preimage_utf16le_sha256"], manual_by_key[key], f"decision preimage {key}")
        if decision["operation"] not in ("space", "concat"):
            raise VerificationError(f"decision operation is invalid: {key}")
        if not isinstance(decision["reason"], str) or not decision["reason"]:
            raise VerificationError(f"decision reason is invalid: {key}")
        if decision["kiwi_relation"] not in ("space", "concat"):
            raise VerificationError(f"decision Kiwi relation is invalid: {key}")
        require(decision["kiwi_version"], engine["version"], f"decision Kiwi version {key}")
        seen.add(key)
        by_key[key] = decision
        operations[decision["operation"]] += 1
        reasons[decision["reason"]] += 1

    require(seen, set(manual_by_key), "manual LF decision coverage")
    selection = artifact.get("selection", {})
    require(selection.get("manual_korean_boundary_review_row_count"), korean_rows, "Korean-boundary row count")
    require(selection.get("manual_protected_token_review_row_count"), protected_rows, "protected-token row count")
    require(selection.get("reviewed_row_count"), manual_rows, "reviewed row count")
    require(selection.get("manual_linebreak_decision_count"), len(seen), "manual decision count")
    counts = artifact.get("counts", {})
    require(counts.get("operations"), dict(sorted(operations.items())), "operation counts")
    require(counts.get("reasons"), dict(sorted(reasons.items())), "reason counts")
    for key, operation in {
        (3203, 0): "space",
        (7047, 0): "concat",
        (7087, 0): "concat",
        (10835, 0): "space",
        (16397, 1): "concat",
    }.items():
        require(by_key[key]["operation"], operation, f"known decision {key}")
    return {
        "manual_rows": manual_rows,
        "korean_rows": korean_rows,
        "protected_rows": protected_rows,
        "decisions": len(seen),
        **dict(operations),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    args = parser.parse_args()
    try:
        report = verify(args.steam_root)
        print("status=PASS")
        print(f"manual_rows={report['manual_rows']}")
        print(f"korean_rows={report['korean_rows']}")
        print(f"protected_rows={report['protected_rows']}")
        print(f"decisions={report['decisions']}")
        print(f"space={report.get('space', 0)}")
        print(f"concat={report.get('concat', 0)}")
        print("steam_files_written=False")
        return 0
    except (VerificationError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
