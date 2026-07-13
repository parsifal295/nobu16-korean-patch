#!/usr/bin/env python3
"""Build a metadata-only, development MSGUI inventory sidecar.

The complete commercial multilingual strings already live in the explicitly
development-only catalog_v2.  This tool does not duplicate those strings.  It
emits stable-id metadata (hashes, raw offsets, lengths, native token profiles,
duplicate collision groups, structural classes, and suggested work priority)
under workstreams/msgui_full/inventory.

It reads only existing decompressed raw tables and a selected catalog.  It
never reads or writes the installed game, registry, executable, or process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

from msgui_catalog_v2 import (
    BUILDABLE_STATUSES,
    ESC_RE,
    LANGUAGES,
    PRINTF_RE,
    glyph_demand,
    invariants,
    read_jsonl,
    text_hash,
)
from nobu16_msg_table import parse_message_table


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
WORKSTREAM_ROOT = PROJECT_ROOT / "KR_PATCH_WORK" / "workstreams" / "msgui_full"
DEFAULT_META = WORKSTREAM_ROOT / "catalog_v2" / "msgui.meta.json"
DEFAULT_CATALOG = WORKSTREAM_ROOT / "catalog_v2" / "msgui.catalog.p3.jsonl"
DEFAULT_OUTPUT = WORKSTREAM_ROOT / "inventory"
DEFAULT_RAW = {
    language: PROJECT_ROOT / "KR_PATCH_WORK" / "tmp" / "mainmenu_v01" / f"msgui_{language}.raw"
    for language in LANGUAGES
}

RECORD_SCHEMA = "nobu16.kr.msgui-inventory-record.v1"
SUMMARY_SCHEMA = "nobu16.kr.msgui-inventory-summary.v1"
MANIFEST_SCHEMA = "nobu16.kr.msgui-inventory-manifest.v1"
MAIN_MENU_IDS = frozenset((1, 2, 5, 56, 85, 87, 88, 97, 178))


CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "officer_personnel",
        (
            "officer", "retainer", "vassal", "daimyo", "lord", "warrior",
            "general", "commander", "governor", "loyalty", "appoint", "dismiss",
            "employ", "recruit", "family", "spouse", "heir", "talent",
        ),
    ),
    (
        "battle_military",
        (
            "battle", "war", "army", "unit", "troop", "soldier", "march",
            "deploy", "attack", "defend", "siege", "sortie", "formation",
            "morale", "weapon", "cavalry", "musket", "navy", "ship", "camp",
        ),
    ),
    (
        "castle_territory",
        (
            "castle", "province", "district", "county", "territory", "domain",
            "region", "capital", "gate", "port", "road", "facility", "base",
        ),
    ),
    (
        "domestic_economy",
        (
            "develop", "commerce", "agriculture", "farm", "market", "gold",
            "money", "rice", "supplies", "resource", "labor", "population",
            "construction", "build", "harvest", "income", "expense", "economy",
            "trade",
        ),
    ),
    (
        "diplomacy",
        (
            "diplomacy", "alliance", "truce", "negotiation", "envoy", "marriage",
            "coalition", "relation", "goodwill", "surrender", "peace",
        ),
    ),
    (
        "policy_administration",
        (
            "policy", "council", "decree", "law", "strategy", "tactic",
            "administration", "govern", "affairs", "mission", "objective",
        ),
    ),
    (
        "system_save_load_settings",
        (
            "save", "load", "setting", "option", "config", "resolution",
            "fullscreen", "window", "audio", "sound", "music", "voice", "volume",
            "language", "quit", "exit", "title screen", "new game", "continue",
            "autosave", "version",
        ),
    ),
    (
        "tutorial_event_help",
        (
            "tutorial", "help", "tip", "event", "history", "scenario", "quest",
            "guide", "manual", "explanation", "description",
        ),
    ),
    (
        "editor_gallery_extras",
        (
            "edit", "editor", "gallery", "movie", "portrait", "extras",
            "encyclopedia", "collection", "achievement",
        ),
    ),
    (
        "time_status",
        (
            "year", "month", "day", "turn", "season", "time", "age", "status",
            "duration", "remaining", "deadline",
        ),
    ),
    (
        "navigation_confirmation",
        (
            "ok", "yes", "no", "cancel", "confirm", "close", "back", "next",
            "previous", "agree", "decline", "sort", "select", "details", "switch",
            "move", "proceed", "finish", "apply", "reset", "clear", "return",
        ),
    ),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


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
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, value: Any) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    payload = bytearray()
    for row in rows:
        payload.extend(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        payload.extend(b"\n")
    atomic_write(path, bytes(payload))


def source_state(text: str) -> str:
    if text == "":
        return "empty"
    if text.strip() == "":
        return "whitespace"
    return "text"


def utf16_units(text: str) -> int:
    return len(text.encode("utf-16le")) // 2


def length_metrics(text: str) -> dict[str, int]:
    lines = text.split("\n")
    return {
        "codepoints": len(text),
        "utf16_units": utf16_units(text),
        "utf16_bytes": len(text.encode("utf-16le")),
        "line_count": len(lines),
        "line_breaks": text.count("\n"),
        "max_line_codepoints": max((len(line) for line in lines), default=0),
    }


def token_profile(text: str) -> dict[str, Any]:
    base = invariants(text)
    printf_matches = list(PRINTF_RE.finditer(text))
    printf_starts = {match.start() for match in printf_matches}
    unknown_percent_positions = [
        index for index, char in enumerate(text) if char == "%" and index not in printf_starts
    ]
    esc_tokens = [f"ESC_C_U+{ord(match.group(0)[2]):04X}" for match in ESC_RE.finditer(text)]
    return {
        "printf": base["printf"],
        "printf_count": len(base["printf"]),
        "unknown_percent_count": len(unknown_percent_positions),
        "unknown_percent_positions": unknown_percent_positions,
        "esc": esc_tokens,
        "esc_count": len(esc_tokens),
        "pua": base["pua"],
        "pua_count": len(base["pua"]),
        "other_controls": base["other_controls"],
        "line_breaks": base["line_breaks"],
        "carriage_returns": text.count("\r"),
        "tabs": text.count("\t"),
    }


def signature_hash(parts: Sequence[str]) -> str:
    encoded = json.dumps(list(parts), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def percentile(values: Sequence[int], percent: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    rank = max(0, math.ceil(percent * len(ordered)) - 1)
    return ordered[rank]


def summarize_lengths(texts: Sequence[str]) -> dict[str, Any]:
    all_values = [len(text) for text in texts]
    substantive = [len(text) for text in texts if source_state(text) == "text"]
    buckets = {
        "1_4": sum(1 <= value <= 4 for value in substantive),
        "5_8": sum(5 <= value <= 8 for value in substantive),
        "9_16": sum(9 <= value <= 16 for value in substantive),
        "17_32": sum(17 <= value <= 32 for value in substantive),
        "33_64": sum(33 <= value <= 64 for value in substantive),
        "65_128": sum(65 <= value <= 128 for value in substantive),
        "129_plus": sum(value >= 129 for value in substantive),
    }
    return {
        "all_rows_mean_codepoints": round(statistics.mean(all_values), 4) if all_values else 0,
        "all_rows_median_codepoints": statistics.median(all_values) if all_values else 0,
        "all_rows_p90_codepoints": percentile(all_values, 0.90),
        "all_rows_p95_codepoints": percentile(all_values, 0.95),
        "all_rows_max_codepoints": max(all_values, default=0),
        "substantive_count": len(substantive),
        "mean_codepoints": round(statistics.mean(substantive), 4) if substantive else 0,
        "median_codepoints": statistics.median(substantive) if substantive else 0,
        "p90_codepoints": percentile(substantive, 0.90),
        "p95_codepoints": percentile(substantive, 0.95),
        "p99_codepoints": percentile(substantive, 0.99),
        "max_codepoints": max(substantive, default=0),
        "buckets": buckets,
    }


def contains_keyword(text: str, keyword: str) -> bool:
    escaped = re.escape(keyword)
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text) is not None


def automatic_category(entry_id: int, sources: dict[str, str], states: dict[str, str]) -> tuple[str, str]:
    if entry_id in MAIN_MENU_IDS:
        return "main_menu", "validated_id_set"
    if all(state == "empty" for state in states.values()):
        return "empty", "structural"
    if all(state != "text" for state in states.values()):
        return "whitespace_only", "structural"
    en = sources["EN"].casefold()
    if re.search(r"(?<![a-z0-9])(dummy|debug|unused|reserved|placeholder)(?![a-z0-9])", en):
        return "internal_dummy", "en_keyword"
    for category, keywords in CATEGORY_RULES:
        if any(contains_keyword(en, keyword) for keyword in keywords):
            return category, "en_keyword"
    if states["EN"] != "text" and any(states[language] == "text" for language in ("JP", "SC", "TC")):
        return "cjk_only_unclassified", "source_state"
    return "unclassified", "no_keyword_match"


def structural_class(states: dict[str, str], sc_text: str, profile: dict[str, Any]) -> str:
    if all(state == "empty" for state in states.values()):
        return "all_empty"
    if all(state != "text" for state in states.values()):
        return "all_whitespace"
    if states["SC"] != "text" and any(
        states[language] == "text" for language in ("EN", "JP", "TC")
    ):
        return "sc_blank_other_text"
    has_printf = profile["printf_count"] > 0
    has_esc = profile["esc_count"] > 0
    if has_printf and has_esc:
        return "styled_dynamic"
    if has_esc:
        return "styled_control"
    if has_printf:
        return "dynamic_printf"
    if profile["line_breaks"] > 0:
        return "multiline_static"
    length = len(sc_text)
    if length <= 8:
        return "short_ui_candidate"
    if length <= 20:
        return "medium_prompt_candidate"
    return "long_help_candidate"


def suggested_priority(
    entry_id: int,
    structural: str,
    category: str,
    catalog_status: str,
) -> tuple[str, str, str]:
    if entry_id in MAIN_MENU_IDS:
        return "P0", "validated_main_menu_surface", "high"
    if structural in ("all_empty", "all_whitespace"):
        return "SKIP", "no_substantive_source_text", "high"
    if structural in ("sc_blank_other_text", "long_help_candidate"):
        return "P4", "context_or_long_help_review", "medium"
    if structural in ("dynamic_printf", "styled_control", "styled_dynamic", "multiline_static"):
        return "P3", "native_token_or_multiline_qa", "high"
    if catalog_status in BUILDABLE_STATUSES:
        return "P1", "active_catalog_translation", "medium"
    if category in ("navigation_confirmation", "system_save_load_settings"):
        return "P1", "common_ui_keyword", "medium"
    return "P2", "static_ui_or_manual_triage", "medium"


def risk_level(flags: Sequence[str]) -> str:
    high = {
        "unknown_percent", "printf_cross_language_mismatch", "esc_cross_language_mismatch",
        "other_control", "pua", "sc_tc_printf_order_mismatch",
    }
    medium = {
        "printf", "esc", "line_breaks", "base_sc_blank_other_text",
        "en_blank_cjk_text", "sc_duplicate_semantic_collision",
    }
    if high.intersection(flags):
        return "high"
    if medium.intersection(flags):
        return "medium"
    return "low"


def build_duplicates(texts: dict[str, list[str]]) -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    report: dict[str, Any] = {"schema": "nobu16.kr.msgui-duplicate-groups.v1", "languages": {}}
    per_id: dict[int, dict[str, Any]] = {entry_id: {} for entry_id in range(len(texts["SC"]))}
    for language in LANGUAGES:
        grouped: dict[str, list[int]] = defaultdict(list)
        for entry_id, text in enumerate(texts[language]):
            if source_state(text) == "text":
                grouped[text].append(entry_id)
        groups = []
        for text, ids in grouped.items():
            if len(ids) < 2:
                continue
            digest = text_hash(text)
            groups.append({"text_utf16le_sha256": digest, "count": len(ids), "ids": ids})
            for entry_id in ids:
                per_id[entry_id].setdefault("per_language", {})[language] = {
                    "group_hash": digest,
                    "count": len(ids),
                }
        groups.sort(key=lambda item: (-item["count"], item["text_utf16le_sha256"]))
        report["languages"][language] = {
            "group_count": len(groups),
            "rows_in_groups": sum(item["count"] for item in groups),
            "redundant_rows": sum(item["count"] - 1 for item in groups),
            "groups": groups,
        }

    sc_groups: dict[str, list[int]] = defaultdict(list)
    tuple_groups: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for entry_id, sc_text in enumerate(texts["SC"]):
        if source_state(sc_text) != "text":
            continue
        sc_groups[sc_text].append(entry_id)
        source_tuple = tuple(texts[language][entry_id] for language in LANGUAGES)
        tuple_groups[source_tuple].append(entry_id)

    collision_groups = []
    for sc_text, ids in sc_groups.items():
        if len(ids) < 2:
            continue
        variants: dict[str, list[int]] = defaultdict(list)
        for entry_id in ids:
            source_tuple = tuple(texts[language][entry_id] for language in LANGUAGES)
            variants[signature_hash(source_tuple)].append(entry_id)
        conflict = len(variants) > 1
        item = {
            "sc_utf16le_sha256": text_hash(sc_text),
            "count": len(ids),
            "ids": ids,
            "multilingual_variant_count": len(variants),
            "semantic_collision": conflict,
            "variants": [
                {"multilingual_tuple_hash": key, "ids": value}
                for key, value in sorted(variants.items())
            ],
        }
        collision_groups.append(item)
        for entry_id in ids:
            per_id[entry_id]["sc_collision_group"] = item["sc_utf16le_sha256"]
            per_id[entry_id]["sc_duplicate_semantic_collision"] = conflict

    exact_tuple_groups = []
    translation_memory_candidates = []
    for source_tuple, ids in tuple_groups.items():
        if len(ids) < 2:
            continue
        digest = signature_hash(source_tuple)
        exact_tuple_groups.append({"multilingual_tuple_hash": digest, "count": len(ids), "ids": ids})
        sc_invariants = invariants(source_tuple[LANGUAGES.index("SC")])
        token_free = not any(
            (
                sc_invariants["printf"],
                sc_invariants["unknown_percent_count"],
                sc_invariants["esc"],
                sc_invariants["pua"],
                sc_invariants["other_controls"],
                sc_invariants["line_breaks"],
            )
        )
        if token_free:
            translation_memory_candidates.append(
                {"multilingual_tuple_hash": digest, "count": len(ids), "ids": ids}
            )
        for entry_id in ids:
            per_id[entry_id]["multilingual_tuple_group"] = digest
            per_id[entry_id]["multilingual_tuple_duplicate_count"] = len(ids)

    collision_groups.sort(key=lambda item: (-item["count"], item["sc_utf16le_sha256"]))
    exact_tuple_groups.sort(key=lambda item: (-item["count"], item["multilingual_tuple_hash"]))
    translation_memory_candidates.sort(
        key=lambda item: (-item["count"], item["multilingual_tuple_hash"])
    )

    # PowerShell Group-Object and some CAT tools group strings case-insensitively.
    # Preserve that legacy/advisory view separately; the canonical identity above
    # remains exact UTF-16 text.
    casefold_groups: dict[str, list[int]] = defaultdict(list)
    for entry_id, sc_text in enumerate(texts["SC"]):
        if source_state(sc_text) == "text":
            casefold_groups[unicodedata.normalize("NFC", sc_text).casefold()].append(entry_id)
    casefold_collisions = []
    for key, ids in casefold_groups.items():
        if len(ids) < 2:
            continue
        variants = {
            signature_hash(tuple(texts[language][entry_id] for language in LANGUAGES))
            for entry_id in ids
        }
        casefold_collisions.append(
            {
                "normalized_sc_sha256": sha256_bytes(key.encode("utf-8")),
                "count": len(ids),
                "ids": ids,
                "multilingual_variant_count": len(variants),
                "semantic_collision": len(variants) > 1,
            }
        )
    casefold_collisions.sort(key=lambda item: (-item["count"], item["normalized_sc_sha256"]))
    report["sc_collision_analysis"] = {
        "duplicate_group_count": len(collision_groups),
        "rows_in_duplicate_groups": sum(item["count"] for item in collision_groups),
        "semantic_collision_group_count": sum(item["semantic_collision"] for item in collision_groups),
        "rows_in_semantic_collision_groups": sum(
            item["count"] for item in collision_groups if item["semantic_collision"]
        ),
        "exact_multilingual_group_count": len(exact_tuple_groups),
        "rows_in_exact_multilingual_groups": sum(item["count"] for item in exact_tuple_groups),
        "exact_multilingual_redundant_rows": sum(item["count"] - 1 for item in exact_tuple_groups),
        "token_free_translation_memory_candidate_group_count": len(translation_memory_candidates),
        "rows_in_token_free_translation_memory_candidate_groups": sum(
            item["count"] for item in translation_memory_candidates
        ),
        "token_free_translation_memory_candidate_redundant_rows": sum(
            item["count"] - 1 for item in translation_memory_candidates
        ),
        "casefold_advisory_group_count": len(casefold_collisions),
        "casefold_advisory_rows_in_groups": sum(item["count"] for item in casefold_collisions),
        "casefold_advisory_semantic_collision_group_count": sum(
            item["semantic_collision"] for item in casefold_collisions
        ),
        "casefold_advisory_rows_in_semantic_collision_groups": sum(
            item["count"] for item in casefold_collisions if item["semantic_collision"]
        ),
        "groups": collision_groups,
        "exact_multilingual_groups": exact_tuple_groups,
        "token_free_translation_memory_candidates": translation_memory_candidates,
        "casefold_advisory_groups": casefold_collisions,
        "automatic_sc_only_translation_propagation_allowed": False,
    }
    return report, per_id


def load_inputs(meta_path: Path, catalog_path: Path, raw_paths: dict[str, Path]) -> tuple[
    dict[str, Any], list[dict[str, Any]], dict[str, bytes], dict[str, Any]
]:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    rows = read_jsonl(catalog_path)
    expected_count = int(meta["string_count"])
    if len(rows) != expected_count:
        raise ValueError(f"catalog row count {len(rows)} != {expected_count}")
    if [int(row["id"]) for row in rows] != list(range(expected_count)):
        raise ValueError("catalog ids are not the exact ordered range")

    raw: dict[str, bytes] = {}
    tables: dict[str, Any] = {}
    for language in LANGUAGES:
        blob = raw_paths[language].read_bytes()
        table = parse_message_table(blob)
        if table.string_count != expected_count:
            raise ValueError(f"{language} string count {table.string_count} != {expected_count}")
        expected_hash = meta["source_files"][language]["raw_sha256"]
        if sha256_bytes(blob) != expected_hash:
            raise ValueError(f"{language} raw SHA-256 differs from catalog metadata")
        for entry_id, row in enumerate(rows):
            text = row["source"][language]
            if table.texts[entry_id] != text:
                raise ValueError(f"{language} raw/catalog text mismatch at id {entry_id}")
            if text_hash(text) != row["source_utf16le_sha256"][language]:
                raise ValueError(f"{language} stored text hash mismatch at id {entry_id}")
        raw[language] = blob
        tables[language] = table
    return meta, rows, raw, tables


def build_inventory(args: argparse.Namespace) -> int:
    meta_path = args.meta.resolve()
    catalog_path = args.catalog.resolve()
    output_root = args.output_root.resolve()
    raw_paths = {
        language: Path(getattr(args, f"raw_{language.lower()}")).resolve()
        for language in LANGUAGES
    }
    meta, catalog_rows, raw, tables = load_inputs(meta_path, catalog_path, raw_paths)
    count = len(catalog_rows)
    texts = {language: list(tables[language].texts) for language in LANGUAGES}
    profiles = {
        language: [token_profile(text) for text in texts[language]] for language in LANGUAGES
    }
    states = {
        language: [source_state(text) for text in texts[language]] for language in LANGUAGES
    }
    duplicate_report, duplicate_by_id = build_duplicates(texts)

    pair_offset_equal: dict[str, int] = {}
    pair_printf_mismatch: dict[str, list[int]] = {}
    pair_esc_mismatch: dict[str, list[int]] = {}
    for left_index, left in enumerate(LANGUAGES):
        for right in LANGUAGES[left_index + 1 :]:
            key = f"{left}-{right}"
            pair_offset_equal[key] = sum(
                tables[left].string_offsets[entry_id] == tables[right].string_offsets[entry_id]
                for entry_id in range(count)
            )
            pair_printf_mismatch[key] = [
                entry_id
                for entry_id in range(count)
                if profiles[left][entry_id]["printf"] != profiles[right][entry_id]["printf"]
            ]
            pair_esc_mismatch[key] = [
                entry_id
                for entry_id in range(count)
                if profiles[left][entry_id]["esc"] != profiles[right][entry_id]["esc"]
            ]

    records: list[dict[str, Any]] = []
    structural_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    priority_counts: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    token_rows = {language: Counter() for language in LANGUAGES}
    token_occurrences = {language: Counter() for language in LANGUAGES}
    for entry_id, catalog_row in enumerate(catalog_rows):
        source = {language: texts[language][entry_id] for language in LANGUAGES}
        state = {language: states[language][entry_id] for language in LANGUAGES}
        profile = {language: profiles[language][entry_id] for language in LANGUAGES}
        offsets: dict[str, Any] = {}
        lengths: dict[str, Any] = {}
        for language in LANGUAGES:
            table = tables[language]
            relative = table.string_offsets[entry_id]
            absolute = table.table_offset + relative
            next_absolute = (
                table.table_offset + table.string_offsets[entry_id + 1]
                if entry_id + 1 < count
                else table.logical_end
            )
            offsets[language] = {
                "relative": relative,
                "absolute": absolute,
                "span_bytes": next_absolute - absolute,
            }
            lengths[language] = length_metrics(source[language])
            if profile[language]["printf_count"]:
                token_rows[language]["printf"] += 1
                token_occurrences[language]["printf"] += profile[language]["printf_count"]
            if profile[language]["esc_count"]:
                token_rows[language]["esc"] += 1
                token_occurrences[language]["esc"] += profile[language]["esc_count"]
            if profile[language]["pua_count"]:
                token_rows[language]["pua"] += 1
                token_occurrences[language]["pua"] += profile[language]["pua_count"]
            if profile[language]["line_breaks"]:
                token_rows[language]["line_breaks"] += 1
                token_occurrences[language]["line_breaks"] += profile[language]["line_breaks"]

        structural = structural_class(state, source["SC"], profile["SC"])
        category, category_basis = automatic_category(entry_id, source, state)
        priority, priority_basis, priority_confidence = suggested_priority(
            entry_id, structural, category, str(catalog_row.get("status", ""))
        )
        flags: list[str] = []
        if structural == "sc_blank_other_text":
            flags.append("base_sc_blank_other_text")
        if state["EN"] != "text" and any(state[language] == "text" for language in ("JP", "SC", "TC")):
            flags.append("en_blank_cjk_text")
        if profile["SC"]["printf_count"]:
            flags.append("printf")
        if profile["SC"]["esc_count"]:
            flags.append("esc")
        if profile["SC"]["pua_count"]:
            flags.append("pua")
        if profile["SC"]["line_breaks"]:
            flags.append("line_breaks")
        if profile["SC"]["unknown_percent_count"]:
            flags.append("unknown_percent")
        if profile["SC"]["other_controls"]:
            flags.append("other_control")
        printf_sequences = [profile[language]["printf"] for language in LANGUAGES]
        esc_sequences = [profile[language]["esc"] for language in LANGUAGES]
        if any(sequence != printf_sequences[0] for sequence in printf_sequences[1:]):
            flags.append("printf_cross_language_mismatch")
        if any(sequence != esc_sequences[0] for sequence in esc_sequences[1:]):
            flags.append("esc_cross_language_mismatch")
        duplicate = duplicate_by_id[entry_id]
        if duplicate.get("sc_duplicate_semantic_collision"):
            flags.append("sc_duplicate_semantic_collision")
        if profile["SC"]["printf"] != profile["TC"]["printf"]:
            flags.append("sc_tc_printf_order_mismatch")
        flags = sorted(set(flags))

        catalog_context = catalog_row.get("context", {})
        record = {
            "schema": RECORD_SCHEMA,
            "id": entry_id,
            "source_ref": {
                "catalog": str(catalog_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "catalog_id": entry_id,
                "contains_text_here": False,
            },
            "source_utf16le_sha256": catalog_row["source_utf16le_sha256"],
            "source_state": state,
            "offset": offsets,
            "length": lengths,
            "tokens": profile,
            "cross_language": {
                "all_offsets_equal": len({offsets[language]["relative"] for language in LANGUAGES}) == 1,
                "printf_sequence_equal": len({tuple(profile[language]["printf"]) for language in LANGUAGES}) == 1,
                "esc_sequence_equal": len({tuple(profile[language]["esc"]) for language in LANGUAGES}) == 1,
                "source_state_equal": len(set(state.values())) == 1,
            },
            "duplicates": duplicate,
            "structural_class": structural,
            "category_auto": category,
            "category_basis": category_basis,
            "priority_suggested": priority,
            "priority_basis": priority_basis,
            "priority_confidence": priority_confidence,
            "risk_level": risk_level(flags),
            "risk_flags": flags,
            "surface_evidence": "main_menu_runtime_validated" if entry_id in MAIN_MENU_IDS else "none",
            "catalog": {
                "status": catalog_row.get("status", ""),
                "priority_manual": catalog_row.get("priority", ""),
                "context_manual": catalog_context,
                "has_korean": bool(catalog_row.get("ko", "")),
                "korean_utf16le_sha256": text_hash(catalog_row.get("ko", "")),
                "korean_length": length_metrics(catalog_row.get("ko", "")),
            },
        }
        records.append(record)
        structural_counts[structural] += 1
        category_counts[category] += 1
        priority_counts[priority] += 1
        risk_counts[record["risk_level"]] += 1

    write_jsonl(output_root / "records.jsonl", records)
    write_json(output_root / "duplicates.json", duplicate_report)

    language_summary: dict[str, Any] = {}
    for language in LANGUAGES:
        state_counter = Counter(states[language])
        language_summary[language] = {
            "raw_path": str(raw_paths[language].relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "raw_size": len(raw[language]),
            "raw_sha256": sha256_bytes(raw[language]),
            "logical_end": tables[language].logical_end,
            "padding_size": len(tables[language].padding),
            "table_offset": tables[language].table_offset,
            "table_size": tables[language].table_size,
            "string_start": tables[language].string_start,
            "string_count": tables[language].string_count,
            "source_states": dict(sorted(state_counter.items())),
            "lengths": summarize_lengths(texts[language]),
            "token_rows": dict(token_rows[language]),
            "token_occurrences": dict(token_occurrences[language]),
        }

    all_offset_equal_ids = [
        entry_id
        for entry_id in range(count)
        if len({tables[language].string_offsets[entry_id] for language in LANGUAGES}) == 1
    ]
    sc_blank_other_text_ids = [
        record["id"] for record in records if record["structural_class"] == "sc_blank_other_text"
    ]
    summary = {
        "schema": SUMMARY_SCHEMA,
        "development_only": True,
        "contains_complete_commercial_text": False,
        "commercial_text_location": str(catalog_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "include_in_public_patch": False,
        "resource": "MSG_PK/*/msgui.bin",
        "stable_key": "id",
        "id_range": [0, count - 1],
        "record_count": count,
        "languages": language_summary,
        "common_structure": {
            "block_count": 1,
            "block_offset": tables["SC"].block_offset,
            "table_relative_offset": tables["SC"].table_offset - tables["SC"].block_offset,
            "table_absolute_offset": tables["SC"].table_offset,
            "table_size": tables["SC"].table_size,
            "string_pool_absolute_offset": tables["SC"].string_start,
        },
        "offset_alignment": {
            "byte_offsets_are_stable_keys": False,
            "all_four_equal_count": len(all_offset_equal_ids),
            "all_four_equal_ids": all_offset_equal_ids,
            "pair_equal_counts": pair_offset_equal,
            "rebuild_must_recompute_language_offsets": True,
        },
        "empty_alignment": {
            "all_empty_count": structural_counts["all_empty"],
            "all_whitespace_count": structural_counts["all_whitespace"],
            "sc_blank_other_text_count": len(sc_blank_other_text_ids),
            "sc_blank_other_text_ids": sc_blank_other_text_ids,
            "en_extra_empty_ids": [
                entry_id
                for entry_id in range(count)
                if states["EN"][entry_id] == "empty"
                and all(states[language][entry_id] == "text" for language in ("JP", "SC", "TC"))
            ],
        },
        "structural_class_counts": dict(sorted(structural_counts.items())),
        "category_auto_counts": dict(sorted(category_counts.items())),
        "priority_suggested_counts": dict(sorted(priority_counts.items())),
        "risk_level_counts": dict(sorted(risk_counts.items())),
        "format_alignment": {
            "pair_printf_mismatch_counts": {
                key: len(value) for key, value in pair_printf_mismatch.items()
            },
            "pair_printf_mismatch_ids": pair_printf_mismatch,
            "pair_esc_mismatch_counts": {key: len(value) for key, value in pair_esc_mismatch.items()},
            "pair_esc_mismatch_ids": pair_esc_mismatch,
            "sc_tc_printf_order_mismatch_ids": pair_printf_mismatch["SC-TC"],
        },
        "main_menu_validated_ids": sorted(MAIN_MENU_IDS),
        "catalog": {
            "path": str(catalog_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "sha256": sha256_file(catalog_path),
            "status_counts": dict(sorted(Counter(row["status"] for row in catalog_rows).items())),
            "buildable_count": sum(row["status"] in BUILDABLE_STATUSES for row in catalog_rows),
        },
        "duplicate_summary": duplicate_report["sc_collision_analysis"],
        "warnings": [
            "ID is the only stable cross-language key; never reuse another language's byte offsets.",
            "SC-only duplicate text is not a safe automatic translation-memory key.",
            "SC blank/whitespace rows with other-language text require context review, not automatic skipping.",
            "ID 3904 has a different SC/TC printf argument order; preserve the SC sequence for Korean.",
        ],
    }
    # Avoid embedding the full duplicate group arrays twice in summary.json.
    summary["duplicate_summary"] = {
        key: value
        for key, value in summary["duplicate_summary"].items()
        if key not in (
            "groups",
            "exact_multilingual_groups",
            "token_free_translation_memory_candidates",
            "casefold_advisory_groups",
        )
    }
    write_json(output_root / "summary.json", summary)

    token_catalog = {
        "schema": "nobu16.kr.msgui-token-catalog.v1",
        "languages": {
            language: {
                "rows": dict(token_rows[language]),
                "occurrences": dict(token_occurrences[language]),
                "printf_token_counts": dict(
                    sorted(Counter(token for profile in profiles[language] for token in profile["printf"]).items())
                ),
                "esc_token_counts": dict(
                    sorted(Counter(token for profile in profiles[language] for token in profile["esc"]).items())
                ),
                "pua_codepoint_counts": dict(
                    sorted(Counter(token for profile in profiles[language] for token in profile["pua"]).items())
                ),
                "unknown_percent_ids": [
                    entry_id
                    for entry_id, profile in enumerate(profiles[language])
                    if profile["unknown_percent_count"]
                ],
            }
            for language in LANGUAGES
        },
        "cross_language": summary["format_alignment"],
        "translation_contract": {
            "base_language": "SC",
            "preserve_printf_order_exactly": True,
            "preserve_esc_sequence_exactly": True,
            "unknown_percent_forbidden": True,
            "nul_forbidden": True,
            "line_break_change_requires_reviewed_override": True,
            "pua_change_requires_manual_review": True,
        },
    }
    write_json(output_root / "token_catalog.json", token_catalog)

    priority_buckets = {
        "schema": "nobu16.kr.msgui-priority-buckets.v1",
        "advisory_only": True,
        "manual_context_overrides_auto": True,
        "definitions": {
            "P0": "runtime-validated main-menu surface",
            "P1": "active translated/reviewed rows or common navigation/system UI",
            "P2": "remaining static short/medium UI and manual triage",
            "P3": "printf, ESC-styled, or multiline strings requiring native-format QA",
            "P4": "long help or SC blank while another language has content; context first",
            "SKIP": "all-language empty or whitespace-only",
        },
        "buckets": {
            priority: [record["id"] for record in records if record["priority_suggested"] == priority]
            for priority in ("P0", "P1", "P2", "P3", "P4", "SKIP")
        },
    }
    write_json(output_root / "priority_buckets.json", priority_buckets)

    demand = glyph_demand(catalog_rows)
    write_json(output_root / "glyph_demand.json", demand)

    source_manifest = {
        "schema": MANIFEST_SCHEMA,
        "development_only": True,
        "installed_game_files_read": False,
        "installed_game_files_modified": False,
        "registry_access": False,
        "process_access": False,
        "complete_commercial_text_duplicated_in_inventory": False,
        "commercial_source_catalog": {
            "path": str(catalog_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "size": catalog_path.stat().st_size,
            "sha256": sha256_file(catalog_path),
            "public_distribution_eligible": False,
        },
        "catalog_meta": {
            "path": str(meta_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "size": meta_path.stat().st_size,
            "sha256": sha256_file(meta_path),
        },
        "raw_sources": {
            language: {
                "path": str(raw_paths[language].relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "size": len(raw[language]),
                "sha256": sha256_bytes(raw[language]),
            }
            for language in LANGUAGES
        },
        "source_wrapper_metadata": meta["source_files"],
        "generator": {
            "path": str(Path(__file__).resolve().relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
    }
    write_json(output_root / "source_manifest.json", source_manifest)

    outputs = {}
    for path in sorted(output_root.iterdir()):
        if path.is_file() and path.name != "inventory_manifest.json":
            outputs[path.name] = {"size": path.stat().st_size, "sha256": sha256_file(path)}
    inventory_manifest = {
        "schema": "nobu16.kr.msgui-inventory-output-manifest.v1",
        "development_only": True,
        "public_distribution_eligible": False,
        "record_count": count,
        "outputs": outputs,
        "validation": {
            "catalog_ids_contiguous": True,
            "four_language_count_equal": True,
            "raw_hashes_match_catalog_meta": True,
            "raw_texts_match_catalog": True,
            "stored_source_hashes_match": True,
            "records_jsonl_count": count,
        },
    }
    write_json(output_root / "inventory_manifest.json", inventory_manifest)

    print(f"output={output_root}")
    print(f"records={count}")
    print(f"catalog={catalog_path}")
    print(f"catalog_buildable={summary['catalog']['buildable_count']}")
    print(f"sc_blank_other_text={len(sc_blank_other_text_ids)}")
    print(f"sc_tc_printf_mismatch={pair_printf_mismatch['SC-TC']}")
    print(f"glyph_demand={demand['character_count']}")
    print("installed_game_files_modified=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meta", type=Path, default=DEFAULT_META)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    for language in LANGUAGES:
        parser.add_argument(
            f"--raw-{language.lower()}",
            type=Path,
            default=DEFAULT_RAW[language],
        )
    return parser


def main() -> int:
    try:
        return build_inventory(build_parser().parse_args())
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
