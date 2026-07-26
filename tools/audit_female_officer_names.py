#!/usr/bin/env python3
"""Statically audit Korean full names for the complete hime-officer roster.

The game renders full officer names through the ``msgev`` table.  This tool
checks all 21 rows in the game's hime-officer roster against the published
source-text-free release recipe, then writes a source-text-free audit report.

It is deliberately read-only with respect to the game root.  The report must
be written outside that root, so this tool cannot be used to modify an
installed game by accident.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


SCHEMA = "nobu16.kr.female-officer-name-audit.v1"
RESOURCE = Path("MSG_PK") / "{language}" / "msgev.bin"
EXPECTED_STRING_COUNT = 17_916
HISTORICAL_OFFICER_MAX_ID = 2_206
KOREAN_NAME = re.compile(r"^[가-힣]+(?: [가-힣]+)*$")

# The explicit hime-officer roster.  Keep this source-free: Korean output and
# numeric IDs are public patch data; original game strings are checked only by
# their UTF-16LE SHA-256 digest from the release recipe.
TARGETS: tuple[tuple[int, str], ...] = (
    (404, "오이치"),
    (410, "오바이인"),
    (406, "오센"),
    (692, "가라샤"),
    (719, "기쿠히메"),
    (715, "기초"),
    (1016, "산조노카타"),
    (1094, "조케이인"),
    (1157, "스와히메"),
    (1170, "세나히메"),
    (1176, "센토인"),
    (1179, "조슌인"),
    (1310, "차차"),
    (1390, "도쿠히메"),
    (1391, "도쿠히메"),
    (1582, "네 네"),
    (1583, "네네"),
    (1827, "마츠"),
    (1969, "묘큐"),
    (2147, "요시히메"),
    (2177, "레이쇼인"),
)


class AuditError(RuntimeError):
    """Raised when a static audit invariant does not hold."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_utf16le(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def read_table(path: Path) -> tuple[tuple[str, ...], dict[str, Any]]:
    blob = path.read_bytes()
    header, raw = decompress_wrapper(blob)
    table = parse_message_table(raw)
    return table.texts, {
        "relative_path": path.parts[-3] + "/" + path.parts[-2] + "/" + path.parts[-1],
        "wrapped_sha256": sha256_bytes(blob),
        "wrapped_size": len(blob),
        "raw_sha256": sha256_bytes(raw),
        "raw_size": len(raw),
        "string_count": table.string_count,
        "wrapper_uncompressed_size": header.uncompressed_size,
    }


def load_recipe_operations(path: Path) -> dict[int, dict[str, str]]:
    try:
        recipe = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot read release recipe {path}: {exc}") from exc

    if recipe.get("schema") != "nobu16.file-only-msg-recipe.v1":
        raise AuditError("release recipe schema is not a common-message file-only recipe")
    if recipe.get("language") != "SC":
        raise AuditError("release recipe must be based on the SC msgev resource")
    if recipe.get("source", {}).get("relative_path") != "MSG_PK/SC/msgev.bin":
        raise AuditError("release recipe is not for MSG_PK/SC/msgev.bin")

    result: dict[int, dict[str, str]] = {}
    for number, operation in enumerate(recipe.get("operations", []), 1):
        if set(operation) != {"id", "replacement", "source_utf16le_sha256"}:
            raise AuditError(f"recipe operation {number} has an unexpected schema")
        entry_id = operation["id"]
        replacement = operation["replacement"]
        source_hash = operation["source_utf16le_sha256"]
        if not isinstance(entry_id, int) or entry_id < 0:
            raise AuditError(f"recipe operation {number} has an invalid id")
        if not isinstance(replacement, str) or not isinstance(source_hash, str):
            raise AuditError(f"recipe operation {number} has an invalid payload")
        if entry_id in result:
            raise AuditError(f"recipe contains duplicate id {entry_id}")
        result[entry_id] = {
            "replacement": replacement,
            "source_utf16le_sha256": source_hash.upper(),
        }
    return result


def ensure_report_is_outside_game(report: Path, game_root: Path) -> None:
    try:
        report.resolve().relative_to(game_root.resolve())
    except ValueError:
        return
    raise AuditError("report path must be outside the game root")


def atomic_json_write(path: Path, document: dict[str, Any]) -> None:
    payload = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def audit(game_root: Path, recipe_path: Path) -> dict[str, Any]:
    target_ids = [entry_id for entry_id, _ in TARGETS]
    if len(set(target_ids)) != len(target_ids):
        raise AuditError("target roster has duplicate IDs")
    if any(entry_id > HISTORICAL_OFFICER_MAX_ID for entry_id in target_ids):
        raise AuditError("target roster contains a non-historical officer ID")

    recipe_operations = load_recipe_operations(recipe_path)
    tables: dict[str, tuple[str, ...]] = {}
    table_reports: dict[str, dict[str, Any]] = {}
    for language in ("SC", "JP", "EN"):
        path = game_root / Path(str(RESOURCE).format(language=language))
        texts, info = read_table(path)
        if len(texts) != EXPECTED_STRING_COUNT:
            raise AuditError(
                f"{language} msgev has {len(texts)} strings, expected {EXPECTED_STRING_COUNT}"
            )
        tables[language] = texts
        table_reports[language] = info

    rows: list[dict[str, Any]] = []
    for entry_id, expected_korean in TARGETS:
        if entry_id >= len(tables["SC"]):
            raise AuditError(f"target id {entry_id} is outside msgev")
        operation = recipe_operations.get(entry_id)
        if operation is None:
            raise AuditError(f"target id {entry_id} is missing from the published msgev recipe")
        if operation["replacement"] != expected_korean:
            raise AuditError(f"target id {entry_id} recipe output does not match the roster")
        source_hash = sha256_utf16le(tables["SC"][entry_id])
        if source_hash != operation["source_utf16le_sha256"]:
            raise AuditError(f"target id {entry_id} SC source hash does not match the release recipe")
        actual_korean = tables["JP"][entry_id]
        if actual_korean != expected_korean:
            raise AuditError(f"target id {entry_id} JP display is {actual_korean!r}, expected {expected_korean!r}")
        if not KOREAN_NAME.fullmatch(actual_korean):
            raise AuditError(f"target id {entry_id} is not a Hangul-only display name")
        rows.append(
            {
                "id": entry_id,
                "ko": actual_korean,
                "ko_utf16le_sha256": sha256_utf16le(actual_korean),
                "source_sc_utf16le_sha256": source_hash,
                "rendering_route": "msgev_direct",
            }
        )

    duplicated_korean: dict[str, list[int]] = {}
    for row in rows:
        duplicated_korean.setdefault(str(row["ko"]), []).append(int(row["id"]))
    collisions = [
        {"ko": name, "ids": ids, "identity_key": "msgev_id"}
        for name, ids in duplicated_korean.items()
        if len(ids) > 1
    ]
    if collisions != [{"ko": "도쿠히메", "ids": [1390, 1391], "identity_key": "msgev_id"}]:
        raise AuditError("unexpected Korean-name collision in the target roster")

    return {
        "schema": SCHEMA,
        "scope": {
            "classification": "hime_officer_roster",
            "roster_count": len(rows),
            "historical_officer_id_range": [0, HISTORICAL_OFFICER_MAX_ID],
            "audited_rendering_route": "MSG_PK/*/msgev.bin",
        },
        "source_text_policy": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "source_text_is_stored_as_hash_only": True,
        },
        "input_tables": table_reports,
        "rows": rows,
        "special_cases": {
            "same_korean_display_requires_id": collisions,
            "spacing_is_intentional": [{"id": 1582, "ko": "네 네"}],
        },
        "result": {"status": "PASS", "audited": len(rows), "failed": 0},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument(
        "--recipe",
        type=Path,
        default=REPOSITORY_ROOT / "workstreams" / "officer_names" / "full_v0.1" / "public" / "msgev_sc.recipe.json",
        help="source-text-free published msgev release recipe",
    )
    parser.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        game_root = args.game_root.resolve()
        report = args.report.resolve()
        ensure_report_is_outside_game(report, game_root)
        document = audit(game_root, args.recipe.resolve())
        atomic_json_write(report, document)
    except (OSError, AuditError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"report={report}")
    print(f"audited={document['result']['audited']}")
    print("result=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
