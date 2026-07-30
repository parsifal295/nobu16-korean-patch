#!/usr/bin/env python3
"""Build a private Base inventory for generic-carrier remediation review."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILDER_PATH = WORKSTREAM / "base_build_runtime_surface_remediation_v1.py"
DEFAULT_OVERLAY = WORKSTREAM / "base_bulk.overlay.v1.json"
DEFAULT_OUTPUT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "generic_target_inventory.private.v1.json"
)
PRISTINE_JP = (
    REPO
    / "tmp"
    / "v090_dialogue_subtitle_integration_v1"
    / "stock"
    / "MSG"
    / "JP"
    / "msggame.bin"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


B = load_module("base_runtime_surface_builder_for_inventory", BUILDER_PATH)


def build_inventory(overlay_path: Path) -> dict[str, Any]:
    source_blob = B.SOURCE_BASE.read_bytes()
    priority = B.load_priority_replacements(source_blob)
    predecessor_blob = B.rebuild_packed_with_literals(source_blob, priority)
    source_records = B.records_from_blob(predecessor_blob)
    jp_records = B.records_from_blob(PRISTINE_JP.read_bytes())
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for entry in overlay["entries"]:
        coordinate = (
            int(entry["block_id"]),
            int(entry["record_id"]),
            int(entry["literal_id"]),
        )
        record_coordinate = coordinate[:2]
        source_literals = [
            value.text
            for value in B.parse_record_literals(source_records[record_coordinate])
        ]
        source_literal = source_literals[coordinate[2]]
        if (
            entry["ko"].count("대상")
            <= source_literal.count("대상")
        ):
            continue
        jp_literals = [
            value.text
            for value in B.parse_record_literals(jp_records[record_coordinate])
        ]
        selector, call = B.literal_context(
            source_records[record_coordinate],
            coordinate[2],
        )
        rows.append(
            {
                "coordinate": ":".join(str(value) for value in coordinate),
                "source_literal": source_literal,
                "replacement_literal": entry["ko"],
                "source_record_literals": source_literals,
                "pristine_jp_record_literals": jp_literals,
                "selector": selector,
                "call": call,
                "methods": entry["base_remediation_evidence"]["methods"],
            }
        )
    return {
        "schema": "nobu16.kr.base-generic-carrier-inventory.private.v1",
        "row_count": len(rows),
        "rows": rows,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_inventory(args.overlay)
    B.atomic_write(args.output, B.canonical_json(payload))
    print(
        json.dumps(
            {
                "output": str(args.output),
                "row_count": payload["row_count"],
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
