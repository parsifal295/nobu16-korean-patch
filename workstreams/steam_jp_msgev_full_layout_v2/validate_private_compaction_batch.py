#!/usr/bin/env python3
"""Validate one private semantic-compaction response batch without writing Steam.

The private input and response live below ``tmp`` because they contain game
text.  This verifier intentionally reports coordinates and layout facts only;
it never copies the private source into a public artifact.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / "steam_jp_msgev_full_layout_v2" / "compaction_review"
V2_SCRIPT = WORKSTREAM / "build_steam_jp_msgev_full_layout_v2.py"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")


class BatchError(ValueError):
    pass


def load_v2() -> Any:
    spec = importlib.util.spec_from_file_location("private_compaction_v2", V2_SCRIPT)
    if spec is None or spec.loader is None:
        raise BatchError("cannot load v2 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BatchError(f"invalid JSON at {path.name}:{number}") from exc
        if not isinstance(row, dict):
            raise BatchError(f"object required at {path.name}:{number}")
        rows.append(row)
    return rows


def source_input_for(response: Path) -> Path:
    stem = response.stem
    if stem.startswith("protected_batch_"):
        folder = TMP_ROOT / "protected_batches"
        # The work tree may contain older, private protected-batch inputs with
        # the same ordinal.  The frozen index names the one that belongs to
        # this review run, so prefer it over a broad glob.
        index_path = TMP_ROOT / "protected_batch_index.v1.json"
        if index_path.is_file():
            try:
                index = json.loads(index_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise BatchError("protected batch index is invalid JSON") from exc
            paths = [
                TMP_ROOT / row["path"]
                for row in index.get("batches", [])
                if isinstance(row, dict)
                and isinstance(row.get("path"), str)
                and Path(row["path"]).stem.startswith(f"{stem}_ids_")
            ]
            if len(paths) == 1 and paths[0].is_file():
                return paths[0]
            if len(paths) > 1:
                raise BatchError(f"protected batch index is ambiguous for {stem}")
        pattern = f"{stem}_ids_*.jsonl"
    elif stem.startswith("batch_"):
        folder = TMP_ROOT / "batches"
        pattern = f"{stem}_ids_*.jsonl"
    else:
        raise BatchError("response name must start with batch_ or protected_batch_")
    matches = sorted(folder.glob(pattern))
    if len(matches) != 1:
        raise BatchError(f"cannot uniquely resolve private input for {response.name}")
    return matches[0]


def validate(response: Path, steam_root: Path) -> dict[str, int]:
    if not response.is_file():
        raise BatchError(f"response is absent: {response}")
    source_input = source_input_for(response)
    expected = read_jsonl(source_input)
    actual = read_jsonl(response)
    expected_ids = [row.get("id") for row in expected]
    seen: set[int] = set()
    answers: dict[int, str] = {}
    for row in actual:
        entry_id = row.get("id")
        target = row.get("ko")
        if type(entry_id) is not int or not isinstance(target, str) or entry_id in seen:
            raise BatchError("response must contain unique integer id and Korean text rows")
        seen.add(entry_id)
        answers[entry_id] = target
    if set(expected_ids) != set(answers) or len(expected_ids) != len(answers):
        missing = sorted(set(expected_ids) - set(answers))
        extra = sorted(set(answers) - set(expected_ids))
        raise BatchError(f"ID coverage differs: missing={missing}, extra={extra}")

    v2 = load_v2()
    _path, _packed, _raw, table = v2.source_table(steam_root)
    advance, _font = v2.current_font(steam_root)
    reservations, _excluded, _document = v2.load_reservations()
    problems: list[str] = []
    for entry_id in expected_ids:
        source = table.texts[entry_id]
        target = answers[entry_id]
        if v2.protected_signature(target) != v2.protected_signature(source):
            problems.append(f"{entry_id}:locked_token_signature")
            continue
        if target != target.strip(" \r\n"):
            problems.append(f"{entry_id}:external_layout_whitespace")
            continue
        result = v2.reflow_manual_text(
            target,
            len(v2.base.visual_line_widths(source, advance)),
            advance,
            reservations,
        )
        if result is None:
            problems.append(f"{entry_id}:cannot_fit_three_lines")
            continue
        _rendered, layout = result
        if len(layout.reserved_widths) > v2.MAX_LINES or max(layout.reserved_widths) > v2.MAX_LINE_PX:
            problems.append(f"{entry_id}:layout_exceeds_budget")
    if problems:
        raise BatchError("batch checks failed: " + ", ".join(problems))
    return {"entries": len(expected_ids)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--translation", required=True, type=Path)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    args = parser.parse_args()
    try:
        report = validate(args.translation, args.steam_root)
        print("status=PASS")
        print(f"entries={report['entries']}")
        print("steam_files_written=False")
        return 0
    except (BatchError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
