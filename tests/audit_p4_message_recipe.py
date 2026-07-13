#!/usr/bin/env python3
"""Strict, read-only audit for a public P4 msgui file recipe.

The audit accepts only the documented recipe shape, cross-checks it against an
independently produced catalog-v2 build manifest, and reconstructs the target
from a SHA-gated stock SC msgui entirely in memory.  It never writes a game
resource and never modifies the input recipe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_file_only_msg_recipe import apply_operations  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


HEX64 = re.compile(r"[0-9A-F]{64}\Z")
TOP_KEYS = {
    "schema",
    "scope",
    "version",
    "language",
    "file_only",
    "source",
    "target",
    "operations",
    "operation_index",
    "payload_policy",
    "export_verification",
}
SOURCE_KEYS = {"relative_path", "size", "sha256", "raw_size", "raw_sha256", "string_count"}
TARGET_KEYS = {"size", "sha256", "raw_size", "raw_sha256"}
OPERATION_KEYS = {"id", "source_utf16le_sha256", "replacement"}
INDEX_KEYS = {"count", "id_encoding", "ids_sha256", "sorted_unique"}
POLICY_KEYS = {
    "contains_complete_source",
    "contains_complete_target",
    "contains_executable_bytes",
    "source_text_is_stored_as_hash_only",
    "stock_file_is_required_at_apply_time",
    "development_catalog_included",
}
VERIFICATION_KEYS = {
    "byte_identical_to_pinned_target",
    "table_parse_roundtrip",
    "wrapper_decompress_roundtrip",
    "build_manifest_sha256",
}
FORBIDDEN_KEYS = {
    "source_text",
    "source_en",
    "source_jp",
    "source_sc",
    "source_tc",
    "development_catalog",
    "catalog_rows",
    "complete_source",
    "complete_target",
    "payload_b64",
    "payload_base64",
}


class AuditError(ValueError):
    pass


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def strict_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        if not isinstance(key, str):
            raise AuditError("JSON object key is not a string")
        normalized = key.casefold()
        if normalized in folded:
            raise AuditError(f"duplicate or case-colliding JSON key: {key!r} / {folded[normalized]!r}")
        folded[normalized] = key
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid UTF-8 JSON in {path}: {exc}") from exc


def exact_keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise AuditError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise AuditError(
            f"{label} keys differ: missing={sorted(expected - actual)!r}, "
            f"extra={sorted(actual - expected)!r}"
        )


def require_bool(value: Any, expected: bool, label: str) -> None:
    if type(value) is not bool or value is not expected:
        raise AuditError(f"{label} must be JSON {str(expected).lower()}")


def require_int(value: Any, expected: int | None, label: str) -> int:
    if type(value) is not int or value < 0:
        raise AuditError(f"{label} must be a non-negative JSON integer")
    if expected is not None and value != expected:
        raise AuditError(f"{label} is {value}, expected {expected}")
    return value


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise AuditError(f"{label} must be an uppercase SHA-256")
    return value


def walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def audit(args: argparse.Namespace) -> dict[str, Any]:
    recipe_path = args.recipe.resolve()
    manifest_path = args.build_manifest.resolve()
    stock_path = args.stock.resolve()
    target_path = args.target.resolve()

    recipe = load_json_strict(recipe_path)
    manifest = load_json_strict(manifest_path)
    exact_keys(recipe, TOP_KEYS, "recipe")
    exact_keys(recipe["source"], SOURCE_KEYS, "recipe.source")
    exact_keys(recipe["target"], TARGET_KEYS, "recipe.target")
    exact_keys(recipe["operation_index"], INDEX_KEYS, "recipe.operation_index")
    exact_keys(recipe["payload_policy"], POLICY_KEYS, "recipe.payload_policy")
    exact_keys(recipe["export_verification"], VERIFICATION_KEYS, "recipe.export_verification")

    forbidden = sorted({key for key in walk_keys(recipe) if key.casefold() in FORBIDDEN_KEYS})
    if forbidden:
        raise AuditError(f"recipe contains forbidden source/payload fields: {forbidden!r}")

    if recipe["schema"] != "nobu16.file-only-msg-recipe.v1":
        raise AuditError("unexpected recipe schema")
    if recipe["scope"] != "msgui_catalog_v2" or recipe["language"] != "SC":
        raise AuditError("recipe scope/language mismatch")
    require_bool(recipe["file_only"], True, "recipe.file_only")

    policy = recipe["payload_policy"]
    require_bool(policy["contains_complete_source"], False, "contains_complete_source")
    require_bool(policy["contains_complete_target"], False, "contains_complete_target")
    require_bool(policy["contains_executable_bytes"], False, "contains_executable_bytes")
    require_bool(policy["source_text_is_stored_as_hash_only"], True, "source_text_is_stored_as_hash_only")
    require_bool(policy["stock_file_is_required_at_apply_time"], True, "stock_file_is_required_at_apply_time")
    require_bool(policy["development_catalog_included"], False, "development_catalog_included")

    verification = recipe["export_verification"]
    require_bool(verification["byte_identical_to_pinned_target"], True, "byte_identical_to_pinned_target")
    require_bool(verification["table_parse_roundtrip"], True, "table_parse_roundtrip")
    require_bool(verification["wrapper_decompress_roundtrip"], True, "wrapper_decompress_roundtrip")
    if require_hash(verification["build_manifest_sha256"], "build_manifest_sha256") != sha256_file(manifest_path):
        raise AuditError("recipe does not pin the supplied build manifest")

    stock_before = stock_path.read_bytes()
    target = target_path.read_bytes()
    _, stock_raw = decompress_wrapper(stock_before)
    source = recipe["source"]
    target_spec = recipe["target"]
    if source["relative_path"] != "MSG_PK/SC/msgui.bin":
        raise AuditError("recipe source path is not the official SC backend")
    if require_int(source["size"], len(stock_before), "source.size") != len(stock_before):
        raise AssertionError("unreachable")
    if require_hash(source["sha256"], "source.sha256") != sha256_bytes(stock_before):
        raise AuditError("stock SHA-256 mismatch")
    require_int(source["raw_size"], len(stock_raw), "source.raw_size")
    if require_hash(source["raw_sha256"], "source.raw_sha256") != sha256_bytes(stock_raw):
        raise AuditError("stock raw SHA-256 mismatch")
    string_count = require_int(source["string_count"], 5100, "source.string_count")

    require_int(target_spec["size"], len(target), "target.size")
    expected_target_hash = args.expected_target_sha256.upper()
    if require_hash(target_spec["sha256"], "target.sha256") != expected_target_hash:
        raise AuditError("recipe target SHA-256 differs from the expected P4 target")
    if sha256_bytes(target) != expected_target_hash:
        raise AuditError("supplied target bytes differ from the expected P4 target")
    require_int(target_spec["raw_size"], args.expected_raw_size, "target.raw_size")
    if require_hash(target_spec["raw_sha256"], "target.raw_sha256") != args.expected_raw_sha256.upper():
        raise AuditError("recipe raw target SHA-256 differs from the expected P4 target")

    operations = recipe["operations"]
    if not isinstance(operations, list):
        raise AuditError("recipe.operations must be an array")
    require_int(len(operations), args.expected_operations, "operation count")
    manifest_changed = manifest.get("changed")
    if not isinstance(manifest_changed, list) or len(manifest_changed) != len(operations):
        raise AuditError("build manifest changed list does not match operation count")

    ids: list[int] = []
    operation_projection: list[dict[str, Any]] = []
    for index, (operation, changed) in enumerate(zip(operations, manifest_changed)):
        exact_keys(operation, OPERATION_KEYS, f"operations[{index}]")
        entry_id = require_int(operation["id"], None, f"operations[{index}].id")
        if entry_id >= string_count:
            raise AuditError(f"operation id is outside msgui: {entry_id}")
        source_hash = require_hash(operation["source_utf16le_sha256"], f"operations[{index}].source hash")
        replacement = operation["replacement"]
        if not isinstance(replacement, str) or not replacement or "\x00" in replacement:
            raise AuditError(f"operations[{index}].replacement is invalid")
        if len(replacement) > 2048:
            raise AuditError(f"operations[{index}].replacement is implausibly large")
        projection = {
            "id": int(changed["id"]),
            "source_utf16le_sha256": str(changed["source_utf16le_sha256"]).upper(),
            "replacement": changed["replacement"],
        }
        if operation != projection:
            raise AuditError(f"operation {entry_id} differs from the independently built manifest")
        ids.append(entry_id)
        operation_projection.append(projection)

    if ids != sorted(set(ids)):
        raise AuditError("operation ids are not sorted and unique")
    ids_blob = json.dumps(ids, separators=(",", ":")).encode("utf-8")
    index = recipe["operation_index"]
    require_int(index["count"], len(ids), "operation_index.count")
    if index["id_encoding"] != "UTF-8 compact JSON integer array":
        raise AuditError("operation id encoding mismatch")
    if require_hash(index["ids_sha256"], "operation_index.ids_sha256") != sha256_bytes(ids_blob):
        raise AuditError("operation id hash mismatch")
    require_bool(index["sorted_unique"], True, "operation_index.sorted_unique")

    rebuilt, rebuilt_raw = apply_operations(stock_before, operations, string_count)
    if rebuilt != target:
        raise AuditError("stock reconstruction is not byte-identical to the supplied P4 target")
    if len(rebuilt_raw) != args.expected_raw_size or sha256_bytes(rebuilt_raw) != args.expected_raw_sha256.upper():
        raise AuditError("reconstructed raw target differs from the expected P4 raw target")
    if sha256_file(stock_path) != sha256_bytes(stock_before):
        raise AuditError("stock input changed during the read-only audit")

    recipe_blob = recipe_path.read_bytes()
    if recipe_blob in (stock_before, target):
        raise AuditError("recipe is a complete commercial resource")
    if recipe_blob.startswith((b"LINK", b"PK\x03\x04", b"MZ")):
        raise AuditError("recipe has a forbidden binary/archive magic")

    return {
        "schema": "nobu16.p4-message-recipe-independent-audit.v1",
        "passed": True,
        "inputs": {
            "recipe": str(recipe_path),
            "recipe_size": len(recipe_blob),
            "recipe_sha256": sha256_bytes(recipe_blob),
            "build_manifest": str(manifest_path),
            "build_manifest_sha256": sha256_file(manifest_path),
            "stock": str(stock_path),
            "stock_sha256": sha256_bytes(stock_before),
            "target": str(target_path),
            "target_sha256": sha256_bytes(target),
        },
        "checks": {
            "strict_recursive_duplicate_key_rejection": True,
            "strict_exact_schema": True,
            "forbidden_source_or_payload_fields_absent": True,
            "development_catalog_absent": True,
            "only_source_hashes_and_replacements": True,
            "operation_projection_matches_independent_manifest": True,
            "operation_ids_sorted_unique": True,
            "stock_reconstruction_byte_exact": True,
            "raw_reconstruction_byte_exact": True,
            "stock_input_unchanged": True,
            "complete_commercial_resource_absent": True,
        },
        "artifacts": {
            "operations": len(operations),
            "operation_ids_sha256": sha256_bytes(ids_blob),
            "target_size": len(target),
            "target_sha256": sha256_bytes(target),
            "raw_target_size": len(rebuilt_raw),
            "raw_target_sha256": sha256_bytes(rebuilt_raw),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--build-manifest", type=Path, required=True)
    parser.add_argument("--stock", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-operations", type=int, default=931)
    parser.add_argument(
        "--expected-target-sha256",
        default="5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984",
    )
    parser.add_argument("--expected-raw-size", type=int, default=86908)
    parser.add_argument(
        "--expected-raw-sha256",
        default="AD47DEF8CD04DAEB7F681980B7F688E1C82EED80D819648E51165AA53854CABB",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = audit(args)
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.resolve().write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
