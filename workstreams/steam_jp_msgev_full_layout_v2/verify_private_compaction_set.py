#!/usr/bin/env python3
"""Verify complete private semantic-compaction coverage in one source pass.

Private batch files contain game text and remain under ``tmp``.  This command
only prints counts and coordinates; it never writes Steam, public assets, or
private source text.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PRIVATE_ROOT = REPO / "tmp" / "steam_jp_msgev_full_layout_v2" / "compaction_review"
TRANSLATIONS = PRIVATE_ROOT / "translations"
V2_SCRIPT = WORKSTREAM / "build_steam_jp_msgev_full_layout_v2.py"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")


class SetError(ValueError):
    pass


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SetError(f"cannot read {path.name}") from exc
    if not isinstance(result, dict):
        raise SetError(f"object required: {path.name}")
    return result


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise SetError(f"cannot read {path}") from exc
    result: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SetError(f"invalid JSON at {path.name}:{number}") from exc
        if not isinstance(row, dict):
            raise SetError(f"object required at {path.name}:{number}")
        result.append(row)
    return result


def load_v2() -> Any:
    spec = importlib.util.spec_from_file_location("verify_private_set_v2", V2_SCRIPT)
    if spec is None or spec.loader is None:
        raise SetError("cannot load v2 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expected_batches() -> list[tuple[Path, Path]]:
    result: list[tuple[Path, Path]] = []
    normal = load_json(PRIVATE_ROOT / "batch_index.v1.json")
    for row in normal.get("batches", []):
        if not isinstance(row, dict) or type(row.get("ordinal")) is not int or not isinstance(row.get("relative_path"), str):
            raise SetError("normal batch index row is invalid")
        ordinal = row["ordinal"]
        result.append((PRIVATE_ROOT / row["relative_path"], TRANSLATIONS / f"batch_{ordinal:03d}.jsonl"))
    protected = load_json(PRIVATE_ROOT / "protected_batch_index.v1.json")
    for row in protected.get("batches", []):
        if not isinstance(row, dict) or type(row.get("ordinal")) is not int or not isinstance(row.get("path"), str):
            raise SetError("protected batch index row is invalid")
        ordinal = row["ordinal"]
        result.append((PRIVATE_ROOT / row["path"], TRANSLATIONS / f"protected_batch_{ordinal:03d}.jsonl"))
    if not result:
        raise SetError("no expected private batches")
    return result


def verify(steam_root: Path) -> dict[str, int]:
    batches = expected_batches()
    v2 = load_v2()
    _source, _packed, _raw, table = v2.source_table(steam_root)
    advance, _font = v2.current_font(steam_root)
    reservations, _excluded, _document = v2.load_reservations()
    all_expected: set[int] = set()
    all_answers: set[int] = set()
    max_reserved = 0
    for source_path, response_path in batches:
        source_rows = read_jsonl(source_path)
        answer_rows = read_jsonl(response_path)
        expected: dict[int, dict[str, Any]] = {}
        answers: dict[int, str] = {}
        for row in source_rows:
            entry_id = row.get("id")
            if type(entry_id) is not int or entry_id in expected:
                raise SetError(f"invalid source batch IDs: {source_path.name}")
            expected[entry_id] = row
        for row in answer_rows:
            entry_id, target = row.get("id"), row.get("ko")
            if type(entry_id) is not int or not isinstance(target, str) or entry_id in answers:
                raise SetError(f"invalid answer batch rows: {response_path.name}")
            answers[entry_id] = target
        if set(expected) != set(answers):
            raise SetError(f"response coverage differs: {response_path.name}")
        if all_expected.intersection(expected):
            raise SetError(f"duplicate expected ID across batches: {source_path.name}")
        if all_answers.intersection(answers):
            raise SetError(f"duplicate translated ID across batches: {response_path.name}")
        all_expected.update(expected)
        all_answers.update(answers)
        for entry_id, record in expected.items():
            if not 0 <= entry_id < table.string_count:
                raise SetError(f"ID is outside Steam table: {entry_id}")
            source = table.texts[entry_id]
            if record.get("ko_source_utf16le_sha256") != text_hash(source):
                raise SetError(f"private source preimage differs: {entry_id}")
            target = answers[entry_id]
            if v2.protected_signature(target) != v2.protected_signature(source):
                raise SetError(f"locked token signature differs: {entry_id}")
            layout_result = v2.reflow_manual_text(
                target,
                len(v2.base.visual_line_widths(source, advance)),
                advance,
                reservations,
            )
            if layout_result is None:
                raise SetError(f"target cannot fit the three-line budget: {entry_id}")
            _rendered, layout = layout_result
            if len(layout.reserved_widths) > v2.MAX_LINES or max(layout.reserved_widths) > v2.MAX_LINE_PX:
                raise SetError(f"target layout exceeds budget: {entry_id}")
            max_reserved = max(max_reserved, max(layout.reserved_widths))
    expected_files = {response.resolve() for _source, response in batches}
    actual_files = {path.resolve() for path in TRANSLATIONS.glob("*.jsonl")}
    if actual_files != expected_files:
        raise SetError("translation file set differs from the private batch index")
    return {"batches": len(batches), "entries": len(all_expected), "max_reserved_px": max_reserved}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    args = parser.parse_args()
    try:
        report = verify(args.steam_root)
        print("status=PASS")
        print(f"batches={report['batches']}")
        print(f"entries={report['entries']}")
        print(f"max_reserved_px={report['max_reserved_px']}")
        print("steam_files_written=False")
        return 0
    except (SetError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
