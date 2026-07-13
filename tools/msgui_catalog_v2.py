#!/usr/bin/env python3
"""Create, validate, and build the development MSG_PK/SC msgui catalog.

The catalog is deliberately a development artifact: it contains the official
multilingual source strings so translators can work by stable numeric id.  A
public patch must contain only the compact file recipe generated from a pinned
target, never this complete source catalog.

All commands are offline.  They only read stock resources and write below an
explicit output directory; they never attach to a process, launch the game,
touch the registry, or modify an executable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

from nobu16_lz4 import LZ4Error, decompress_wrapper, recompress_wrapper
from nobu16_msg_table import MessageTableError, parse_message_table, rebuild_message_table


META_SCHEMA = "nobu16.kr.msgui-catalog-meta.v2"
ROW_SCHEMA = "nobu16.kr.msgui-catalog-row.v2"
BUILD_SCHEMA = "nobu16.kr.msgui-build-manifest.v2"
BATCH_SCHEMA = "nobu16.kr.msgui-translation-batch.v1"
OVERLAY_SCHEMA = "nobu16.kr.msgui-translation-overlay.v1"
LANGUAGES = ("EN", "JP", "SC", "TC")
BUILDABLE_STATUSES = frozenset(("translated", "reviewed"))
VALID_STATUSES = frozenset(("empty", "untranslated", "draft", "translated", "reviewed"))
INVARIANT_KEYS = (
    "printf",
    "unknown_percent_count",
    "esc",
    "pua",
    "other_controls",
    "line_breaks",
)
REFERENCE_OVERRIDE_LANGUAGES = frozenset(("EN", "JP", "TC"))
LEGACY_INVARIANT_OVERRIDES = frozenset(("line_breaks",))

# C printf conversions used by the game's UI strings.  The exact ordered token
# sequence is invariant because changing it can mismatch the native varargs.
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)


class CatalogError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


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


def write_json(path: Path, value: Any) -> None:
    atomic_write(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    payload = bytearray()
    for row in rows:
        payload.extend(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        payload.extend(b"\n")
    atomic_write(path, bytes(payload))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CatalogError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise CatalogError(f"{path}:{line_number}: row is not an object")
            rows.append(value)
    return rows


def stock_path(game_root: Path, language: str) -> Path:
    return game_root / "MSG_PK" / language / "msgui.bin"


def load_stock_tables(game_root: Path) -> tuple[dict[str, bytes], dict[str, bytes], dict[str, Any]]:
    packed: dict[str, bytes] = {}
    raw: dict[str, bytes] = {}
    tables: dict[str, Any] = {}
    for language in LANGUAGES:
        path = stock_path(game_root, language)
        packed[language] = path.read_bytes()
        _, raw[language] = decompress_wrapper(packed[language])
        tables[language] = parse_message_table(raw[language])
    counts = {table.string_count for table in tables.values()}
    if len(counts) != 1:
        raise CatalogError(f"language string counts differ: {sorted(counts)}")
    return packed, raw, tables


def printf_tokens(text: str) -> tuple[list[str], list[int]]:
    matches = list(PRINTF_RE.finditer(text))
    starts = {match.start() for match in matches}
    unknown = [index for index, char in enumerate(text) if char == "%" and index not in starts]
    return [match.group(0) for match in matches], unknown


def invariants(text: str) -> dict[str, Any]:
    printf, unknown_percent_positions = printf_tokens(text)
    esc = ESC_RE.findall(text)
    consumed_esc = {index for match in ESC_RE.finditer(text) for index in range(match.start(), match.end())}
    other_controls = [
        f"U+{ord(char):04X}"
        for index, char in enumerate(text)
        if ord(char) < 0x20 and char not in ("\n", "\r", "\t") and index not in consumed_esc
    ]
    return {
        "printf": printf,
        "unknown_percent_count": len(unknown_percent_positions),
        "esc": esc,
        "pua": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "other_controls": other_controls,
        "line_breaks": text.count("\n"),
    }


def supported_invariant_overrides() -> set[str]:
    """Return explicit, reviewable invariant override tokens.

    ``key:LANG`` never disables a check.  It changes the authoritative source
    for exactly one invariant from SC to a named stock-language string.  This
    is needed for a small number of official SC whitespace/internal-key slots
    whose visible UI contract survives in JP.  The legacy ``line_breaks``
    token remains readable for older reviewed catalogs, but new work should
    always use a language-qualified token.
    """

    return set(LEGACY_INVARIANT_OVERRIDES) | {
        f"{key}:{language}"
        for key in INVARIANT_KEYS
        for language in REFERENCE_OVERRIDE_LANGUAGES
    }


def compare_invariants(
    source: str,
    replacement: str,
    overrides: set[str],
    reference_sources: dict[str, str] | None = None,
) -> list[str]:
    before = invariants(source)
    after = invariants(replacement)
    issues: list[str] = []
    unsupported = sorted(overrides - supported_invariant_overrides())
    if unsupported:
        issues.append(f"unsupported invariant override(s): {unsupported!r}")
    for key in INVARIANT_KEYS:
        if key in overrides:
            # Backward-compatible reviewed exception.  New batches use the
            # source-qualified form below so the expected value is still
            # independently pinned to a stock string.
            continue
        qualified = sorted(
            token for token in overrides if token.startswith(f"{key}:")
        )
        if len(qualified) > 1:
            issues.append(f"{key}: multiple reference overrides {qualified!r}")
            continue
        expected = before[key]
        expected_label = "SC"
        if qualified:
            language = qualified[0].split(":", 1)[1]
            if reference_sources is None or not isinstance(reference_sources.get(language), str):
                issues.append(f"{key}: missing stock {language} reference source")
                continue
            expected = invariants(reference_sources[language])[key]
            expected_label = language
        if expected != after[key]:
            issues.append(f"{key}: {expected_label}={expected!r}, ko={after[key]!r}")
    return issues


def canonical_translation_state(
    source: dict[str, str], status: str, ko: str
) -> tuple[str, str]:
    """Canonicalize whitespace-only no-ops before they can become buildable.

    A translation containing only Unicode whitespace is never a translation.
    Fully structural source rows become ``empty``; asymmetric rows (for
    example SC whitespace with JP text) become ``untranslated``.  Activating
    an asymmetric row requires real text and, where applicable, an explicit
    source-qualified invariant override.
    """

    if ko.strip():
        return status, ko
    canonical_status = (
        "empty" if all(not source[language].strip() for language in LANGUAGES) else "untranslated"
    )
    return canonical_status, ""


def renderable_characters(text: str) -> list[str]:
    """Return font glyphs, excluding whitespace, UI controls, and game PUA icons."""
    consumed_esc = {
        index
        for match in ESC_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    return [
        char
        for index, char in enumerate(text)
        if index not in consumed_esc
        and not char.isspace()
        and not (ord(char) < 0x20 or 0x7F <= ord(char) <= 0x9F)
        and not (0xE000 <= ord(char) <= 0xF8FF)
    ]


def font_exclusion_reason(char: str) -> str:
    codepoint = ord(char)
    if 0xE000 <= codepoint <= 0xF8FF:
        return "game_private_icon"
    if codepoint < 0x20 or 0x7F <= codepoint <= 0x9F:
        return "ui_control"
    return "ui_escape_sequence_component"


def font_exclusion_inventory(raw_characters: set[str], font_characters: set[str]) -> list[dict[str, str]]:
    return [
        {
            "codepoint": f"U+{ord(char):04X}",
            "reason": font_exclusion_reason(char),
        }
        for char in sorted(raw_characters - font_characters, key=ord)
    ]


def load_seed_catalogs(paths: Sequence[Path]) -> dict[int, dict[str, Any]]:
    seeds: dict[int, dict[str, Any]] = {}
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("schema") != "nobu16.kr.translation.v1":
            raise CatalogError(f"unsupported seed schema in {path}")
        for entry in value.get("entries", []):
            entry_id = int(entry["id"])
            if entry_id in seeds:
                raise CatalogError(f"duplicate seed id {entry_id}")
            seeds[entry_id] = {
                "ko": entry["ko"],
                "source": entry["source"],
                "scope": value.get("scope", ""),
                "version": value.get("version", ""),
                "path": str(path).replace("\\", "/"),
            }
    return seeds


def cmd_init(args: argparse.Namespace) -> int:
    game_root = args.game_root.resolve()
    output_root = args.output_root.resolve()
    meta_path = output_root / "msgui.meta.json"
    catalog_path = output_root / "msgui.catalog.jsonl"
    if not args.force and (meta_path.exists() or catalog_path.exists()):
        raise CatalogError("catalog already exists; pass --force to regenerate")

    packed, raw, tables = load_stock_tables(game_root)
    seeds = load_seed_catalogs(args.seed_catalog)
    source_files: dict[str, Any] = {}
    for language in LANGUAGES:
        path = stock_path(game_root, language)
        source_files[language] = {
            "relative_path": str(path.relative_to(game_root)).replace("\\", "/"),
            "size": len(packed[language]),
            "sha256": sha256_bytes(packed[language]),
            "raw_size": len(raw[language]),
            "raw_sha256": sha256_bytes(raw[language]),
        }

    count = tables["SC"].string_count
    duplicate_counts = {
        language: Counter(tables[language].texts) for language in LANGUAGES
    }
    rows: list[dict[str, Any]] = []
    seeded = 0
    fully_empty = 0
    for entry_id in range(count):
        source = {language: tables[language].texts[entry_id] for language in LANGUAGES}
        seed = seeds.get(entry_id)
        if seed is not None:
            for language in LANGUAGES:
                if seed["source"].get(language) != source[language]:
                    raise CatalogError(f"seed source mismatch at id {entry_id} language {language}")
            ko = seed["ko"]
            status = "translated"
            seeded += 1
            context = {
                "category": seed["scope"],
                "screen": seed["scope"],
                "notes": f"seeded from {seed['path']} version {seed['version']}",
            }
            priority = "p0"
        elif all(not text.strip() for text in source.values()):
            ko = ""
            status = "empty"
            fully_empty += 1
            context = {"category": "", "screen": "", "notes": ""}
            priority = ""
        else:
            ko = ""
            status = "untranslated"
            context = {"category": "", "screen": "", "notes": ""}
            priority = ""

        rows.append(
            {
                "schema": ROW_SCHEMA,
                "id": entry_id,
                "source": source,
                "source_utf16le_sha256": {
                    language: text_hash(source[language]) for language in LANGUAGES
                },
                "source_duplicate_count": {
                    language: duplicate_counts[language][source[language]] for language in LANGUAGES
                },
                "base_invariants": invariants(source["SC"]),
                "ko": ko,
                "status": status,
                "priority": priority,
                "context": context,
                "invariant_overrides": [],
                "review": {"translator": "", "reviewer": "", "notes": ""},
            }
        )

    meta = {
        "schema": META_SCHEMA,
        "resource": "msgui",
        "version": "0.2-dev",
        "base_language": "SC",
        "languages": list(LANGUAGES),
        "string_count": count,
        "source_files": source_files,
        "development_only": True,
        "distribution_policy": {
            "contains_complete_commercial_source_text": True,
            "include_in_public_patch": False,
            "public_output_must_be_compact_recipe_only": True,
        },
        "build_policy": {
            "buildable_statuses": sorted(BUILDABLE_STATUSES),
            "preserve_printf_sequence": True,
            "preserve_escape_sequence": True,
            "preserve_private_use_sequence": True,
            "preserve_line_break_count_unless_reviewed_override": True,
        },
        "seed_catalogs": [str(path).replace("\\", "/") for path in args.seed_catalog],
    }
    write_json(meta_path, meta)
    write_jsonl(catalog_path, rows)
    print(f"meta={meta_path}")
    print(f"catalog={catalog_path}")
    print(f"strings={count}")
    print(f"fully_empty={fully_empty}")
    print(f"seeded={seeded}")
    print("installed_game_files_modified=False")
    return 0


def load_catalog(meta_path: Path, catalog_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("schema") != META_SCHEMA:
        raise CatalogError("unsupported catalog metadata schema")
    rows = read_jsonl(catalog_path)
    return meta, rows


def validate_catalog(
    meta: dict[str, Any],
    rows: Sequence[dict[str, Any]],
    tables: dict[str, Any] | None,
) -> dict[str, Any]:
    expected_count = int(meta["string_count"])
    errors: list[str] = []
    warnings: list[str] = []
    counts: Counter[str] = Counter()
    ids: set[int] = set()
    buildable_ids: list[int] = []
    glyphs: set[str] = set()
    raw_non_whitespace: set[str] = set()

    if len(rows) != expected_count:
        errors.append(f"row count {len(rows)} != {expected_count}")
    for row_number, row in enumerate(rows, 1):
        try:
            if row.get("schema") != ROW_SCHEMA:
                raise CatalogError("unsupported row schema")
            entry_id = int(row["id"])
            if isinstance(row["id"], bool) or entry_id != row["id"]:
                raise CatalogError("id must be a JSON integer")
            if entry_id in ids:
                raise CatalogError("duplicate id")
            ids.add(entry_id)
            if not 0 <= entry_id < expected_count:
                raise CatalogError("id outside catalog range")
            source = row["source"]
            source_hashes = row["source_utf16le_sha256"]
            for language in LANGUAGES:
                if not isinstance(source.get(language), str):
                    raise CatalogError(f"{language} source is not a string")
                if source_hashes.get(language) != text_hash(source[language]):
                    raise CatalogError(f"{language} source hash mismatch")
                if tables is not None and source[language] != tables[language].texts[entry_id]:
                    raise CatalogError(f"{language} source differs from stock")
            if row.get("base_invariants") != invariants(source["SC"]):
                raise CatalogError("stored SC invariants are stale")
            status = row.get("status")
            if status not in VALID_STATUSES:
                raise CatalogError(f"invalid status {status!r}")
            counts[status] += 1
            ko = row.get("ko")
            if not isinstance(ko, str) or "\x00" in ko:
                raise CatalogError("ko must be a NUL-free string")
            overrides_value = row.get("invariant_overrides", [])
            if not isinstance(overrides_value, list) or not all(isinstance(v, str) for v in overrides_value):
                raise CatalogError("invariant_overrides must be a string list")
            overrides = set(overrides_value)
            if overrides - supported_invariant_overrides():
                raise CatalogError(
                    f"unsupported invariant override(s): "
                    f"{sorted(overrides - supported_invariant_overrides())}"
                )
            if overrides and status != "reviewed":
                raise CatalogError("invariant overrides require reviewed status")
            if status == "empty":
                if ko or any(source[language].strip() for language in LANGUAGES):
                    raise CatalogError(
                        "empty status requires every source and ko to be whitespace-empty"
                    )
            elif status in BUILDABLE_STATUSES:
                if not ko.strip():
                    raise CatalogError("buildable status requires a non-whitespace Korean translation")
                invariant_issues = compare_invariants(
                    source["SC"], ko, overrides, source
                )
                if invariant_issues:
                    raise CatalogError("invariant mismatch: " + "; ".join(invariant_issues))
                buildable_ids.append(entry_id)
                raw_non_whitespace.update(char for char in ko if not char.isspace())
                glyphs.update(renderable_characters(ko))
            elif status == "untranslated" and ko:
                raise CatalogError("untranslated status requires canonical empty ko")
        except (CatalogError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"row {row_number}: {exc}")

    missing_ids = sorted(set(range(expected_count)) - ids)
    if missing_ids:
        errors.append(f"missing ids: {missing_ids[:20]}")
    exclusions = font_exclusion_inventory(raw_non_whitespace, glyphs)
    return {
        "schema": "nobu16.kr.msgui-catalog-validation.v2",
        "valid": not errors,
        "row_count": len(rows),
        "expected_count": expected_count,
        "status_counts": dict(sorted(counts.items())),
        "buildable_count": len(buildable_ids),
        "buildable_ids": buildable_ids,
        "required_glyph_count": len(glyphs),
        "required_codepoints": [f"U+{ord(char):04X}" for char in sorted(glyphs, key=ord)],
        "source_non_whitespace_character_count": len(raw_non_whitespace),
        "excluded_font_token_count": len(exclusions),
        "excluded_font_tokens": exclusions,
        "errors": errors,
        "warnings": warnings,
    }


def verify_stock(meta: dict[str, Any], game_root: Path) -> tuple[dict[str, bytes], dict[str, bytes], dict[str, Any]]:
    packed, raw, tables = load_stock_tables(game_root)
    for language in LANGUAGES:
        spec = meta["source_files"][language]
        if len(packed[language]) != int(spec["size"]) or sha256_bytes(packed[language]) != spec["sha256"]:
            raise CatalogError(f"stock {language} packed resource hash/size mismatch")
        if len(raw[language]) != int(spec["raw_size"]) or sha256_bytes(raw[language]) != spec["raw_sha256"]:
            raise CatalogError(f"stock {language} raw resource hash/size mismatch")
    return packed, raw, tables


def cmd_validate(args: argparse.Namespace) -> int:
    meta, rows = load_catalog(args.meta.resolve(), args.catalog.resolve())
    tables = None
    if args.game_root is not None:
        _, _, tables = verify_stock(meta, args.game_root.resolve())
    report = validate_catalog(meta, rows, tables)
    if args.report:
        write_json(args.report.resolve(), report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["valid"] else 1


def cmd_merge_batch(args: argparse.Namespace) -> int:
    meta_path = args.meta.resolve()
    catalog_path = args.catalog.resolve()
    output_path = args.output.resolve()
    if output_path == catalog_path and not args.in_place:
        raise CatalogError("refusing in-place catalog update without --in-place")
    meta, rows = load_catalog(meta_path, catalog_path)
    batch = json.loads(args.batch.resolve().read_text(encoding="utf-8"))
    if batch.get("schema") != BATCH_SCHEMA:
        raise CatalogError("unsupported translation batch schema")
    if batch.get("resource") != "msgui" or batch.get("base_language") != "SC":
        raise CatalogError("translation batch resource/base language mismatch")
    by_id = {int(row["id"]): row for row in rows}
    defaults = batch.get("defaults", {})
    if not isinstance(defaults, dict):
        raise CatalogError("translation batch defaults must be an object")
    changed: list[dict[str, Any]] = []
    seen: set[int] = set()
    for item in batch.get("entries", []):
        entry_id = int(item["id"])
        if entry_id in seen:
            raise CatalogError(f"duplicate batch id {entry_id}")
        seen.add(entry_id)
        if entry_id not in by_id:
            raise CatalogError(f"batch id {entry_id} is outside the catalog")
        row = by_id[entry_id]
        expected_en = item.get("source_en")
        if expected_en != row["source"]["EN"]:
            raise CatalogError(
                f"id {entry_id}: English source mismatch {expected_en!r} != {row['source']['EN']!r}"
            )
        expected_sc_hash = item.get("source_sc_utf16le_sha256")
        if expected_sc_hash is not None and str(expected_sc_hash).upper() != row["source_utf16le_sha256"]["SC"]:
            raise CatalogError(f"id {entry_id}: SC source hash mismatch")
        status = item.get("status", defaults.get("status", "translated"))
        if status not in VALID_STATUSES:
            raise CatalogError(f"id {entry_id}: invalid batch status {status!r}")
        ko = item.get("ko")
        if not isinstance(ko, str) or "\x00" in ko:
            raise CatalogError(f"id {entry_id}: invalid Korean translation")
        status, ko = canonical_translation_state(row["source"], status, ko)
        if ko and status not in BUILDABLE_STATUSES:
            raise CatalogError(f"id {entry_id}: non-empty batch text must be translated or reviewed")
        if row["status"] == "reviewed" and status != "reviewed" and not args.allow_downgrade:
            raise CatalogError(f"id {entry_id}: refusing to downgrade reviewed translation")
        overrides = item.get("invariant_overrides", defaults.get("invariant_overrides", []))
        if not isinstance(overrides, list) or not all(isinstance(value, str) for value in overrides):
            raise CatalogError(f"id {entry_id}: invariant_overrides must be a string list")
        if overrides and status != "reviewed":
            raise CatalogError(f"id {entry_id}: invariant overrides require reviewed status")
        if status in BUILDABLE_STATUSES:
            problems = compare_invariants(
                row["source"]["SC"], ko, set(overrides), row["source"]
            )
            if problems:
                raise CatalogError(f"id {entry_id}: invariant mismatch: {'; '.join(problems)}")

        before = {
            key: row.get(key)
            for key in ("ko", "status", "priority", "context", "review", "invariant_overrides")
        }
        row["ko"] = ko
        row["status"] = status
        row["priority"] = item.get("priority", defaults.get("priority", row.get("priority", "")))
        context = item.get("context", defaults.get("context"))
        if context is not None:
            if not isinstance(context, dict):
                raise CatalogError(f"id {entry_id}: context must be an object")
            row["context"] = {
                "category": str(context.get("category", "")),
                "screen": str(context.get("screen", "")),
                "notes": str(context.get("notes", "")),
            }
        review = item.get("review", defaults.get("review"))
        if review is not None:
            if not isinstance(review, dict):
                raise CatalogError(f"id {entry_id}: review must be an object")
            row["review"] = {
                "translator": str(review.get("translator", "")),
                "reviewer": str(review.get("reviewer", "")),
                "notes": str(review.get("notes", "")),
            }
        row["invariant_overrides"] = overrides
        after = {
            key: row.get(key)
            for key in ("ko", "status", "priority", "context", "review", "invariant_overrides")
        }
        if before != after:
            changed.append({"id": entry_id, "before": before, "after": after})

    tables = None
    if args.game_root is not None:
        _, _, tables = verify_stock(meta, args.game_root.resolve())
    validation = validate_catalog(meta, rows, tables)
    if not validation["valid"]:
        raise CatalogError("merged catalog is invalid: " + " | ".join(validation["errors"][:10]))
    write_jsonl(output_path, rows)
    report = {
        "schema": "nobu16.kr.msgui-batch-merge-report.v1",
        "batch_id": batch.get("batch_id", ""),
        "batch_path": str(args.batch.resolve()),
        "input_catalog": str(catalog_path),
        "output_catalog": str(output_path),
        "batch_entry_count": len(seen),
        "changed_count": len(changed),
        "changed_ids": [item["id"] for item in changed],
        "validation": validation,
    }
    if args.report:
        write_json(args.report.resolve(), report)
    print(f"output={output_path}")
    print(f"batch_entries={len(seen)}")
    print(f"changed={len(changed)}")
    print(f"buildable={validation['buildable_count']}")
    print("validation=OK")
    return 0


def cmd_merge_overlay(args: argparse.Namespace) -> int:
    """Merge a public translation overlay without redistributing source text."""

    meta_path = args.meta.resolve()
    catalog_path = args.catalog.resolve()
    output_path = args.output.resolve()
    if output_path == catalog_path and not args.in_place:
        raise CatalogError("refusing in-place catalog update without --in-place")
    meta, rows = load_catalog(meta_path, catalog_path)
    overlay = json.loads(args.overlay.resolve().read_text(encoding="utf-8"))
    if overlay.get("schema") != OVERLAY_SCHEMA:
        raise CatalogError("unsupported public translation overlay schema")
    if overlay.get("resource") != "msgui" or overlay.get("base_language") != "SC":
        raise CatalogError("translation overlay resource/base language mismatch")

    stock_sc = overlay.get("stock_sc", {})
    expected_sc = meta["source_files"]["SC"]
    if stock_sc.get("packed_sha256") != expected_sc["sha256"]:
        raise CatalogError("overlay SC packed stock hash does not match catalog metadata")
    if stock_sc.get("raw_sha256") != expected_sc["raw_sha256"]:
        raise CatalogError("overlay SC raw stock hash does not match catalog metadata")

    by_id = {int(row["id"]): row for row in rows}
    defaults = overlay.get("defaults", {})
    if not isinstance(defaults, dict):
        raise CatalogError("translation overlay defaults must be an object")
    changed_ids: list[int] = []
    seen: set[int] = set()
    for item in overlay.get("entries", []):
        entry_id = int(item["id"])
        if entry_id in seen:
            raise CatalogError(f"duplicate overlay id {entry_id}")
        seen.add(entry_id)
        if entry_id not in by_id:
            raise CatalogError(f"overlay id {entry_id} is outside the catalog")
        row = by_id[entry_id]
        source_hash = str(item.get("source_sc_utf16le_sha256", "")).upper()
        if source_hash != row["source_utf16le_sha256"]["SC"]:
            raise CatalogError(f"id {entry_id}: SC source hash mismatch")

        status = item.get("status", defaults.get("status", "translated"))
        if status not in BUILDABLE_STATUSES:
            raise CatalogError(f"id {entry_id}: overlay status must be translated or reviewed")
        if row["status"] == "reviewed" and status != "reviewed" and not args.allow_downgrade:
            raise CatalogError(f"id {entry_id}: refusing to downgrade reviewed translation")
        ko = item.get("ko")
        if not isinstance(ko, str) or not ko.strip() or "\x00" in ko:
            raise CatalogError(f"id {entry_id}: invalid Korean translation")
        overrides = item.get("invariant_overrides", defaults.get("invariant_overrides", []))
        if not isinstance(overrides, list) or not all(isinstance(value, str) for value in overrides):
            raise CatalogError(f"id {entry_id}: invariant_overrides must be a string list")
        if overrides and status != "reviewed":
            raise CatalogError(f"id {entry_id}: invariant overrides require reviewed status")
        problems = compare_invariants(
            row["source"]["SC"], ko, set(overrides), row["source"]
        )
        if problems:
            raise CatalogError(f"id {entry_id}: invariant mismatch: {'; '.join(problems)}")

        before = (row.get("ko"), row.get("status"), row.get("priority"), row.get("invariant_overrides"))
        row["ko"] = ko
        row["status"] = status
        row["priority"] = item.get("priority", defaults.get("priority", row.get("priority", "")))
        row["invariant_overrides"] = overrides
        after = (row.get("ko"), row.get("status"), row.get("priority"), row.get("invariant_overrides"))
        if before != after:
            changed_ids.append(entry_id)

    declared_count = overlay.get("entry_count")
    if declared_count is not None and int(declared_count) != len(seen):
        raise CatalogError(f"overlay entry_count {declared_count} != actual {len(seen)}")
    tables = None
    if args.game_root is not None:
        _, _, tables = verify_stock(meta, args.game_root.resolve())
    validation = validate_catalog(meta, rows, tables)
    if not validation["valid"]:
        raise CatalogError("merged catalog is invalid: " + " | ".join(validation["errors"][:10]))
    write_jsonl(output_path, rows)
    report = {
        "schema": "nobu16.kr.msgui-overlay-merge-report.v1",
        "overlay_id": overlay.get("overlay_id", ""),
        "overlay_entry_count": len(seen),
        "changed_count": len(changed_ids),
        "changed_ids": changed_ids,
        "validation": validation,
    }
    if args.report:
        write_json(args.report.resolve(), report)
    print(f"output={output_path}")
    print(f"overlay_entries={len(seen)}")
    print(f"changed={len(changed_ids)}")
    print(f"buildable={validation['buildable_count']}")
    print("validation=OK")
    return 0


def parse_id_ranges(values: Sequence[str], limit: int) -> set[int]:
    ids: set[int] = set()
    for value in values:
        match = re.fullmatch(r"(\d+)(?::(\d+))?", value.strip())
        if match is None:
            raise CatalogError(f"invalid id range {value!r}; use N or START:END")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start > end or start < 0 or end >= limit:
            raise CatalogError(f"id range is outside 0..{limit - 1}: {value!r}")
        ids.update(range(start, end + 1))
    return ids


def cmd_export_batch(args: argparse.Namespace) -> int:
    meta, rows = load_catalog(args.meta.resolve(), args.catalog.resolve())
    selected_ids = parse_id_ranges(args.id_range, int(meta["string_count"]))
    entries: list[dict[str, Any]] = []
    for row in rows:
        entry_id = int(row["id"])
        if entry_id not in selected_ids:
            continue
        if not args.include_translated and row["status"] in BUILDABLE_STATUSES:
            continue
        states = {
            language: (
                "empty"
                if row["source"][language] == ""
                else "whitespace"
                if row["source"][language].strip() == ""
                else "text"
            )
            for language in LANGUAGES
        }
        if not args.include_structural and not any(state == "text" for state in states.values()):
            continue
        entries.append(
            {
                "id": entry_id,
                "source_en": row["source"]["EN"],
                "source_sc_utf16le_sha256": row["source_utf16le_sha256"]["SC"],
                "source_reference": row["source"],
                "source_state": states,
                "base_invariants": row["base_invariants"],
                "current_status": row["status"],
                "current_ko": row["ko"],
                "ko": "",
            }
        )
    value = {
        "schema": BATCH_SCHEMA,
        "resource": "msgui",
        "base_language": "SC",
        "batch_id": args.batch_id,
        "description": args.description,
        "development_only": True,
        "distribution_policy": {
            "contains_commercial_source_text": True,
            "include_in_public_patch": False,
        },
        "source_catalog": {
            "meta_sha256": sha256_bytes(args.meta.resolve().read_bytes()),
            "catalog_sha256": sha256_bytes(args.catalog.resolve().read_bytes()),
        },
        "defaults": {
            "status": "translated",
            "priority": args.priority,
            "context": {
                "category": args.category,
                "screen": args.screen,
                "notes": "화면/문맥 검수 전 초벌 번역",
            },
            "review": {"translator": "", "reviewer": "", "notes": ""},
            "invariant_overrides": [],
        },
        "entries": entries,
    }
    write_json(args.output.resolve(), value)
    print(f"output={args.output.resolve()}")
    print(f"selected_ranges={len(selected_ids)}")
    print(f"exported_entries={len(entries)}")
    print("development_only=True")
    return 0


def glyph_demand(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    raw_chars = {
        char
        for row in rows
        if row["status"] in BUILDABLE_STATUSES
        for char in row["ko"]
        if not char.isspace()
    }
    font_chars = {
        char
        for row in rows
        if row["status"] in BUILDABLE_STATUSES
        for char in renderable_characters(row["ko"])
    }
    chars = sorted(font_chars, key=ord)
    exclusions = font_exclusion_inventory(raw_chars, font_chars)
    exclusions_blob = json.dumps(
        exclusions, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    source_codepoint_lines = "".join(
        f"U+{ord(char):04X}\n" for char in sorted(raw_chars, key=ord)
    ).encode("ascii")
    hangul_syllables = [char for char in chars if 0xAC00 <= ord(char) <= 0xD7A3]
    hangul_jamo = [
        char
        for char in chars
        if 0x1100 <= ord(char) <= 0x11FF
        or 0x3130 <= ord(char) <= 0x318F
        or 0xA960 <= ord(char) <= 0xA97F
        or 0xD7B0 <= ord(char) <= 0xD7FF
    ]
    return {
        "schema": "nobu16.kr.glyph-demand.v1",
        "source": "buildable ko strings in msgui catalog v2",
        "source_non_whitespace_character_count": len(raw_chars),
        "source_non_whitespace_codepoints_sha256": sha256_bytes(source_codepoint_lines),
        "font_exclusion_policy": "exclude ESC command components, C0/C1 controls, and game PUA icons from G1N raster demand",
        "excluded_font_token_count": len(exclusions),
        "excluded_font_tokens": exclusions,
        "excluded_font_tokens_sha256": sha256_bytes(exclusions_blob),
        "character_count": len(chars),
        "characters": chars,
        "codepoints": [f"U+{ord(char):04X}" for char in chars],
        "hangul_syllable_count": len(hangul_syllables),
        "hangul_syllables": hangul_syllables,
        "hangul_syllable_codepoints": [f"U+{ord(char):04X}" for char in hangul_syllables],
        "hangul_jamo_count": len(hangul_jamo),
        "hangul_jamo": hangul_jamo,
        "hangul_jamo_codepoints": [f"U+{ord(char):04X}" for char in hangul_jamo],
    }


def cmd_build(args: argparse.Namespace) -> int:
    meta_path = args.meta.resolve()
    catalog_path = args.catalog.resolve()
    game_root = args.game_root.resolve()
    output_root = args.output_root.resolve()
    meta, rows = load_catalog(meta_path, catalog_path)
    packed, raw, tables = verify_stock(meta, game_root)
    report = validate_catalog(meta, rows, tables)
    if not report["valid"]:
        raise CatalogError("catalog validation failed: " + " | ".join(report["errors"][:10]))

    source_path = stock_path(game_root, "SC").resolve()
    output_path = (output_root / "MSG_PK" / "SC" / "msgui.bin").resolve()
    if source_path == output_path:
        raise CatalogError("refusing to overwrite the installed stock msgui")
    table = tables["SC"]
    texts = list(table.texts)
    changed: list[dict[str, Any]] = []
    for row in rows:
        if row["status"] not in BUILDABLE_STATUSES:
            continue
        replacement = row["ko"]
        entry_id = int(row["id"])
        if replacement == texts[entry_id]:
            continue
        changed.append(
            {
                "id": entry_id,
                "status": row["status"],
                "source_utf16le_sha256": text_hash(texts[entry_id]),
                "replacement": replacement,
                "replacement_utf16le_sha256": text_hash(replacement),
            }
        )
        texts[entry_id] = replacement

    rebuilt_raw = rebuild_message_table(table, texts)
    check = parse_message_table(rebuilt_raw)
    if check.texts != tuple(texts):
        raise CatalogError("rebuilt raw msgui parse verification failed")
    rebuilt_packed = recompress_wrapper(rebuilt_raw, packed["SC"])
    _, decompressed_check = decompress_wrapper(rebuilt_packed)
    if decompressed_check != rebuilt_raw:
        raise CatalogError("rebuilt packed msgui decompression verification failed")
    atomic_write(output_path, rebuilt_packed)

    demand = glyph_demand(rows)
    write_json(output_root / "glyph_demand.json", demand)
    operation_ids = [item["id"] for item in changed]
    operation_ids_blob = json.dumps(operation_ids, separators=(",", ":")).encode("utf-8")
    manifest = {
        "schema": BUILD_SCHEMA,
        "resource": "MSG_PK/SC/msgui.bin",
        "catalog_version": meta["version"],
        "file_only": True,
        "process_memory_access": False,
        "registry_modified": False,
        "executable_modified": False,
        "installed_game_files_modified": False,
        "source": {
            "size": len(packed["SC"]),
            "sha256": sha256_bytes(packed["SC"]),
            "raw_size": len(raw["SC"]),
            "raw_sha256": sha256_bytes(raw["SC"]),
            "string_count": table.string_count,
        },
        "target": {
            "relative_path": "MSG_PK/SC/msgui.bin",
            "size": len(rebuilt_packed),
            "sha256": sha256_bytes(rebuilt_packed),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256_bytes(rebuilt_raw),
        },
        "changed_count": len(changed),
        "operation_index": {
            "count": len(operation_ids),
            "id_encoding": "UTF-8 compact JSON integer array",
            "ids_sha256": sha256_bytes(operation_ids_blob),
            "sorted_unique": operation_ids == sorted(set(operation_ids)),
        },
        "changed": changed,
        "glyph_demand": {
            "path": "glyph_demand.json",
            "source_non_whitespace_character_count": demand["source_non_whitespace_character_count"],
            "source_non_whitespace_codepoints_sha256": demand["source_non_whitespace_codepoints_sha256"],
            "excluded_font_token_count": demand["excluded_font_token_count"],
            "excluded_font_tokens": demand["excluded_font_tokens"],
            "excluded_font_tokens_sha256": demand["excluded_font_tokens_sha256"],
            "character_count": demand["character_count"],
            "hangul_syllable_count": demand["hangul_syllable_count"],
        },
        "verification": {
            "all_stock_hashes": "OK",
            "all_source_strings": "OK",
            "format_invariants": "OK",
            "table_parse_roundtrip": "OK",
            "wrapper_decompress_roundtrip": "OK",
        },
    }
    write_json(output_root / "msgui.build-manifest.json", manifest)
    print(f"output={output_path}")
    print(f"sha256={manifest['target']['sha256']}")
    print(f"changed={len(changed)}")
    print(f"glyphs={demand['character_count']}")
    print(f"hangul_syllables={demand['hangul_syllable_count']}")
    print("installed_game_files_modified=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="extract the aligned four-language development catalog")
    init.add_argument("--game-root", type=Path, required=True)
    init.add_argument("--output-root", type=Path, required=True)
    init.add_argument("--seed-catalog", type=Path, action="append", default=[])
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    validate = sub.add_parser("validate", help="validate ids, source hashes, statuses, and native tokens")
    validate.add_argument("--meta", type=Path, required=True)
    validate.add_argument("--catalog", type=Path, required=True)
    validate.add_argument("--game-root", type=Path)
    validate.add_argument("--report", type=Path)
    validate.set_defaults(func=cmd_validate)

    merge = sub.add_parser("merge-batch", help="hash-gate and merge a compact translation batch")
    merge.add_argument("--meta", type=Path, required=True)
    merge.add_argument("--catalog", type=Path, required=True)
    merge.add_argument("--batch", type=Path, required=True)
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--game-root", type=Path)
    merge.add_argument("--report", type=Path)
    merge.add_argument("--in-place", action="store_true")
    merge.add_argument("--allow-downgrade", action="store_true")
    merge.set_defaults(func=cmd_merge_batch)

    merge_overlay = sub.add_parser(
        "merge-overlay", help="hash-gate and merge a public source-text-free translation overlay"
    )
    merge_overlay.add_argument("--meta", type=Path, required=True)
    merge_overlay.add_argument("--catalog", type=Path, required=True)
    merge_overlay.add_argument("--overlay", type=Path, required=True)
    merge_overlay.add_argument("--output", type=Path, required=True)
    merge_overlay.add_argument("--game-root", type=Path)
    merge_overlay.add_argument("--report", type=Path)
    merge_overlay.add_argument("--in-place", action="store_true")
    merge_overlay.add_argument("--allow-downgrade", action="store_true")
    merge_overlay.set_defaults(func=cmd_merge_overlay)

    export_batch = sub.add_parser(
        "export-batch", help="export a development-only multilingual translator work pack"
    )
    export_batch.add_argument("--meta", type=Path, required=True)
    export_batch.add_argument("--catalog", type=Path, required=True)
    export_batch.add_argument("--id-range", action="append", required=True)
    export_batch.add_argument("--batch-id", required=True)
    export_batch.add_argument("--description", default="")
    export_batch.add_argument("--priority", default="p2")
    export_batch.add_argument("--category", default="")
    export_batch.add_argument("--screen", default="")
    export_batch.add_argument("--include-translated", action="store_true")
    export_batch.add_argument("--include-structural", action="store_true")
    export_batch.add_argument("--output", type=Path, required=True)
    export_batch.set_defaults(func=cmd_export_batch)

    build = sub.add_parser("build", help="build a separate SC msgui from translated/reviewed rows")
    build.add_argument("--game-root", type=Path, required=True)
    build.add_argument("--meta", type=Path, required=True)
    build.add_argument("--catalog", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.set_defaults(func=cmd_build)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, CatalogError, KeyError, TypeError, json.JSONDecodeError, LZ4Error, MessageTableError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
