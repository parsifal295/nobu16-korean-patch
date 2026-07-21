#!/usr/bin/env python3
"""Replay the checked-in, source-free Korean-Hanja furigana operation ledger.

This tool intentionally has no in-place mode.  It accepts only the exact
Steam resource hashes recorded by the ledger and emits verified candidates
below a separate output directory.  A release step may copy those candidates
to Steam only after an explicit user request.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
DEFAULT_LEDGER = WORKSTREAM / "public" / "hanja_furigana_v0140.operations.json"
DEFAULT_OUTPUT_ROOT = WORKSTREAM / "private" / "applied_candidate"
SHA256_RE = re.compile(r"^[0-9A-F]{64}$")


def load_builder() -> Any:
    path = WORKSTREAM / "build_hanja_furigana_v0140.py"
    spec = importlib.util.spec_from_file_location("hanja_furigana_apply_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import the furigana builder helpers")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def is_nested(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise builder.FuriganaError(f"{label} is not an uppercase SHA-256")
    return value


def require_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise builder.FuriganaError(f"{label} is not a non-negative integer")
    return value


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise builder.FuriganaError(f"{label} is not an object")
    return value


def read_ledger(path: Path) -> Mapping[str, Any]:
    try:
        ledger = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise builder.FuriganaError(f"cannot read operation ledger: {path}") from exc
    ledger = require_mapping(ledger, "operation ledger")
    if ledger.get("schema") != builder.SCHEMA:
        raise builder.FuriganaError("operation ledger schema differs")
    if ledger.get("source_free") is not True:
        raise builder.FuriganaError("operation ledger is not marked source-free")
    builder.assert_source_free(ledger)
    return ledger


def parse_operations(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise builder.FuriganaError(f"{label} operations are absent")
    operations: list[Any] = []
    seen: set[int] = set()
    for position, raw in enumerate(value):
        operation = require_mapping(raw, f"{label} operation {position}")
        entry_id = require_int(operation.get("id"), f"{label} operation {position} id")
        if entry_id in seen:
            raise builder.FuriganaError(f"{label} contains duplicate operation {entry_id}")
        seen.add(entry_id)
        replacement = operation.get("replacement")
        if not isinstance(replacement, str):
            raise builder.FuriganaError(f"{label} operation {entry_id} replacement is not text")
        builder.validate_replacement(replacement, f"{label} operation {entry_id}")
        source_hash = require_hash(
            operation.get("source_utf16le_sha256"),
            f"{label} operation {entry_id} source hash",
        )
        display_hash = require_hash(
            operation.get("display_source_utf16le_sha256"),
            f"{label} operation {entry_id} display hash",
        )
        group = operation.get("group")
        if not isinstance(group, str) or not group:
            raise builder.FuriganaError(f"{label} operation {entry_id} group is invalid")
        operations.append(
            builder.Operation(
                entry_id=entry_id,
                replacement=replacement,
                source_hash=source_hash,
                display_hash=display_hash,
                group=group,
            )
        )
    return operations


def verify_source_metadata(
    packed: bytes,
    raw: bytes,
    source: Mapping[str, Any],
    label: str,
) -> None:
    expected_size = require_int(source.get("size"), f"{label} source size")
    expected_hash = require_hash(source.get("sha256"), f"{label} source hash")
    expected_raw_size = require_int(source.get("raw_size"), f"{label} source raw size")
    expected_raw_hash = require_hash(source.get("raw_sha256"), f"{label} source raw hash")
    actual = (len(packed), builder.sha256_bytes(packed), len(raw), builder.sha256_bytes(raw))
    expected = (expected_size, expected_hash, expected_raw_size, expected_raw_hash)
    if actual != expected:
        raise builder.FuriganaError(f"{label} source resource does not match the operation ledger")


def verify_target_metadata(
    packed: bytes,
    raw: bytes,
    target: Mapping[str, Any],
    label: str,
) -> None:
    expected_size = require_int(target.get("size"), f"{label} target size")
    expected_hash = require_hash(target.get("sha256"), f"{label} target hash")
    expected_raw_size = require_int(target.get("raw_size"), f"{label} target raw size")
    expected_raw_hash = require_hash(target.get("raw_sha256"), f"{label} target raw hash")
    actual = (len(packed), builder.sha256_bytes(packed), len(raw), builder.sha256_bytes(raw))
    expected = (expected_size, expected_hash, expected_raw_size, expected_raw_hash)
    if actual != expected:
        raise builder.FuriganaError(f"{label} candidate differs from the operation ledger target")


def find_resource(ledger: Mapping[str, Any], resource: str, kind: str) -> Mapping[str, Any]:
    resources = ledger.get("resources")
    if not isinstance(resources, list) or len(resources) != 2:
        raise builder.FuriganaError("operation ledger resource count differs")
    matches = [
        item
        for item in resources
        if isinstance(item, Mapping) and item.get("resource") == resource and item.get("kind") == kind
    ]
    if len(matches) != 1:
        raise builder.FuriganaError(f"operation ledger lacks the expected {resource} resource")
    return matches[0]


def apply_resource(
    steam_root: Path,
    resource_data: Mapping[str, Any],
    resource: str,
    kind: str,
) -> tuple[bytes, bytes, Sequence[str], list[Any]]:
    source = require_mapping(resource_data.get("source"), f"{resource} source")
    target = require_mapping(resource_data.get("target"), f"{resource} target")
    operations = parse_operations(resource_data.get("operations"), resource)
    operation_count = require_int(resource_data.get("operation_count"), f"{resource} operation count")
    if operation_count != len(operations):
        raise builder.FuriganaError(f"{resource} operation count differs")

    source_path = builder.safe_resource_path(steam_root, resource)
    if kind == "common_message_table":
        packed, raw, parsed = builder.parse_common(source_path)
        verify_source_metadata(packed, raw, source, resource)
        if require_int(source.get("string_count"), f"{resource} string count") != parsed.string_count:
            raise builder.FuriganaError(f"{resource} string count differs")
        if builder.compact_int_list_hash([item.entry_id for item in operations]) != builder.PK_READING_IDS_SHA256:
            raise builder.FuriganaError(f"{resource} operation scope differs")
        candidate_packed, candidate_raw, candidate = builder.apply_common_operations(packed, operations)
        builder.assert_candidate_scope(parsed.texts, candidate.texts, operations, resource)
        source_texts = parsed.texts
    elif kind == "strdata_block_zero":
        packed, raw, parsed = builder.parse_base(source_path)
        verify_source_metadata(packed, raw, source, resource)
        block_counts = source.get("block_slot_counts")
        if not isinstance(block_counts, list) or block_counts != [block.slot_count for block in parsed.blocks]:
            raise builder.FuriganaError(f"{resource} block counts differ")
        if builder.compact_int_list_hash([item.entry_id for item in operations]) != builder.BASE_READING_IDS_SHA256:
            raise builder.FuriganaError(f"{resource} operation scope differs")
        candidate_packed, candidate_raw, candidate = builder.apply_base_operations(packed, operations)
        builder.assert_candidate_scope(
            parsed.blocks[0].texts,
            candidate.blocks[0].texts,
            operations,
            f"{resource} block 0",
        )
        source_texts = parsed.blocks[0].texts
    else:
        raise builder.FuriganaError(f"unsupported operation ledger kind: {kind}")
    verify_target_metadata(candidate_packed, candidate_raw, target, resource)
    return candidate_packed, candidate_raw, source_texts, operations


def apply(args: argparse.Namespace) -> dict[str, Path | int]:
    steam_root = args.steam_root.resolve(strict=True)
    ledger_path = args.operation_ledger.resolve(strict=True)
    output_root = args.output_root.resolve()
    if output_root.exists() and not output_root.is_dir():
        raise builder.FuriganaError("output root is not a directory")
    if is_nested(output_root, steam_root):
        raise builder.FuriganaError("output root must not be within the Steam installation")

    ledger = read_ledger(ledger_path)
    pk_data = find_resource(ledger, builder.PK_RESOURCE, "common_message_table")
    base_data = find_resource(ledger, builder.BASE_RESOURCE, "strdata_block_zero")
    pk_candidate, _pk_raw, _pk_source, pk_operations = apply_resource(
        steam_root, pk_data, builder.PK_RESOURCE, "common_message_table"
    )
    base_candidate, _base_raw, _base_source, base_operations = apply_resource(
        steam_root, base_data, builder.BASE_RESOURCE, "strdata_block_zero"
    )

    pk_path = output_root / "candidate" / builder.PK_RESOURCE
    base_path = output_root / "candidate" / builder.BASE_RESOURCE
    report_path = output_root / "apply.v1.json"
    builder.atomic_write(pk_path, pk_candidate)
    builder.atomic_write(base_path, base_candidate)
    report = {
        "schema": "nobu16.kr.hanja-furigana-apply.v1",
        "source_free": True,
        "in_place_write": False,
        "steam_root_written": False,
        "operation_ledger_sha256": builder.sha256_file(ledger_path),
        "resources": [
            {
                "resource": builder.PK_RESOURCE,
                "operation_count": len(pk_operations),
                "candidate_sha256": builder.sha256_bytes(pk_candidate),
            },
            {
                "resource": builder.BASE_RESOURCE,
                "operation_count": len(base_operations),
                "candidate_sha256": builder.sha256_bytes(base_candidate),
            },
        ],
    }
    builder.assert_source_free(report)
    builder.write_json(report_path, report)
    return {
        "candidate_pk": pk_path,
        "candidate_base": base_path,
        "report": report_path,
        "pk_operations": len(pk_operations),
        "base_operations": len(base_operations),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=builder.DEFAULT_STEAM_ROOT)
    parser.add_argument("--operation-ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args(argv)


def main() -> int:
    try:
        result = apply(parse_args())
    except builder.FuriganaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for key, value in result.items():
        print(f"{key}={value}")
    print("apply=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
