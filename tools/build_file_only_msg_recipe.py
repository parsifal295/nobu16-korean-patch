#!/usr/bin/env python3
"""Build and apply a compact offline recipe for NOBU16 msgui.bin.

The exported recipe carries only stock/target hashes, per-entry source hashes,
and Korean replacement strings.  It never carries a complete publisher
resource.  Application always reads a SHA-gated stock file and writes a
separate verified output through an atomic rename.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

from nobu16_lz4 import LZ4Error, decompress_wrapper, recompress_wrapper
from nobu16_msg_table import MessageTableError, parse_message_table, rebuild_message_table


SCHEMA = "nobu16.file-only-msg-recipe.v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise


def write_json(path: Path, value: Any) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    atomic_write(path, encoded)


def load_catalog(path: Path, language: str) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("schema") != "nobu16.kr.translation.v1":
        raise ValueError("unsupported translation catalog schema")
    if language not in catalog.get("source_files", {}):
        raise ValueError(f"catalog has no {language} source")
    return catalog


def apply_operations(
    source_blob: bytes, operations: Sequence[dict[str, Any]], expected_count: int
) -> tuple[bytes, bytes]:
    _, raw = decompress_wrapper(source_blob)
    table = parse_message_table(raw)
    if table.string_count != expected_count:
        raise ValueError(
            f"msgui string count is {table.string_count}, expected {expected_count}"
        )

    texts = list(table.texts)
    seen: set[int] = set()
    for operation in operations:
        entry_id = int(operation["id"])
        if entry_id in seen:
            raise ValueError(f"duplicate operation id {entry_id}")
        seen.add(entry_id)
        if not 0 <= entry_id < table.string_count:
            raise ValueError(f"operation id {entry_id} is outside msgui")
        source = texts[entry_id]
        actual_source_hash = text_hash(source)
        expected_source_hash = str(operation["source_utf16le_sha256"]).upper()
        if actual_source_hash != expected_source_hash:
            raise ValueError(
                f"id {entry_id} source hash mismatch: {actual_source_hash}, "
                f"expected {expected_source_hash}"
            )
        replacement = operation["replacement"]
        if not isinstance(replacement, str) or not replacement or "\x00" in replacement:
            raise ValueError(f"id {entry_id} has an invalid replacement")
        texts[entry_id] = replacement

    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise ValueError("rebuilt message-table parse verification failed")
    output_blob = recompress_wrapper(rebuilt_raw, source_blob)
    _, output_raw_check = decompress_wrapper(output_blob)
    if output_raw_check != rebuilt_raw:
        raise ValueError("rebuilt wrapper decompression verification failed")
    return output_blob, rebuilt_raw


def cmd_export(args: argparse.Namespace) -> int:
    language = args.language.upper()
    catalog = load_catalog(args.catalog, language)
    source_spec = catalog["source_files"][language]
    stock_path = (args.game_root / Path(source_spec["path"])).resolve()
    target_path = args.target.resolve()
    stock_blob = stock_path.read_bytes()
    target_blob = target_path.read_bytes()
    expected_stock_hash = str(source_spec["sha256"]).upper()
    if sha256_bytes(stock_blob) != expected_stock_hash:
        raise ValueError("stock msgui hash does not match the translation catalog")

    _, stock_raw = decompress_wrapper(stock_blob)
    stock_table = parse_message_table(stock_raw)
    operations: list[dict[str, Any]] = []
    seen: set[int] = set()
    for entry in catalog["entries"]:
        entry_id = int(entry["id"])
        if entry_id in seen:
            raise ValueError(f"duplicate catalog id {entry_id}")
        seen.add(entry_id)
        if not 0 <= entry_id < stock_table.string_count:
            raise ValueError(f"catalog id {entry_id} is outside msgui")
        expected_source = entry["source"][language]
        actual_source = stock_table.texts[entry_id]
        if actual_source != expected_source:
            raise ValueError(f"catalog source mismatch at id {entry_id}")
        replacement = entry["ko"]
        if not isinstance(replacement, str) or not replacement or "\x00" in replacement:
            raise ValueError(f"catalog replacement is invalid at id {entry_id}")
        operations.append(
            {
                "id": entry_id,
                "source_utf16le_sha256": text_hash(actual_source),
                "replacement": replacement,
            }
        )

    rebuilt_blob, rebuilt_raw = apply_operations(
        stock_blob, operations, stock_table.string_count
    )
    if rebuilt_blob != target_blob:
        raise ValueError("compact recipe does not reproduce the pinned target byte-for-byte")

    recipe = {
        "schema": SCHEMA,
        "scope": catalog["scope"],
        "version": catalog["version"],
        "language": language,
        "file_only": True,
        "source": {
            "relative_path": str(Path(source_spec["path"])).replace("\\", "/"),
            "size": len(stock_blob),
            "sha256": sha256_bytes(stock_blob),
            "raw_size": len(stock_raw),
            "raw_sha256": sha256_bytes(stock_raw),
            "string_count": stock_table.string_count,
        },
        "target": {
            "size": len(rebuilt_blob),
            "sha256": sha256_bytes(rebuilt_blob),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256_bytes(rebuilt_raw),
        },
        "operations": operations,
        "payload_policy": {
            "contains_complete_source": False,
            "contains_complete_target": False,
            "contains_executable_bytes": False,
            "source_text_is_stored_as_hash_only": True,
            "stock_file_is_required_at_apply_time": True,
        },
        "export_verification": {
            "byte_identical_to_pinned_target": True,
            "table_parse_roundtrip": True,
            "wrapper_decompress_roundtrip": True,
        },
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    recipe_path = args.output_root / "main_menu_sc.recipe.json"
    write_json(recipe_path, recipe)
    print(f"recipe={recipe_path}")
    print(f"recipe_sha256={sha256_file(recipe_path)}")
    print(f"operations={len(operations)}")
    print(f"target_sha256={recipe['target']['sha256']}")
    print("pinned_target_exact=OK")
    return 0


def cmd_export_build(args: argparse.Namespace) -> int:
    """Export a public recipe from a validated msgui catalog-v2 build manifest.

    Unlike ``export`` this path does not need the development catalog (which
    contains complete commercial source text).  The build manifest carries
    only source hashes and the translated replacement strings.
    """
    manifest_path = args.build_manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "nobu16.kr.msgui-build-manifest.v2":
        raise ValueError("unsupported msgui build manifest schema")
    if manifest.get("file_only") is not True:
        raise ValueError("build manifest is not marked file-only")
    for key in (
        "process_memory_access",
        "registry_modified",
        "executable_modified",
        "installed_game_files_modified",
    ):
        if manifest.get(key) is not False:
            raise ValueError(f"unsafe or missing build-manifest field: {key}")

    source_spec = manifest["source"]
    target_spec = manifest["target"]
    relative_path = Path(manifest["resource"])
    stock_path = (args.game_root / relative_path).resolve()
    target_path = args.target.resolve()
    stock_blob = stock_path.read_bytes()
    target_blob = target_path.read_bytes()
    if len(stock_blob) != int(source_spec["size"]) or sha256_bytes(stock_blob) != source_spec["sha256"]:
        raise ValueError("stock msgui does not match the v2 build manifest")
    if len(target_blob) != int(target_spec["size"]) or sha256_bytes(target_blob) != target_spec["sha256"]:
        raise ValueError("target msgui does not match the v2 build manifest")

    operations: list[dict[str, Any]] = []
    for changed in manifest["changed"]:
        operation = {
            "id": int(changed["id"]),
            "source_utf16le_sha256": str(changed["source_utf16le_sha256"]).upper(),
            "replacement": changed["replacement"],
        }
        if text_hash(operation["replacement"]) != str(changed["replacement_utf16le_sha256"]).upper():
            raise ValueError(f"replacement hash mismatch at id {operation['id']}")
        operations.append(operation)
    if len(operations) != int(manifest["changed_count"]):
        raise ValueError("changed operation count mismatch")
    operation_ids = [operation["id"] for operation in operations]
    operation_ids_blob = json.dumps(operation_ids, separators=(",", ":")).encode("utf-8")
    operation_index = manifest.get("operation_index")
    if (
        not isinstance(operation_index, dict)
        or int(operation_index.get("count", -1)) != len(operation_ids)
        or operation_index.get("ids_sha256") != sha256_bytes(operation_ids_blob)
        or operation_index.get("sorted_unique") is not True
        or operation_ids != sorted(set(operation_ids))
    ):
        raise ValueError("build manifest operation index is invalid")

    rebuilt_blob, rebuilt_raw = apply_operations(
        stock_blob, operations, int(source_spec["string_count"])
    )
    if rebuilt_blob != target_blob:
        raise ValueError("compact recipe does not reproduce the v2 pinned target byte-for-byte")
    if len(rebuilt_raw) != int(target_spec["raw_size"]) or sha256_bytes(rebuilt_raw) != target_spec["raw_sha256"]:
        raise ValueError("rebuilt raw target does not match the v2 build manifest")

    recipe = {
        "schema": SCHEMA,
        "scope": "msgui_catalog_v2",
        "version": manifest["catalog_version"],
        "language": "SC",
        "file_only": True,
        "source": {
            "relative_path": str(relative_path).replace("\\", "/"),
            "size": len(stock_blob),
            "sha256": sha256_bytes(stock_blob),
            "raw_size": int(source_spec["raw_size"]),
            "raw_sha256": source_spec["raw_sha256"],
            "string_count": int(source_spec["string_count"]),
        },
        "target": {
            "size": len(rebuilt_blob),
            "sha256": sha256_bytes(rebuilt_blob),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256_bytes(rebuilt_raw),
        },
        "operations": operations,
        "operation_index": {
            "count": len(operation_ids),
            "id_encoding": "UTF-8 compact JSON integer array",
            "ids_sha256": sha256_bytes(operation_ids_blob),
            "sorted_unique": True,
        },
        "payload_policy": {
            "contains_complete_source": False,
            "contains_complete_target": False,
            "contains_executable_bytes": False,
            "source_text_is_stored_as_hash_only": True,
            "stock_file_is_required_at_apply_time": True,
            "development_catalog_included": False,
        },
        "export_verification": {
            "byte_identical_to_pinned_target": True,
            "table_parse_roundtrip": True,
            "wrapper_decompress_roundtrip": True,
            "build_manifest_sha256": sha256_file(manifest_path),
        },
    }
    output_path = args.output.resolve()
    write_json(output_path, recipe)
    print(f"recipe={output_path}")
    print(f"recipe_sha256={sha256_file(output_path)}")
    print(f"operations={len(operations)}")
    print(f"target_sha256={recipe['target']['sha256']}")
    print("development_catalog_included=False")
    print("pinned_target_exact=OK")
    return 0


def load_recipe(path: Path) -> dict[str, Any]:
    recipe = json.loads(path.read_text(encoding="utf-8"))
    if recipe.get("schema") != SCHEMA:
        raise ValueError("unsupported message recipe schema")
    if recipe.get("file_only") is not True:
        raise ValueError("message recipe is not marked file-only")
    if recipe.get("language") != "SC":
        raise ValueError("this file-only recipe applier accepts only the SC backend")
    operations = recipe.get("operations")
    if not isinstance(operations, list):
        raise ValueError("message recipe operations must be an array")
    operation_ids = [int(operation["id"]) for operation in operations]
    operation_index = recipe.get("operation_index")
    if recipe.get("scope") == "msgui_catalog_v2" and not isinstance(operation_index, dict):
        raise ValueError("catalog-v2 message recipe has no operation index")
    if operation_index is not None:
        if not isinstance(operation_index, dict):
            raise ValueError("message recipe operation index must be an object")
        operation_ids_blob = json.dumps(operation_ids, separators=(",", ":")).encode("utf-8")
        if (
            int(operation_index.get("count", -1)) != len(operation_ids)
            or operation_index.get("ids_sha256") != sha256_bytes(operation_ids_blob)
            or operation_index.get("sorted_unique") is not True
            or operation_ids != sorted(set(operation_ids))
        ):
            raise ValueError("message recipe operation index is invalid")
    return recipe


def cmd_apply(args: argparse.Namespace) -> int:
    recipe_path = args.recipe.resolve()
    stock_path = args.stock.resolve()
    output_path = args.output.resolve()
    if stock_path == output_path:
        raise ValueError("refusing to overwrite the stock input")
    recipe = load_recipe(recipe_path)
    stock_blob = stock_path.read_bytes()
    input_hash_before = sha256_bytes(stock_blob)
    source = recipe["source"]
    if len(stock_blob) != int(source["size"]) or input_hash_before != source["sha256"]:
        raise ValueError(
            f"stock msgui mismatch: size={len(stock_blob)} sha256={input_hash_before}"
        )

    output_blob, output_raw = apply_operations(
        stock_blob, recipe["operations"], int(source["string_count"])
    )
    target = recipe["target"]
    if len(output_blob) != int(target["size"]):
        raise ValueError("rebuilt msgui size mismatch")
    if sha256_bytes(output_blob) != target["sha256"]:
        raise ValueError("rebuilt msgui hash mismatch")
    if len(output_raw) != int(target["raw_size"]) or sha256_bytes(output_raw) != target["raw_sha256"]:
        raise ValueError("rebuilt raw message-table mismatch")

    atomic_write(output_path, output_blob)
    input_hash_after = sha256_file(stock_path)
    if input_hash_after != input_hash_before:
        output_path.unlink(missing_ok=True)
        raise ValueError("stock msgui changed while applying the recipe")

    report = {
        "schema": "nobu16.file-only-msg-recipe.apply-report.v1",
        "stock": {
            "path": str(stock_path),
            "sha256_before": input_hash_before,
            "sha256_after": input_hash_after,
            "unchanged": True,
        },
        "output": {
            "path": str(output_path),
            "size": len(output_blob),
            "sha256": sha256_bytes(output_blob),
            "exact": True,
        },
        "operations": len(recipe["operations"]),
        "offline_file_recipe": True,
    }
    if args.report:
        write_json(args.report.resolve(), report)
    print(f"output={output_path}")
    print(f"sha256={report['output']['sha256']}")
    print("stock_input_unchanged=OK")
    print("target_exact=OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    export = sub.add_parser("export")
    export.add_argument("--game-root", type=Path, required=True)
    export.add_argument("--catalog", type=Path, required=True)
    export.add_argument("--language", choices=("SC", "sc"), default="SC")
    export.add_argument("--target", type=Path, required=True)
    export.add_argument("--output-root", type=Path, required=True)
    export.set_defaults(func=cmd_export)

    export_build = sub.add_parser(
        "export-build",
        help="export a compact public recipe from a validated catalog-v2 build manifest",
    )
    export_build.add_argument("--game-root", type=Path, required=True)
    export_build.add_argument("--build-manifest", type=Path, required=True)
    export_build.add_argument("--target", type=Path, required=True)
    export_build.add_argument("--output", type=Path, required=True)
    export_build.set_defaults(func=cmd_export_build)

    apply = sub.add_parser("apply")
    apply.add_argument("--recipe", type=Path, required=True)
    apply.add_argument("--stock", type=Path, required=True)
    apply.add_argument("--output", type=Path, required=True)
    apply.add_argument("--report", type=Path)
    apply.set_defaults(func=cmd_apply)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, KeyError, json.JSONDecodeError, LZ4Error, MessageTableError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
