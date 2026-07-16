#!/usr/bin/env python3
"""Integrate wave08 and the 980-entry Steam-JP officer-surname recovery.

The builder layers the nine source-free semantic batches over the pinned
``steam_jp_common_messages_v1`` baseline.  The 1,796 source-equal structural
contracts are excluded from the applied count.  The surname supplement
recovers the edge-whitespace rows that v0.7 omitted while preserving 70
base-owned conflicts.  Complete candidates may only be written below ``tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = import_file(
    "steam_jp_common_messages_wave08_integration_common",
    REPO
    / "workstreams"
    / "steam_jp_common_messages_v1"
    / "build_steam_jp_common_messages_v1.py",
)
SURNAMES = import_file(
    "steam_jp_common_messages_wave08_surnames",
    REPO
    / "workstreams"
    / "steam_jp_officer_surnames_v1"
    / "build_steam_jp_officer_surnames_v1.py",
)


SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-integration.v1"
DELTA_SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-delta.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-integration-validation.v1"
TRIAGE_SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-triage.v1"
EXACT_VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-exact-recovery-validation.v1"

TRIAGE_PATH = HERE / "triage.v1.json"
EXACT_VALIDATION_PATH = HERE / "validation.exact_contract.v1.json"
VALIDATION_PATH = HERE / "validation.integration.v1.json"
DEFAULT_STOCK_ROOT = Path(
    "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    "steam-jp-1.1.7-v0.6.0/originals"
)
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_common_messages_wave08_integrated_candidate"

BASE_APPLIED_ENTRIES = 39_507
WAVE08_SEMANTIC_ENTRIES = 94
SURNAME_RECOVERY_ENTRIES = 980
FINAL_APPLIED_ENTRIES = 40_581
WAVE08_REVIEWED_SEMANTIC_GAP_REMAINING = 0
RETAINED_INTERNAL_DUMMY_ENTRIES = 2
EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES = 1_796
FORMAT_CONTRACT_BLOCKED_ENTRIES = 730
ALIGNMENT_GAP_ENTRIES = 62
REVIEW_BACKLOG_ENTRIES = FORMAT_CONTRACT_BLOCKED_ENTRIES + ALIGNMENT_GAP_ENTRIES
SOURCE_UNION_EFFECTIVE_ENTRIES = 43_169
EXPECTED_RESOURCE_DELTAS = {
    "msgev.bin": 69,
    "msgdata.bin": 1_004,
    "msgbre.bin": 0,
    "msgire.bin": 0,
    "msgstf.bin": 1,
}
EXPECTED_SEMANTIC_DELTAS = {
    "msgev.bin": 69,
    "msgdata.bin": 24,
    "msgbre.bin": 0,
    "msgire.bin": 0,
    "msgstf.bin": 1,
}
EXPECTED_SOURCE_EQUAL_BY_RESOURCE = {
    "msgev.bin": 83,
    "msgdata.bin": 1_713,
    "msgbre.bin": 0,
    "msgire.bin": 0,
    "msgstf.bin": 0,
}
EXPECTED_FORMAT_BLOCKED_BY_RESOURCE = {
    "msgev.bin": 554,
    "msgdata.bin": 175,
    "msgbre.bin": 1,
    "msgire.bin": 0,
    "msgstf.bin": 0,
}
EXPECTED_ALIGNMENT_GAP_BY_RESOURCE = {
    "msgev.bin": 4,
    "msgdata.bin": 57,
    "msgbre.bin": 0,
    "msgire.bin": 0,
    "msgstf.bin": 1,
}
EXPECTED_SOURCE_UNION_BY_RESOURCE = {
    "msgev.bin": 14_504,
    "msgdata.bin": 26_318,
    "msgbre.bin": 2_217,
    "msgire.bin": 122,
    "msgstf.bin": 8,
}

BATCHES: tuple[dict[str, Any], ...] = (
    {
        "batch_id": "j01_msgev_semantic_equivalent_reuse",
        "resource": "MSG_PK/JP/msgev.bin",
        "count": 5,
        "path": HERE / "public" / "msgev_ko_steam_jp_wave08_j01_5.v1.json",
    },
    {
        "batch_id": "j02_msgev_officer_names",
        "resource": "MSG_PK/JP/msgev.bin",
        "count": 2,
        "path": HERE / "public" / "msgev_ko_steam_jp_wave08_j02_2.v1.json",
    },
    {
        "batch_id": "j03_msgev_event_and_era_titles",
        "resource": "MSG_PK/JP/msgev.bin",
        "count": 31,
        "path": HERE / "public" / "msgev_ko_steam_jp_wave08_j03_31.v1.json",
    },
    {
        "batch_id": "j04_msgev_reading_keys",
        "resource": "MSG_PK/JP/msgev.bin",
        "count": 31,
        "path": HERE / "public" / "msgev_ko_steam_jp_wave08_j04_reading_keys_31.v1.json",
    },
    {
        "batch_id": "j05_msgdata_live_revisions",
        "resource": "MSG_PK/JP/msgdata.bin",
        "count": 6,
        "path": HERE / "public" / "msgdata_ko_steam_jp_wave08_j05_live_revisions_6.v1.json",
    },
    {
        "batch_id": "j06_msgdata_legend_names",
        "resource": "MSG_PK/JP/msgdata.bin",
        "count": 6,
        "path": HERE / "public" / "msgdata_ko_steam_jp_wave08_j06_legend_names_6.v1.json",
    },
    {
        "batch_id": "j07_msgdata_legend_reading_keys",
        "resource": "MSG_PK/JP/msgdata.bin",
        "count": 6,
        "path": HERE / "public" / "msgdata_ko_steam_jp_wave08_j07_legend_reading_keys_6.v1.json",
    },
    {
        "batch_id": "j08_msgdata_legend_descriptions",
        "resource": "MSG_PK/JP/msgdata.bin",
        "count": 6,
        "path": HERE / "public" / "msgdata_ko_steam_jp_wave08_j08_legend_descriptions_6.v1.json",
    },
    {
        "batch_id": "j09_msgstf_credit_update",
        "resource": "MSG_PK/JP/msgstf.bin",
        "count": 1,
        "path": HERE / "public" / "msgstf_ko_steam_jp_wave08_j09_credit_update_1.v1.json",
    },
)

INDIVIDUAL_BUILDERS: tuple[tuple[str, str, int], ...] = (
    ("j01", "build_wave08_j01.py", 5),
    ("j02", "build_wave08_j02.py", 2),
    ("j03", "build_wave08_j03.py", 31),
    ("j04", "build_wave08_j04.py", 31),
    ("j05", "build_wave08_j05.py", 6),
    ("j06_j09", "build_wave08_j06_j09.py", 19),
)


class Wave08IntegrationError(ValueError):
    """A Steam-JP pin, delta, accounting, or structure contract differed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def path_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def _load_triage() -> tuple[dict[str, dict[str, Any]], dict[str, Any], bytes]:
    value, blob = COMMON.read_json(TRIAGE_PATH)
    if value.get("schema") != TRIAGE_SCHEMA or value.get("base_language") != "JP":
        raise Wave08IntegrationError("wave08 triage identity differs")
    if value.get("distribution_policy") != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise Wave08IntegrationError("wave08 triage distribution policy differs")
    aggregate = value.get("aggregate")
    if not isinstance(aggregate, dict) or {
        "legacy_unresolved_count": aggregate.get("legacy_unresolved_count"),
        "semantic_translation_count": aggregate.get("semantic_translation_count"),
        "nonsemantic_hold_count": aggregate.get("nonsemantic_hold_count"),
    } != {
        "legacy_unresolved_count": 96,
        "semantic_translation_count": WAVE08_SEMANTIC_ENTRIES,
        "nonsemantic_hold_count": RETAINED_INTERNAL_DUMMY_ENTRIES,
    }:
        raise Wave08IntegrationError("wave08 triage aggregate differs")
    provenance = value.get("provenance")
    if (
        not isinstance(provenance, dict)
        or provenance.get("sc_binary_used") is not False
        or provenance.get("sc_coordinate_used") is not False
    ):
        raise Wave08IntegrationError("wave08 triage provenance differs")
    rows = value.get("batches")
    if not isinstance(rows, list):
        raise Wave08IntegrationError("wave08 triage batches are absent")
    by_id = {row.get("batch_id"): row for row in rows if isinstance(row, dict)}
    if len(by_id) != len(rows):
        raise Wave08IntegrationError("wave08 triage batch IDs are not unique")
    hold = by_id.get("hold_msgev_internal_dummy_labels")
    if (
        not isinstance(hold, dict)
        or hold.get("resource") != "MSG_PK/JP/msgev.bin"
        or hold.get("current_ids") != [15_420, 16_219]
        or hold.get("semantic_entry_count") != 0
        or hold.get("translation_action") != "hold"
        or hold.get("status") != "withheld_nonsemantic"
    ):
        raise Wave08IntegrationError("retained internal dummy contract differs")
    return by_id, hold, blob


def load_semantic_overlays() -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Load and normalize only the nine semantic overlay batches."""
    triage, _hold, _triage_blob = _load_triage()
    by_resource: dict[str, list[dict[str, Any]]] = defaultdict(list)
    artifacts: list[dict[str, Any]] = []
    coordinates: set[tuple[str, int]] = set()
    overlay_ids: set[str] = set()
    for spec in BATCHES:
        row = triage.get(spec["batch_id"])
        if not isinstance(row, dict):
            raise Wave08IntegrationError(f"triage batch is absent: {spec['batch_id']}")
        if (
            row.get("resource") != spec["resource"]
            or row.get("semantic_entry_count") != spec["count"]
            or row.get("translation_action") == "hold"
        ):
            raise Wave08IntegrationError(f"triage scope differs: {spec['batch_id']}")

        overlay, blob = COMMON.read_json(spec["path"])
        required = {
            "schema", "overlay_id", "resource", "base_language", "distribution_policy",
            "stock_jp", "provenance", "entry_count", "ids_sha256",
            "source_rows_sha256", "entries",
        }
        COMMON.exact_keys(overlay, required, spec["batch_id"])
        name = Path(spec["resource"]).name
        overlay_id = overlay["overlay_id"]
        if (
            overlay["schema"] != DELTA_SCHEMA
            or not isinstance(overlay_id, str)
            or not overlay_id
            or overlay_id in overlay_ids
            or overlay["resource"] != spec["resource"]
            or overlay["base_language"] != "JP"
            or overlay["stock_jp"] != COMMON.pin_public(COMMON.STEAM_PINS[name])
        ):
            raise Wave08IntegrationError(f"overlay identity differs: {spec['batch_id']}")
        overlay_ids.add(overlay_id)
        if overlay["distribution_policy"] != {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        }:
            raise Wave08IntegrationError(f"overlay policy differs: {spec['batch_id']}")
        provenance = overlay["provenance"]
        if (
            not isinstance(provenance, dict)
            or provenance.get("existing_v1_overlay_preserved") is not True
            or provenance.get("resolved_previous_unmapped_count") != spec["count"]
            or provenance.get("official_multilingual_reference_is_build_dependency") is True
            or provenance.get("sc_binary_used") is True
            or provenance.get("sc_coordinate_used") is True
        ):
            raise Wave08IntegrationError(f"overlay provenance differs: {spec['batch_id']}")
        entries = overlay["entries"]
        if not isinstance(entries, list) or overlay["entry_count"] != spec["count"]:
            raise Wave08IntegrationError(f"overlay entry count differs: {spec['batch_id']}")
        ids: list[int] = []
        source_rows: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise Wave08IntegrationError(f"overlay entry is not an object: {spec['batch_id']}")
            entry_id = COMMON.require_int(entry.get("id"), "entry.id")
            source_hash = COMMON.require_hash(
                entry.get("source_jp_utf16le_sha256"), "entry source hash"
            )
            ko_hash = COMMON.require_hash(entry.get("ko_utf16le_sha256"), "entry Korean hash")
            korean = entry.get("ko")
            if (
                not isinstance(korean, str)
                or "\0" in korean
                or COMMON.text_hash(korean) != ko_hash
                or source_hash == ko_hash
            ):
                raise Wave08IntegrationError(
                    f"semantic Korean payload differs: {spec['batch_id']}:{entry_id}"
                )
            coordinate = (spec["resource"], entry_id)
            if coordinate in coordinates:
                raise Wave08IntegrationError(f"duplicate semantic coordinate: {coordinate}")
            coordinates.add(coordinate)
            ids.append(entry_id)
            source_rows.append({"id": entry_id, "source_jp_utf16le_sha256": source_hash})
            by_resource[spec["resource"]].append(entry)
        if (
            ids != row.get("current_ids")
            or COMMON.canonical_hash(ids) != overlay["ids_sha256"]
            or overlay["ids_sha256"] != row.get("current_ids_sha256")
            or COMMON.canonical_hash(source_rows) != overlay["source_rows_sha256"]
            or overlay["source_rows_sha256"] != row.get("source_rows_sha256")
        ):
            raise Wave08IntegrationError(f"overlay coordinate vector differs: {spec['batch_id']}")
        artifacts.append(
            {
                "batch_id": spec["batch_id"],
                "resource": spec["resource"],
                "entry_count": spec["count"],
                "path": spec["path"].relative_to(REPO).as_posix(),
                "size": len(blob),
                "sha256": sha256(blob),
            }
        )

    actual = {Path(resource).name: len(entries) for resource, entries in by_resource.items()}
    actual |= {name: 0 for name in COMMON.FILES if name not in actual}
    if actual != EXPECTED_SEMANTIC_DELTAS or len(coordinates) != WAVE08_SEMANTIC_ENTRIES:
        raise Wave08IntegrationError(f"semantic resource totals differ: {actual}")
    for entries in by_resource.values():
        entries.sort(key=lambda entry: int(entry["id"]))
    return dict(by_resource), artifacts


def _validate_excluded_catalogs() -> dict[str, Any]:
    value, blob = COMMON.read_json(EXACT_VALIDATION_PATH)
    expected = value.get("expected")
    progress = value.get("progress_accounting")
    if (
        value.get("schema") != EXACT_VALIDATION_SCHEMA
        or value.get("status") != "PASS"
        or not isinstance(expected, dict)
        or expected.get("exact_contract_entry_count") != EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES
        or expected.get("effective_korean_change_count") != BASE_APPLIED_ENTRIES
        or not isinstance(progress, dict)
        or progress.get("runtime_translation_added_count") != 0
        or progress.get("source_equal_contracts_must_not_increment_applied_translation") is not True
    ):
        raise Wave08IntegrationError("source-equal exclusion validation differs")
    resources = expected.get("resources")
    if not isinstance(resources, dict):
        raise Wave08IntegrationError("source-equal resource validation is absent")
    observed = {
        name: int(resources.get(name, {}).get("exact_contract_entry_count", 0))
        for name in EXPECTED_SOURCE_EQUAL_BY_RESOURCE
    }
    if observed != EXPECTED_SOURCE_EQUAL_BY_RESOURCE:
        raise Wave08IntegrationError("source-equal resource counts differ")
    return {
        "entry_count": EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES,
        "runtime_translation_added_count": 0,
        "path": EXACT_VALIDATION_PATH.relative_to(REPO).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def _build_once(stock_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    deltas, artifacts = load_semantic_overlays()
    surname_overlay, surname_blob = SURNAMES.load_overlay(stock_root)
    if (
        surname_overlay.get("resource") != "MSG_PK/JP/msgdata.bin"
        or surname_overlay.get("entry_count") != SURNAME_RECOVERY_ENTRIES
    ):
        raise Wave08IntegrationError("surname recovery overlay scope differs")
    excluded_catalog = _validate_excluded_catalogs()
    triage, hold, triage_blob = _load_triage()
    del triage
    hold_ids = set(int(value) for value in hold["current_ids"])
    base_overlays, base_blobs = COMMON.load_public_overlays()
    candidates: dict[str, bytes] = {}
    resource_metrics: list[dict[str, Any]] = []

    for name in COMMON.FILES:
        resource = f"MSG_PK/JP/{name}"
        stock = COMMON.load_pinned(
            stock_root / Path(resource),
            COMMON.STEAM_PINS[name],
            f"Steam 1.1.7 pristine JP {name}",
        )
        baseline, baseline_metrics = COMMON.build_one(name, stock, base_overlays[name])
        _header, baseline_raw = COMMON.decompress_wrapper(baseline)
        baseline_table = COMMON.parse_message_table(baseline_raw)
        texts = list(baseline_table.texts)
        delta_ids: set[int] = set()
        semantic_delta_ids: set[int] = set()
        surname_delta_ids: set[int] = set()
        typed_entries = [
            (entry, "semantic") for entry in deltas.get(resource, [])
        ]
        if name == "msgdata.bin":
            typed_entries.extend(
                (entry, "surname") for entry in surname_overlay["entries"]
            )
        for entry, delta_kind in typed_entries:
            entry_id = int(entry["id"])
            if not 0 <= entry_id < stock.table.string_count:
                raise Wave08IntegrationError(f"delta ID is outside table: {name}:{entry_id}")
            source = stock.table.texts[entry_id]
            if COMMON.text_hash(source) != entry["source_jp_utf16le_sha256"]:
                raise Wave08IntegrationError(f"current JP source hash differs: {name}:{entry_id}")
            if texts[entry_id] != source:
                raise Wave08IntegrationError(f"delta overlaps v1 overlay: {name}:{entry_id}")
            if entry_id in delta_ids:
                raise Wave08IntegrationError(f"duplicate resource delta: {name}:{entry_id}")
            mismatches = COMMON.common.invariant_mismatches(
                source,
                entry["ko"],
                allow_edge_whitespace_change=bool(
                    entry.get("allow_edge_whitespace_change", False)
                ),
            )
            if mismatches:
                raise Wave08IntegrationError(
                    f"format invariant differs: {name}:{entry_id}: {mismatches}"
                )
            texts[entry_id] = entry["ko"]
            delta_ids.add(entry_id)
            if delta_kind == "semantic":
                semantic_delta_ids.add(entry_id)
            else:
                surname_delta_ids.add(entry_id)

        if name == "msgev.bin":
            base_ids = {int(entry["id"]) for entry in base_overlays[name]["entries"]}
            if hold_ids & (base_ids | delta_ids):
                raise Wave08IntegrationError("retained internal dummy IDs entered an applied overlay")
            if any(texts[entry_id] != stock.table.texts[entry_id] for entry_id in hold_ids):
                raise Wave08IntegrationError("retained internal dummy text changed")

        rebuilt_raw = COMMON.rebuild_message_table(stock.table, texts)
        reparsed = COMMON.parse_message_table(rebuilt_raw)
        if reparsed.texts != tuple(texts):
            raise Wave08IntegrationError(f"rebuilt text table differs: {name}")
        if not COMMON._opaque_structure_preserved(stock.table, reparsed, rebuilt_raw):
            raise Wave08IntegrationError(f"opaque structure differs: {name}")
        for entry_id, text in enumerate(baseline_table.texts):
            if entry_id not in delta_ids and reparsed.texts[entry_id] != text:
                raise Wave08IntegrationError(f"non-delta text changed: {name}:{entry_id}")
        candidate = COMMON.recompress_wrapper(rebuilt_raw, stock.packed)
        _wrapper, roundtrip = COMMON.decompress_wrapper(candidate)
        if roundtrip != rebuilt_raw or candidate[:8] != stock.packed[:8]:
            raise Wave08IntegrationError(f"wrapper round-trip differs: {name}")
        if not delta_ids and candidate != baseline:
            raise Wave08IntegrationError(f"zero-delta resource differs from v1 baseline: {name}")
        if len(delta_ids) != EXPECTED_RESOURCE_DELTAS[name]:
            raise Wave08IntegrationError(f"resource delta count differs: {name}")
        if len(semantic_delta_ids) != EXPECTED_SEMANTIC_DELTAS[name]:
            raise Wave08IntegrationError(f"resource semantic delta count differs: {name}")
        expected_surname_count = SURNAME_RECOVERY_ENTRIES if name == "msgdata.bin" else 0
        if len(surname_delta_ids) != expected_surname_count:
            raise Wave08IntegrationError(f"resource surname delta count differs: {name}")

        applied_count = int(baseline_metrics["applied_count"]) + len(delta_ids)
        source_union_count = EXPECTED_SOURCE_UNION_BY_RESOURCE[name]
        accounted_count = (
            applied_count
            + EXPECTED_SOURCE_EQUAL_BY_RESOURCE[name]
            + EXPECTED_FORMAT_BLOCKED_BY_RESOURCE[name]
            + EXPECTED_ALIGNMENT_GAP_BY_RESOURCE[name]
        )
        if accounted_count != source_union_count:
            raise Wave08IntegrationError(f"resource source-union accounting differs: {name}")

        candidates[name] = candidate
        candidate_spec = {
            "size": len(candidate),
            "sha256": sha256(candidate),
            "packed_sha256": sha256(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256(rebuilt_raw),
            "string_count": reparsed.string_count,
        }
        resource_metrics.append(
            {
                "resource": resource,
                "baseline_applied_count": int(baseline_metrics["applied_count"]),
                "wave08_semantic_delta_count": len(semantic_delta_ids),
                "surname_recovery_delta_count": len(surname_delta_ids),
                "applied_count": applied_count,
                "wave08_reviewed_semantic_gap_remaining": (
                    WAVE08_REVIEWED_SEMANTIC_GAP_REMAINING
                    if EXPECTED_SEMANTIC_DELTAS[name]
                    else 0
                ),
                "retained_internal_dummy_count": (
                    RETAINED_INTERNAL_DUMMY_ENTRIES if name == "msgev.bin" else 0
                ),
                "excluded_source_equal_contract_count": EXPECTED_SOURCE_EQUAL_BY_RESOURCE[name],
                "format_contract_blocked_count": EXPECTED_FORMAT_BLOCKED_BY_RESOURCE[name],
                "alignment_gap_count": EXPECTED_ALIGNMENT_GAP_BY_RESOURCE[name],
                "source_union_effective_coordinate_count": source_union_count,
                "stock": COMMON.pin_public(COMMON.STEAM_PINS[name]),
                "baseline_candidate": {
                    "size": len(baseline),
                    "sha256": sha256(baseline),
                },
                "candidate": candidate_spec,
                "delta_ids_sha256": COMMON.canonical_hash(sorted(delta_ids)),
                "id_domain_preserved": True,
                "string_count_preserved": True,
                "opaque_non_string_metadata_preserved": True,
                "non_delta_texts_preserved": True,
                "wrapper_prefix_preserved": True,
            }
        )

    if sum(row["applied_count"] for row in resource_metrics) != FINAL_APPLIED_ENTRIES:
        raise Wave08IntegrationError("final common applied total differs")
    if (
        FINAL_APPLIED_ENTRIES
        + EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES
        + FORMAT_CONTRACT_BLOCKED_ENTRIES
        + ALIGNMENT_GAP_ENTRIES
        != SOURCE_UNION_EFFECTIVE_ENTRIES
    ):
        raise Wave08IntegrationError("global source-union accounting differs")
    return candidates, {
        "schema": SCHEMA,
        "base_language": "JP",
        "steam_version": "1.1.7",
        "applied_entries": FINAL_APPLIED_ENTRIES,
        "baseline_applied_entries": BASE_APPLIED_ENTRIES,
        "wave08_semantic_delta_entries": WAVE08_SEMANTIC_ENTRIES,
        "surname_recovery_delta_entries": SURNAME_RECOVERY_ENTRIES,
        "wave08_reviewed_semantic_gap_remaining": WAVE08_REVIEWED_SEMANTIC_GAP_REMAINING,
        "review_backlog_entries": REVIEW_BACKLOG_ENTRIES,
        "format_contract_blocked_entries": FORMAT_CONTRACT_BLOCKED_ENTRIES,
        "alignment_gap_entries": ALIGNMENT_GAP_ENTRIES,
        "source_union_effective_entries": SOURCE_UNION_EFFECTIVE_ENTRIES,
        "source_union_effective_coordinate_entries": SOURCE_UNION_EFFECTIVE_ENTRIES,
        "retained_internal_dummy_entries": RETAINED_INTERNAL_DUMMY_ENTRIES,
        "excluded_source_equal_contract_entries": EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES,
        "candidates": {
            Path(row["resource"]).name: row["candidate"] for row in resource_metrics
        },
        "resources": resource_metrics,
        "semantic_overlays": artifacts,
        "surname_overlay": {
            "path": SURNAMES.OVERLAY_PATH.relative_to(REPO).as_posix(),
            "entry_count": SURNAME_RECOVERY_ENTRIES,
            "size": len(surname_blob),
            "sha256": sha256(surname_blob),
        },
        "triage": {
            "path": TRIAGE_PATH.relative_to(REPO).as_posix(),
            "size": len(triage_blob),
            "sha256": sha256(triage_blob),
        },
        "excluded_source_equal_catalog": excluded_catalog,
        "base_overlay_artifacts": {
            name: {"size": len(blob), "sha256": sha256(blob)}
            for name, blob in sorted(base_blobs.items())
        },
        "provenance": {
            "base_workstream": "steam_jp_common_messages_v1",
            "semantic_batches": [spec["batch_id"] for spec in BATCHES],
            "source_equal_contracts_applied": False,
            "internal_dummy_labels_applied": False,
            "source_free_officer_catalog_coordinates_revalidated_to_jp": True,
            "current_jp_source_hashes_fail_closed": True,
            "official_multilingual_reference_is_build_dependency": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
        "candidate_binaries_tracked": False,
        "installed_game_files_modified": False,
    }


def build_all(stock_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Return all five deterministic integrated candidate binaries and metadata."""
    first, first_metrics = _build_once(stock_root)
    second, second_metrics = _build_once(stock_root)
    if first != second or first_metrics != second_metrics:
        raise Wave08IntegrationError("integrated deterministic A/B build differs")
    first_metrics["deterministic_ab_equal"] = True
    return first, first_metrics


def _verification_artifacts() -> list[dict[str, Any]]:
    paths = [HERE / filename for _label, filename, _count in INDIVIDUAL_BUILDERS]
    paths.extend(
        [
            HERE / "validation.j01.v1.json",
            HERE / "validation.j02.v1.json",
            HERE / "validation.j03.v1.json",
            HERE / "validation.j04.v1.json",
            HERE / "validation.j05.v1.json",
            HERE / "validation.j06_j09.v1.json",
        ]
    )
    return [
        {
            "path": path.relative_to(REPO).as_posix(),
            **path_spec(path),
        }
        for path in paths
    ]


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "target": {
            "base_language": "JP",
            "steam_version": "1.1.7",
            "resources": [f"MSG_PK/JP/{name}" for name in COMMON.FILES],
        },
        "translation": {
            "baseline_applied_count": BASE_APPLIED_ENTRIES,
            "wave08_semantic_delta_count": WAVE08_SEMANTIC_ENTRIES,
            "surname_recovery_delta_count": SURNAME_RECOVERY_ENTRIES,
            "total_common_applied_count": FINAL_APPLIED_ENTRIES,
            "wave08_reviewed_semantic_gap_remaining": (
                WAVE08_REVIEWED_SEMANTIC_GAP_REMAINING
            ),
            "retained_internal_dummy_count": RETAINED_INTERNAL_DUMMY_ENTRIES,
        },
        "source_union_accounting": {
            "effective_coordinate_count": SOURCE_UNION_EFFECTIVE_ENTRIES,
            "applied_count": FINAL_APPLIED_ENTRIES,
            "source_equal_structural_noop_count": EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES,
            "format_contract_blocked_count": FORMAT_CONTRACT_BLOCKED_ENTRIES,
            "alignment_gap_count": ALIGNMENT_GAP_ENTRIES,
            "review_backlog_count": REVIEW_BACKLOG_ENTRIES,
            "equation_holds": True,
        },
        "excluded_source_equal_contracts": {
            "entry_count": EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES,
            "runtime_translation_added_count": 0,
            "counted_as_applied_translation": False,
            "artifact": metrics["excluded_source_equal_catalog"],
        },
        "expected": {
            "candidates": metrics["candidates"],
            "resources": metrics["resources"],
            "semantic_overlays": metrics["semantic_overlays"],
            "surname_overlay": metrics["surname_overlay"],
            "triage": metrics["triage"],
            "base_overlay_artifacts": metrics["base_overlay_artifacts"],
            "individual_builder_artifacts": _verification_artifacts(),
        },
        "proofs": {
            "all_individual_builder_verifies_required": True,
            "all_stock_hash_pins_exact": True,
            "deterministic_ab_equal": True,
            "id_domains_preserved": True,
            "non_delta_texts_preserved": True,
            "opaque_non_string_metadata_preserved": True,
            "source_hashes_fail_closed": True,
            "wrapper_prefixes_preserved": True,
        },
        "safety": {
            "complete_candidate_binaries_tracked": False,
            "installed_game_files_modified": False,
            "official_multilingual_reference_is_build_dependency": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
            "source_free_officer_catalog_coordinates_revalidated_to_jp": True,
        },
    }


def verify_individual_builders(stock_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for label, filename, expected_delta in INDIVIDUAL_BUILDERS:
        module = import_file(f"wave08_integration_verify_{label}", HERE / filename)
        result = module.verify(stock_root)
        if result.get("status") != "PASS" or result.get("delta_applied_count") != expected_delta:
            raise Wave08IntegrationError(f"individual builder verify differs: {label}")
        results.append(
            {
                "batch": label,
                "status": "PASS",
                "delta_applied_count": expected_delta,
            }
        )
    return results


def verify_excluded_exact_contracts(stock_root: Path) -> dict[str, Any]:
    module = import_file(
        "wave08_integration_verify_exact_contracts", HERE / "build_exact_contract_recovery.py"
    )
    result = module.verify(stock_root)
    if (
        result.get("status") != "PASS"
        or result.get("exact_contract_entry_count") != EXCLUDED_SOURCE_EQUAL_CONTRACT_ENTRIES
        or result.get("effective_korean_change_count") != BASE_APPLIED_ENTRIES
    ):
        raise Wave08IntegrationError("excluded source-equal contract verify differs")
    return {
        "status": "PASS",
        "entry_count": result["exact_contract_entry_count"],
        "runtime_translation_added_count": 0,
        "candidate_bytes_unchanged": result["proofs"]["candidate_bytes_unchanged"],
    }


def generate(stock_root: Path) -> dict[str, Any]:
    surname = SURNAMES.verify(stock_root)
    if surname.get("status") != "PASS" or surname.get("surname_delta_count") != SURNAME_RECOVERY_ENTRIES:
        raise Wave08IntegrationError("surname supplement verify differs")
    _candidates, metrics = build_all(stock_root)
    individual = verify_individual_builders(stock_root)
    exact = verify_excluded_exact_contracts(stock_root)
    COMMON.atomic_write(VALIDATION_PATH, COMMON.pretty_bytes(validation_model(metrics)))
    return {
        "status": "GENERATED",
        "applied_entries": metrics["applied_entries"],
        "review_backlog_entries": metrics["review_backlog_entries"],
        "surname_recovery_delta_entries": metrics["surname_recovery_delta_entries"],
        "individual_builders": individual,
        "surname_supplement": {
            "status": "PASS",
            "surname_delta_count": surname["surname_delta_count"],
        },
        "excluded_source_equal_contracts": exact,
        "deterministic_ab_equal": True,
    }


def verify(stock_root: Path) -> dict[str, Any]:
    surname = SURNAMES.verify(stock_root)
    if surname.get("status") != "PASS" or surname.get("surname_delta_count") != SURNAME_RECOVERY_ENTRIES:
        raise Wave08IntegrationError("surname supplement verify differs")
    _candidates, metrics = build_all(stock_root)
    validation, blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(metrics)
    if validation != expected or blob != COMMON.pretty_bytes(expected):
        raise Wave08IntegrationError("tracked integration validation differs")
    individual = verify_individual_builders(stock_root)
    exact = verify_excluded_exact_contracts(stock_root)
    return {
        "status": "PASS",
        **metrics,
        "individual_builders": individual,
        "surname_supplement_verify": {
            "status": "PASS",
            "surname_delta_count": surname["surname_delta_count"],
        },
        "excluded_source_equal_verify": exact,
    }


def output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    if resolved == tmp or tmp not in resolved.parents or resolved.exists():
        raise Wave08IntegrationError(f"unsafe or existing output root: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "verify", "build"):
        child = subparsers.add_parser(command)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        result = generate(args.stock_root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        result = verify(args.stock_root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    candidates, metrics = build_all(args.stock_root)
    destination = output_root(args.output_root)
    try:
        for name, candidate in candidates.items():
            target = destination / "MSG_PK" / "JP" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(candidate)
        (destination / "private_manifest.json").write_bytes(COMMON.pretty_bytes(metrics))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
