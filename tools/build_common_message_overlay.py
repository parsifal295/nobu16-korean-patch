#!/usr/bin/env python3
"""Build a source-text-free file recipe for a common NOBU16 message table.

The input overlay contains only stable string ids, SHA-256 hashes of the
official SC strings, and project-authored Korean replacements.  The builder
reads a fully pinned stock ``msgdata.bin`` or ``msgev.bin``, validates every
replacement against the live source table, rebuilds the whole offset table,
and emits three offline artifacts below an explicit output directory:

* a deterministic rebuilt target resource;
* a source-text-free build manifest; and
* a ``nobu16.file-only-msg-recipe.v1`` recipe accepted by the existing
  ``build_file_only_msg_recipe.py apply`` command.

It never overwrites an installed game file, launches the game, accesses a
process, modifies an executable, or reads/writes the registry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Sequence

from nobu16_lz4 import LZ4Error, decompress_wrapper, recompress_wrapper
from nobu16_msg_table import MessageTableError, parse_message_table, rebuild_message_table


OVERLAY_SCHEMA = "nobu16.kr.common-message-overlay.v1"
BUILD_SCHEMA = "nobu16.kr.common-message-build-manifest.v1"
RECIPE_SCHEMA = "nobu16.file-only-msg-recipe.v1"
RECIPE_SCOPE = "common_message_overlay_v1"
ALLOWED_RESOURCES = frozenset(
    (
        "MSG_PK/SC/msgdata.bin",
        "MSG_PK/SC/msgev.bin",
    )
)
BUILDABLE_STATUSES = frozenset(("translated", "reviewed"))
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
OVERLAY_ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,127}\Z")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
NON_SEMANTIC_UNICODE_CATEGORIES = frozenset(
    ("Cc", "Cf", "Cs", "Mn", "Me", "Zl", "Zp", "Zs", "Cn")
)

ROOT_KEYS = {
    "schema",
    "overlay_id",
    "resource",
    "base_language",
    "entry_count",
    "distribution_policy",
    "stock_sc",
    "defaults",
    "entries",
}
POLICY_KEYS = {
    "contains_commercial_source_text",
    "contains_complete_game_resource",
}
STOCK_KEYS = {
    "size",
    "packed_sha256",
    "raw_size",
    "raw_sha256",
    "string_count",
}
DEFAULT_KEYS = {"status"}
ENTRY_REQUIRED_KEYS = {"id", "source_sc_utf16le_sha256", "ko"}
ENTRY_ALLOWED_KEYS = ENTRY_REQUIRED_KEYS | {"status", "allow_edge_whitespace_change"}
EDGE_WHITESPACE_INVARIANTS = frozenset(("leading_whitespace", "trailing_whitespace"))


class CommonMessageOverlayError(ValueError):
    """Raised when an overlay or a pinned source resource is invalid."""


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
        temporary.unlink(missing_ok=True)
        raise


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        if not isinstance(key, str):
            raise CommonMessageOverlayError("JSON object key is not a string")
        normalized = key.casefold()
        if normalized in folded:
            raise CommonMessageOverlayError(
                f"duplicate or case-colliding JSON key: {key!r} / {folded[normalized]!r}"
            )
        folded[normalized] = key
        result[key] = value
    return result


def load_json_strict(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CommonMessageOverlayError(f"invalid UTF-8 JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CommonMessageOverlayError("overlay root must be a JSON object")
    return value, blob


def require_exact_keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise CommonMessageOverlayError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise CommonMessageOverlayError(
            f"{label} keys differ: missing={sorted(expected - actual)!r}, "
            f"extra={sorted(actual - expected)!r}"
        )


def require_bool(value: Any, expected: bool, label: str) -> None:
    if type(value) is not bool or value is not expected:
        raise CommonMessageOverlayError(
            f"{label} must be JSON {str(expected).lower()}"
        )


def require_int(value: Any, label: str, *, positive: bool = False) -> int:
    if type(value) is not int or value < (1 if positive else 0):
        qualifier = "positive" if positive else "non-negative"
        raise CommonMessageOverlayError(f"{label} must be a {qualifier} JSON integer")
    return value


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64_RE.fullmatch(value) is None:
        raise CommonMessageOverlayError(f"{label} must be an uppercase SHA-256")
    return value


def has_semantic_text(text: str) -> bool:
    consumed_escape_indexes = {
        index
        for match in ESC_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    return any(
        index not in consumed_escape_indexes
        and not character.isspace()
        and unicodedata.category(character) not in NON_SEMANTIC_UNICODE_CATEGORIES
        for index, character in enumerate(text)
    )


def printf_tokens(text: str) -> tuple[list[str], int]:
    matches = list(PRINTF_RE.finditer(text))
    consumed_percent_indexes = {
        index
        for match in matches
        for index in range(match.start(), match.end())
        if text[index] == "%"
    }
    unknown_percent_count = sum(
        1
        for index, character in enumerate(text)
        if character == "%" and index not in consumed_percent_indexes
    )
    return [match.group(0) for match in matches], unknown_percent_count


def message_invariants(text: str) -> dict[str, Any]:
    printf, unknown_percent_count = printf_tokens(text)
    escape_matches = list(ESC_RE.finditer(text))
    consumed_escape_indexes = {
        index
        for match in escape_matches
        for index in range(match.start(), match.end())
    }
    controls = [
        f"U+{ord(character):04X}"
        for index, character in enumerate(text)
        if unicodedata.category(character) == "Cc"
        and character not in ("\r", "\n")
        and index not in consumed_escape_indexes
    ]
    return {
        "printf": printf,
        "unknown_percent_count": unknown_percent_count,
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "esc": [match.group(0) for match in escape_matches],
        "controls": controls,
        "line_breaks": LINE_BREAK_RE.findall(text),
        "pua": [
            f"U+{ord(character):04X}"
            for character in text
            if 0xE000 <= ord(character) <= 0xF8FF
        ],
    }


def invariant_mismatches(
    source: str,
    replacement: str,
    *,
    allow_edge_whitespace_change: bool = False,
) -> list[str]:
    before = message_invariants(source)
    after = message_invariants(replacement)
    return [
        f"{key}: source={before[key]!r}, ko={after[key]!r}"
        for key in before
        if not (allow_edge_whitespace_change and key in EDGE_WHITESPACE_INVARIANTS)
        if before[key] != after[key]
    ]


def validate_overlay_shape(overlay: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    require_exact_keys(overlay, ROOT_KEYS, "overlay")
    if overlay["schema"] != OVERLAY_SCHEMA:
        raise CommonMessageOverlayError("unsupported common-message overlay schema")
    overlay_id = overlay["overlay_id"]
    if not isinstance(overlay_id, str) or OVERLAY_ID_RE.fullmatch(overlay_id) is None:
        raise CommonMessageOverlayError("overlay_id must be a stable lowercase identifier")
    resource = overlay["resource"]
    if not isinstance(resource, str) or resource not in ALLOWED_RESOURCES:
        raise CommonMessageOverlayError(
            f"resource must be one of {sorted(ALLOWED_RESOURCES)!r}"
        )
    if overlay["base_language"] != "SC":
        raise CommonMessageOverlayError("base_language must be SC")

    policy = overlay["distribution_policy"]
    require_exact_keys(policy, POLICY_KEYS, "distribution_policy")
    require_bool(
        policy["contains_commercial_source_text"],
        False,
        "contains_commercial_source_text",
    )
    require_bool(
        policy["contains_complete_game_resource"],
        False,
        "contains_complete_game_resource",
    )

    stock = overlay["stock_sc"]
    require_exact_keys(stock, STOCK_KEYS, "stock_sc")
    require_int(stock["size"], "stock_sc.size", positive=True)
    require_hash(stock["packed_sha256"], "stock_sc.packed_sha256")
    require_int(stock["raw_size"], "stock_sc.raw_size", positive=True)
    require_hash(stock["raw_sha256"], "stock_sc.raw_sha256")
    require_int(stock["string_count"], "stock_sc.string_count", positive=True)

    defaults = overlay["defaults"]
    require_exact_keys(defaults, DEFAULT_KEYS, "defaults")
    if not isinstance(defaults["status"], str) or defaults["status"] not in BUILDABLE_STATUSES:
        raise CommonMessageOverlayError(
            f"defaults.status must be one of {sorted(BUILDABLE_STATUSES)!r}"
        )

    entries = overlay["entries"]
    if not isinstance(entries, list):
        raise CommonMessageOverlayError("entries must be an array")
    declared_count = require_int(overlay["entry_count"], "entry_count", positive=True)
    if declared_count != len(entries):
        raise CommonMessageOverlayError(
            f"entry_count is {declared_count}, actual entries={len(entries)}"
        )

    ids: list[int] = []
    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            raise CommonMessageOverlayError(f"{label} must be an object")
        actual_keys = set(entry)
        if not ENTRY_REQUIRED_KEYS <= actual_keys or not actual_keys <= ENTRY_ALLOWED_KEYS:
            raise CommonMessageOverlayError(
                f"{label} keys differ: missing={sorted(ENTRY_REQUIRED_KEYS - actual_keys)!r}, "
                f"extra={sorted(actual_keys - ENTRY_ALLOWED_KEYS)!r}"
            )
        entry_id = require_int(entry["id"], f"{label}.id")
        source_hash = require_hash(
            entry["source_sc_utf16le_sha256"],
            f"{label}.source_sc_utf16le_sha256",
        )
        replacement = entry["ko"]
        if not isinstance(replacement, str):
            raise CommonMessageOverlayError(f"{label}.ko must be a string")
        if "\x00" in replacement:
            raise CommonMessageOverlayError(f"{label}.ko contains an embedded NUL")
        if not has_semantic_text(replacement):
            raise CommonMessageOverlayError(f"{label}.ko must contain semantic text")
        try:
            replacement.encode("utf-16le")
        except UnicodeEncodeError as exc:
            raise CommonMessageOverlayError(
                f"{label}.ko is not valid UTF-16 text: {exc}"
            ) from exc
        status = entry.get("status", defaults["status"])
        if not isinstance(status, str) or status not in BUILDABLE_STATUSES:
            raise CommonMessageOverlayError(
                f"{label}.status must be one of {sorted(BUILDABLE_STATUSES)!r}"
            )
        allow_edge_whitespace_change = entry.get("allow_edge_whitespace_change", False)
        if type(allow_edge_whitespace_change) is not bool:
            raise CommonMessageOverlayError(
                f"{label}.allow_edge_whitespace_change must be a JSON boolean"
            )
        ids.append(entry_id)
        normalized.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": source_hash,
                "ko": replacement,
                "status": status,
                "allow_edge_whitespace_change": allow_edge_whitespace_change,
            }
        )

    if ids != sorted(ids):
        raise CommonMessageOverlayError("entry ids must be sorted in ascending order")
    if len(ids) != len(set(ids)):
        raise CommonMessageOverlayError("entry ids must be unique")
    return resource, stock, normalized


def _operation_index(operations: Sequence[dict[str, Any]]) -> dict[str, Any]:
    ids = [int(operation["id"]) for operation in operations]
    encoded = json.dumps(ids, separators=(",", ":")).encode("utf-8")
    return {
        "count": len(ids),
        "id_encoding": "UTF-8 compact JSON integer array",
        "ids_sha256": sha256_bytes(encoded),
        "sorted_unique": ids == sorted(set(ids)),
    }


def build_overlay(game_root: Path, overlay_path: Path, output_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    overlay_path = overlay_path.resolve()
    output_root = output_root.resolve()
    overlay, overlay_blob = load_json_strict(overlay_path)
    resource, stock_spec, entries = validate_overlay_shape(overlay)

    stock_path = (game_root / Path(resource)).resolve()
    target_path = (output_root / Path(resource)).resolve()
    if stock_path == target_path:
        raise CommonMessageOverlayError("refusing to overwrite the installed stock resource")
    manifest_path = output_root / f"{Path(resource).stem}.build-manifest.json"
    recipe_path = output_root / f"{Path(resource).stem}_sc.recipe.json"
    if overlay_path in (target_path, manifest_path.resolve(), recipe_path.resolve()):
        raise CommonMessageOverlayError("refusing to overwrite the input overlay")

    stock_blob = stock_path.read_bytes()
    stock_hash_before = sha256_bytes(stock_blob)
    if len(stock_blob) != int(stock_spec["size"]):
        raise CommonMessageOverlayError(
            f"stock packed size is {len(stock_blob)}, expected {stock_spec['size']}"
        )
    if stock_hash_before != stock_spec["packed_sha256"]:
        raise CommonMessageOverlayError(
            f"stock packed SHA-256 is {stock_hash_before}, "
            f"expected {stock_spec['packed_sha256']}"
        )

    _, stock_raw = decompress_wrapper(stock_blob)
    if len(stock_raw) != int(stock_spec["raw_size"]):
        raise CommonMessageOverlayError(
            f"stock raw size is {len(stock_raw)}, expected {stock_spec['raw_size']}"
        )
    stock_raw_hash = sha256_bytes(stock_raw)
    if stock_raw_hash != stock_spec["raw_sha256"]:
        raise CommonMessageOverlayError(
            f"stock raw SHA-256 is {stock_raw_hash}, expected {stock_spec['raw_sha256']}"
        )

    table = parse_message_table(stock_raw)
    if table.string_count != int(stock_spec["string_count"]):
        raise CommonMessageOverlayError(
            f"stock string count is {table.string_count}, "
            f"expected {stock_spec['string_count']}"
        )
    if rebuild_message_table(table, table.texts) != stock_raw:
        raise CommonMessageOverlayError("stock message-table parse/rebuild is not byte-exact")

    texts = list(table.texts)
    operations: list[dict[str, Any]] = []
    changed_manifest: list[dict[str, Any]] = []
    for entry in entries:
        entry_id = int(entry["id"])
        if not 0 <= entry_id < table.string_count:
            raise CommonMessageOverlayError(
                f"entry id {entry_id} is outside 0..{table.string_count - 1}"
            )
        source = texts[entry_id]
        actual_source_hash = text_hash(source)
        if actual_source_hash != entry["source_sc_utf16le_sha256"]:
            raise CommonMessageOverlayError(
                f"id {entry_id} source hash is {actual_source_hash}, "
                f"expected {entry['source_sc_utf16le_sha256']}"
            )
        replacement = str(entry["ko"])
        problems = invariant_mismatches(
            source,
            replacement,
            allow_edge_whitespace_change=bool(entry["allow_edge_whitespace_change"]),
        )
        if problems:
            raise CommonMessageOverlayError(
                f"id {entry_id} invariant mismatch: {'; '.join(problems)}"
            )
        if replacement == source:
            continue
        operation = {
            "id": entry_id,
            "source_utf16le_sha256": actual_source_hash,
            "replacement": replacement,
        }
        operations.append(operation)
        changed_manifest.append(
            {
                **operation,
                "replacement_utf16le_sha256": text_hash(replacement),
                "status": entry["status"],
            }
        )
        texts[entry_id] = replacement

    if not operations:
        raise CommonMessageOverlayError("overlay contains no effective message changes")

    operation_index = _operation_index(operations)
    if operation_index["sorted_unique"] is not True:
        raise CommonMessageOverlayError("internal operation id order is not sorted and unique")
    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise CommonMessageOverlayError("rebuilt raw message-table verification failed")
    target_blob = recompress_wrapper(rebuilt_raw, stock_blob)
    _, target_raw_check = decompress_wrapper(target_blob)
    if target_raw_check != rebuilt_raw:
        raise CommonMessageOverlayError("rebuilt wrapper decompression verification failed")

    source = {
        "relative_path": resource,
        "size": len(stock_blob),
        "sha256": stock_hash_before,
        "raw_size": len(stock_raw),
        "raw_sha256": stock_raw_hash,
        "string_count": table.string_count,
    }
    target = {
        "size": len(target_blob),
        "sha256": sha256_bytes(target_blob),
        "raw_size": len(rebuilt_raw),
        "raw_sha256": sha256_bytes(rebuilt_raw),
    }
    manifest = {
        "schema": BUILD_SCHEMA,
        "overlay_schema": OVERLAY_SCHEMA,
        "overlay_id": overlay["overlay_id"],
        "overlay_sha256": sha256_bytes(overlay_blob),
        "resource": resource,
        "base_language": "SC",
        "file_only": True,
        "process_memory_access": False,
        "registry_modified": False,
        "executable_modified": False,
        "installed_game_files_modified": False,
        "commercial_source_text_included": False,
        "overlay_entry_count": len(entries),
        "changed_count": len(operations),
        "source": source,
        "target": target,
        "operation_index": operation_index,
        "changed": changed_manifest,
        "verification": {
            "stock_pins": "OK",
            "source_string_hashes": "OK",
            "replacement_invariants": "OK",
            "table_parse_roundtrip": "OK",
            "wrapper_decompress_roundtrip": "OK",
        },
    }
    manifest_blob = encode_json(manifest)
    recipe = {
        "schema": RECIPE_SCHEMA,
        "scope": RECIPE_SCOPE,
        "version": "1",
        "language": "SC",
        "file_only": True,
        "source": source,
        "target": target,
        "operations": operations,
        "operation_index": operation_index,
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
            "build_manifest_sha256": sha256_bytes(manifest_blob),
        },
    }
    recipe_blob = encode_json(recipe)

    if sha256_file(stock_path) != stock_hash_before:
        raise CommonMessageOverlayError("stock resource changed while the overlay was built")
    atomic_write(target_path, target_blob)
    atomic_write(manifest_path, manifest_blob)
    atomic_write(recipe_path, recipe_blob)

    return {
        "target_path": target_path,
        "manifest_path": manifest_path,
        "recipe_path": recipe_path,
        "target_sha256": target["sha256"],
        "manifest_sha256": sha256_bytes(manifest_blob),
        "recipe_sha256": sha256_bytes(recipe_blob),
        "overlay_entries": len(entries),
        "operations": len(operations),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser(
        "build", help="validate a public overlay and build a target, manifest, and recipe"
    )
    build.add_argument("--game-root", type=Path, required=True)
    build.add_argument("--overlay", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command != "build":
            raise CommonMessageOverlayError(f"unsupported command: {args.command}")
        result = build_overlay(args.game_root, args.overlay, args.output_root)
    except (
        OSError,
        KeyError,
        TypeError,
        CommonMessageOverlayError,
        LZ4Error,
        MessageTableError,
    ) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 1

    print(f"target={result['target_path']}")
    print(f"target_sha256={result['target_sha256']}")
    print(f"manifest={result['manifest_path']}")
    print(f"manifest_sha256={result['manifest_sha256']}")
    print(f"recipe={result['recipe_path']}")
    print(f"recipe_sha256={result['recipe_sha256']}")
    print(f"overlay_entries={result['overlay_entries']}")
    print(f"operations={result['operations']}")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
