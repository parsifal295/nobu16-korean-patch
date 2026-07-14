#!/usr/bin/env python3
"""Export a private common-message translation batch as a public overlay.

Private development batches contain official Simplified-Chinese strings so a
translator can review the correct row.  Those strings must never be committed
or shipped.  This exporter verifies them against a pinned stock ``msgdata`` or
``msgev`` resource and emits only stable ids, per-string UTF-16LE hashes, and
project-authored Korean replacements accepted by
``build_common_message_overlay.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import build_common_message_overlay as common
from nobu16_lz4 import LZ4Error, decompress_wrapper
from nobu16_msg_table import MessageTableError, parse_message_table, rebuild_message_table


PRIVATE_SCHEMA = "nobu16.kr.translation.v1"
PRIVATE_ROOT_KEYS = {
    "schema",
    "scope",
    "version",
    "base_languages",
    "source_files",
    "entries",
}
SOURCE_FILE_KEYS = {"path", "sha256"}
PRIVATE_ENTRY_REQUIRED_KEYS = {"id", "source", "ko"}
PRIVATE_ENTRY_ALLOWED_KEYS = PRIVATE_ENTRY_REQUIRED_KEYS | {
    "status",
    "allow_edge_whitespace_change",
}
REFERENCE_LANGUAGES = frozenset(("SC", "EN", "JP"))


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise common.CommonMessageOverlayError(f"{label} must be a non-empty string")
    return value


def _load_private_batch(
    path: Path, default_status: str
) -> tuple[str, dict[str, dict[str, str]], list[dict[str, Any]]]:
    batch, _ = common.load_json_strict(path)
    common.require_exact_keys(batch, PRIVATE_ROOT_KEYS, "private batch")
    if batch["schema"] != PRIVATE_SCHEMA:
        raise common.CommonMessageOverlayError("unsupported private translation schema")
    _require_nonempty_string(batch["scope"], "scope")
    _require_nonempty_string(batch["version"], "version")
    base_languages = batch["base_languages"]
    if (
        not isinstance(base_languages, list)
        or not base_languages
        or not all(isinstance(language, str) for language in base_languages)
        or len(base_languages) != len(set(base_languages))
        or "SC" not in base_languages
        or not set(base_languages) <= REFERENCE_LANGUAGES
    ):
        raise common.CommonMessageOverlayError(
            "base_languages must be unique SC/EN/JP names and include SC"
        )

    source_files = batch["source_files"]
    if not isinstance(source_files, dict) or set(source_files) != set(base_languages):
        raise common.CommonMessageOverlayError(
            "source_files keys must exactly match base_languages"
        )
    source_sc = source_files["SC"]
    common.require_exact_keys(source_sc, SOURCE_FILE_KEYS, "source_files.SC")
    resource = source_sc["path"]
    if not isinstance(resource, str) or resource not in common.ALLOWED_RESOURCES:
        raise common.CommonMessageOverlayError(
            f"source_files.SC.path must be one of {sorted(common.ALLOWED_RESOURCES)!r}"
        )
    resource_name = Path(resource).name
    normalized_sources: dict[str, dict[str, str]] = {}
    for language in base_languages:
        descriptor = source_files[language]
        common.require_exact_keys(
            descriptor, SOURCE_FILE_KEYS, f"source_files.{language}"
        )
        expected_path = f"MSG_PK/{language}/{resource_name}"
        if descriptor["path"] != expected_path:
            raise common.CommonMessageOverlayError(
                f"source_files.{language}.path must be {expected_path!r}"
            )
        normalized_sources[language] = {
            "path": expected_path,
            "sha256": common.require_hash(
                descriptor["sha256"], f"source_files.{language}.sha256"
            ),
        }

    entries = batch["entries"]
    if not isinstance(entries, list) or not entries:
        raise common.CommonMessageOverlayError("entries must be a non-empty array")

    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            raise common.CommonMessageOverlayError(f"{label} must be an object")
        actual_keys = set(entry)
        if (
            not PRIVATE_ENTRY_REQUIRED_KEYS <= actual_keys
            or not actual_keys <= PRIVATE_ENTRY_ALLOWED_KEYS
        ):
            raise common.CommonMessageOverlayError(
                f"{label} keys differ: "
                f"missing={sorted(PRIVATE_ENTRY_REQUIRED_KEYS - actual_keys)!r}, "
                f"extra={sorted(actual_keys - PRIVATE_ENTRY_ALLOWED_KEYS)!r}"
            )
        entry_id = common.require_int(entry["id"], f"{label}.id")
        source = entry["source"]
        if (
            not isinstance(source, dict)
            or "SC" not in source
            or not set(source) <= set(base_languages)
        ):
            raise common.CommonMessageOverlayError(
                f"{label}.source must contain SC and only declared reference languages"
            )
        source_texts: dict[str, str] = {}
        for language, source_text in source.items():
            if not isinstance(source_text, str) or "\x00" in source_text:
                raise common.CommonMessageOverlayError(
                    f"{label}.source.{language} must be NUL-free text"
                )
            source_texts[language] = source_text
        replacement = entry["ko"]
        if not isinstance(replacement, str) or "\x00" in replacement:
            raise common.CommonMessageOverlayError(f"{label}.ko must be NUL-free text")
        if not common.has_semantic_text(replacement):
            raise common.CommonMessageOverlayError(
                f"{label}.ko must contain semantic text"
            )
        try:
            replacement.encode("utf-16le")
        except UnicodeEncodeError as exc:
            raise common.CommonMessageOverlayError(
                f"{label}.ko is not valid UTF-16 text: {exc}"
            ) from exc
        status = entry.get("status", default_status)
        if not isinstance(status, str) or status not in common.BUILDABLE_STATUSES:
            raise common.CommonMessageOverlayError(
                f"{label}.status must be one of {sorted(common.BUILDABLE_STATUSES)!r}"
            )
        allow_edge_whitespace_change = entry.get("allow_edge_whitespace_change", False)
        if type(allow_edge_whitespace_change) is not bool:
            raise common.CommonMessageOverlayError(
                f"{label}.allow_edge_whitespace_change must be a JSON boolean"
            )
        normalized.append(
            {
                "id": entry_id,
                "source": source_texts,
                "ko": replacement,
                "status": status,
                "allow_edge_whitespace_change": allow_edge_whitespace_change,
            }
        )

    # Input order is intentionally irrelevant. Duplicate/conflict handling is
    # performed across all batches after each row is verified against stock.
    return resource, normalized_sources, normalized


def export_overlay(
    private_batch_paths: Sequence[Path] | Path,
    stock_paths: dict[str, Path] | Path,
    output_path: Path,
    overlay_id: str,
    default_status: str = "translated",
) -> dict[str, Any]:
    if isinstance(private_batch_paths, Path):
        private_batch_paths = [private_batch_paths]
    if isinstance(stock_paths, Path):
        stock_paths = {"SC": stock_paths}
    resolved_batches = [path.resolve() for path in private_batch_paths]
    if not resolved_batches:
        raise common.CommonMessageOverlayError("at least one private batch is required")
    if len(resolved_batches) != len(set(resolved_batches)):
        raise common.CommonMessageOverlayError("private batch paths must be unique")
    # Conflicting duplicates are rejected, so sorting inputs makes results
    # deterministic without creating an implicit last-writer-wins rule.
    resolved_batches.sort(key=lambda path: str(path).replace("\\", "/").casefold())
    resolved_stocks = {
        language: path.resolve() for language, path in stock_paths.items()
    }
    output_path = output_path.resolve()
    if output_path in set(resolved_batches) | set(resolved_stocks.values()):
        raise common.CommonMessageOverlayError("refusing to overwrite an input file")
    if (
        not isinstance(overlay_id, str)
        or common.OVERLAY_ID_RE.fullmatch(overlay_id) is None
    ):
        raise common.CommonMessageOverlayError(
            "overlay_id must be a stable lowercase identifier"
        )
    if default_status not in common.BUILDABLE_STATUSES:
        raise common.CommonMessageOverlayError(
            f"default status must be one of {sorted(common.BUILDABLE_STATUSES)!r}"
        )

    loaded_batches: list[
        tuple[Path, str, dict[str, dict[str, str]], list[dict[str, Any]]]
    ] = []
    resource: str | None = None
    descriptors: dict[str, dict[str, str]] = {}
    for batch_path in resolved_batches:
        batch_resource, batch_descriptors, entries = _load_private_batch(
            batch_path, default_status
        )
        if resource is None:
            resource = batch_resource
        elif batch_resource != resource:
            raise common.CommonMessageOverlayError(
                "all private batches must target the same common-message resource"
            )
        for language, descriptor in batch_descriptors.items():
            previous = descriptors.get(language)
            if previous is not None and previous != descriptor:
                raise common.CommonMessageOverlayError(
                    f"conflicting {language} source-file descriptor across private batches"
                )
            descriptors[language] = descriptor
        loaded_batches.append((batch_path, batch_resource, batch_descriptors, entries))
    assert resource is not None

    if "SC" not in resolved_stocks:
        raise common.CommonMessageOverlayError("an SC stock resource is required")
    unexpected_stock_languages = set(resolved_stocks) - REFERENCE_LANGUAGES
    if unexpected_stock_languages:
        raise common.CommonMessageOverlayError(
            f"unsupported stock languages: {sorted(unexpected_stock_languages)!r}"
        )
    missing_stock_languages = set(descriptors) - set(resolved_stocks)
    if missing_stock_languages:
        raise common.CommonMessageOverlayError(
            f"missing stock resources for {sorted(missing_stock_languages)!r}"
        )

    stock_blobs: dict[str, bytes] = {}
    raws: dict[str, bytes] = {}
    tables: dict[str, Any] = {}
    for language, descriptor in descriptors.items():
        stock_blob = resolved_stocks[language].read_bytes()
        actual_hash = common.sha256_bytes(stock_blob)
        if actual_hash != descriptor["sha256"]:
            raise common.CommonMessageOverlayError(
                f"{language} stock packed SHA-256 is {actual_hash}, "
                f"expected {descriptor['sha256']}"
            )
        _, raw = decompress_wrapper(stock_blob)
        table = parse_message_table(raw)
        if rebuild_message_table(table, table.texts) != raw:
            raise common.CommonMessageOverlayError(
                f"{language} stock message-table parse/rebuild is not byte-exact"
            )
        stock_blobs[language] = stock_blob
        raws[language] = raw
        tables[language] = table

    merged: dict[int, dict[str, Any]] = {}
    for batch_path, _, _, entries in loaded_batches:
        for entry in entries:
            entry_id = int(entry["id"])
            for language, expected_source in entry["source"].items():
                if language not in tables:
                    raise common.CommonMessageOverlayError(
                        f"{batch_path.name}: id {entry_id} has no verified {language} stock table"
                    )
                table = tables[language]
                if not 0 <= entry_id < table.string_count:
                    raise common.CommonMessageOverlayError(
                        f"{batch_path.name}: id {entry_id} is outside the {language} "
                        f"range 0..{table.string_count - 1}"
                    )
                if expected_source != table.texts[entry_id]:
                    raise common.CommonMessageOverlayError(
                        f"{batch_path.name}: id {entry_id} {language} source mismatch"
                    )

            actual_source = tables["SC"].texts[entry_id]
            replacement = str(entry["ko"])
            if replacement == actual_source:
                raise common.CommonMessageOverlayError(
                    f"{batch_path.name}: id {entry_id} is a no-op and would expose "
                    "commercial source text"
                )
            problems = common.invariant_mismatches(
                actual_source,
                replacement,
                allow_edge_whitespace_change=bool(
                    entry["allow_edge_whitespace_change"]
                ),
            )
            if problems:
                raise common.CommonMessageOverlayError(
                    f"{batch_path.name}: id {entry_id} invariant mismatch: "
                    f"{'; '.join(problems)}"
                )
            public_entry: dict[str, Any] = {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(actual_source),
                "ko": replacement,
            }
            if entry["status"] != default_status:
                public_entry["status"] = entry["status"]
            if entry["allow_edge_whitespace_change"]:
                public_entry["allow_edge_whitespace_change"] = True
            previous = merged.get(entry_id)
            if previous is not None and previous != public_entry:
                raise common.CommonMessageOverlayError(
                    f"conflicting duplicate translation for id {entry_id}"
                )
            merged[entry_id] = public_entry

    public_entries = [merged[entry_id] for entry_id in sorted(merged)]
    if not public_entries:
        raise common.CommonMessageOverlayError("private batches contain no translations")

    stock_blob = stock_blobs["SC"]
    raw = raws["SC"]
    table = tables["SC"]

    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": overlay_id,
        "resource": resource,
        "base_language": "SC",
        "entry_count": len(public_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(stock_blob),
            "packed_sha256": common.sha256_bytes(stock_blob),
            "raw_size": len(raw),
            "raw_sha256": common.sha256_bytes(raw),
            "string_count": table.string_count,
        },
        "defaults": {"status": default_status},
        "entries": public_entries,
    }
    # Run the exact public-schema validator before committing bytes to disk.
    common.validate_overlay_shape(overlay)
    encoded = common.encode_json(overlay)
    for language, original_blob in stock_blobs.items():
        if common.sha256_file(resolved_stocks[language]) != common.sha256_bytes(
            original_blob
        ):
            raise common.CommonMessageOverlayError(
                f"{language} stock resource changed while the public overlay was exported"
            )
    common.atomic_write(output_path, encoded)
    return {
        "output_path": output_path,
        "output_sha256": common.sha256_bytes(encoded),
        "entry_count": len(public_entries),
        "resource": resource,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--private-batch",
        type=Path,
        action="append",
        required=True,
        help="Repeat for each nobu16.kr.translation.v1 catalog",
    )
    parser.add_argument("--stock-sc", type=Path, required=True)
    parser.add_argument("--stock-en", type=Path)
    parser.add_argument("--stock-jp", type=Path)
    parser.add_argument("--overlay-id", required=True)
    parser.add_argument(
        "--default-status",
        choices=sorted(common.BUILDABLE_STATUSES),
        default="translated",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        stock_paths = {"SC": args.stock_sc}
        if args.stock_en is not None:
            stock_paths["EN"] = args.stock_en
        if args.stock_jp is not None:
            stock_paths["JP"] = args.stock_jp
        result = export_overlay(
            args.private_batch,
            stock_paths,
            args.output,
            args.overlay_id,
            args.default_status,
        )
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        LZ4Error,
        MessageTableError,
        common.CommonMessageOverlayError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"output={result['output_path']}")
    print(f"sha256={result['output_sha256']}")
    print(f"entries={result['entry_count']}")
    print(f"resource={result['resource']}")
    print("contains_commercial_source_text=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
