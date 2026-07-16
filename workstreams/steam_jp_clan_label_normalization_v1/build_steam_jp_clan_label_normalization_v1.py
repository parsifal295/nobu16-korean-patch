#!/usr/bin/env python3
"""Normalize the post-wave08 event-family clan suffix labels for issue #46.

This workstream starts from the deterministic Steam 1.1.7 JP wave08+surname
``msgdata.bin`` candidate, never from a live game file.  The public overlay
contains project-authored Korean output plus hashes only; it contains neither
commercial JP text nor a complete game resource.  ``build`` may write a
candidate only below ``tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from dataclasses import dataclass
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
    "steam_jp_clan_label_normalization_common",
    REPO / "workstreams" / "steam_jp_common_messages_v1" / "build_steam_jp_common_messages_v1.py",
)
WAVE08 = import_file(
    "steam_jp_clan_label_normalization_wave08",
    REPO / "workstreams" / "steam_jp_common_messages_wave08" / "build_wave08_integration.py",
)


SCHEMA = "nobu16.kr.steam-jp-clan-label-normalization-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-clan-label-normalization-validation.v1"
PRIVATE_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-clan-label-normalization-private-candidate.v1"
RESOURCE = "MSG_PK/JP/msgdata.bin"
NAME = "msgdata.bin"
OVERLAY_PATH = HERE / "public" / "msgdata_ko_steam_jp_clan_label_normalization_159.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = WAVE08.DEFAULT_STOCK_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_clan_label_normalization_v1_candidate"

ISSUE_NUMBER = 46
EVENT_FAMILY_START_ID = 14_519
EVENT_FAMILY_END_ID = 14_766
READING_START_ID = 14_777
READING_END_ID = 15_034
CLAN_SUFFIX = "가"
NORMALIZED_SUFFIX = " 가문"
NORMALIZED_ENTRY_COUNT = 159
NORMALIZED_IDS_SHA256 = "52141827153A2466A7629E593400E838CBAFBE6F8481D68997ECEE461322F58A"

# These IDs intentionally remain outside the normalization delta.  14542 is
# already correct; 14603 is a non-family item; 14767..14776 and 14777..15034
# are the separate named-family and reading domains.
ALREADY_NORMALIZED_ID = 14_542
NON_FAMILY_PRESERVE_ID = 14_603
NAMED_FAMILY_PRESERVE_IDS = tuple(range(14_767, 14_777))
READING_PRESERVE_IDS = tuple(range(READING_START_ID, READING_END_ID + 1))
ARAKI_ID = 14_692

WAVE08_MSGDATA_BASELINE_PIN = {
    "size": 496_866,
    "packed_sha256": "5469F26B0E75A2214969F2EBA66CD0C850D7BFEC9E3D344ECBC4DBD171110AA6",
    "raw_size": 494_900,
    "raw_sha256": "62E0209E7A9715C1D44BCE28E4C7D0CE2BBBDDD19A25DC21D4A3FA931CD8BC8D",
    "string_count": 29_218,
}
OUTPUT_CANDIDATE_PIN = {
    "size": 497_505,
    "packed_sha256": "E783C492860BDC6229A3A05343635FEB05435D3751BBB2670F691F270DA484B6",
    "raw_size": 495_536,
    "raw_sha256": "7276B55F4E5C95728DA9DFA3372F037FE256587F0761E87BA6C87F75DA8BE597",
    "string_count": 29_218,
}


class ClanLabelNormalizationError(ValueError):
    """A source, wave08-baseline, overlay, or structure contract differed."""


@dataclass(frozen=True)
class BaselineContext:
    stock: Any
    packed: bytes
    raw: bytes
    table: Any
    wave08_metrics: dict[str, Any]


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def packed_spec(packed: bytes) -> dict[str, Any]:
    _header, raw = COMMON.decompress_wrapper(packed)
    table = COMMON.parse_message_table(raw)
    return {
        "size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }


def _require_exact_pin(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    if actual != expected:
        raise ClanLabelNormalizationError(
            f"{label} pin differs: expected={expected!r}, actual={actual!r}"
        )


def build_wave08_baseline(stock_root: Path) -> BaselineContext:
    """Return the exact current wave08+surname msgdata baseline in memory."""
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgdata",
    )
    candidates, wave08_metrics = WAVE08.build_all(stock_root)
    if set(candidates) != set(COMMON.FILES):
        raise ClanLabelNormalizationError("wave08 baseline resource domain differs")
    if wave08_metrics.get("applied_entries") != 40_581:
        raise ClanLabelNormalizationError("wave08 applied-entry accounting differs")
    if wave08_metrics.get("surname_recovery_delta_entries") != 980:
        raise ClanLabelNormalizationError("wave08 surname-recovery accounting differs")
    if wave08_metrics.get("wave08_semantic_delta_entries") != 94:
        raise ClanLabelNormalizationError("wave08 semantic accounting differs")
    packed = candidates.get(NAME)
    if not isinstance(packed, bytes):
        raise ClanLabelNormalizationError("wave08 msgdata candidate is absent")
    baseline_spec = packed_spec(packed)
    _require_exact_pin(baseline_spec, WAVE08_MSGDATA_BASELINE_PIN, "wave08+surname msgdata")
    metric_spec = wave08_metrics.get("candidates", {}).get(NAME)
    expected_metric_spec = {
        **WAVE08_MSGDATA_BASELINE_PIN,
        "sha256": WAVE08_MSGDATA_BASELINE_PIN["packed_sha256"],
    }
    if metric_spec != expected_metric_spec:
        raise ClanLabelNormalizationError("wave08 metadata baseline pin differs")
    _header, raw = COMMON.decompress_wrapper(packed)
    table = COMMON.parse_message_table(raw)
    if table.string_count != stock.table.string_count:
        raise ClanLabelNormalizationError("wave08 baseline string domain differs")
    return BaselineContext(stock, packed, raw, table, wave08_metrics)


def selected_ids(texts: tuple[str, ...] | list[str]) -> list[int]:
    """Select exactly the family-label subdomain, not its neighboring readings."""
    if len(texts) != WAVE08_MSGDATA_BASELINE_PIN["string_count"]:
        raise ClanLabelNormalizationError("baseline text-domain size differs")
    selected = [
        entry_id
        for entry_id in range(EVENT_FAMILY_START_ID, EVENT_FAMILY_END_ID + 1)
        if texts[entry_id].endswith(CLAN_SUFFIX)
    ]
    if len(selected) != NORMALIZED_ENTRY_COUNT:
        raise ClanLabelNormalizationError("selected clan-label count differs")
    if COMMON.canonical_hash(selected) != NORMALIZED_IDS_SHA256:
        raise ClanLabelNormalizationError("selected clan-label ID hash differs")
    if ALREADY_NORMALIZED_ID in selected or NON_FAMILY_PRESERVE_ID in selected:
        raise ClanLabelNormalizationError("an explicit preserve ID entered the normalization delta")
    if set(selected) & set(NAMED_FAMILY_PRESERVE_IDS):
        raise ClanLabelNormalizationError("a named-family preserve ID entered the delta")
    if set(selected) & set(READING_PRESERVE_IDS):
        raise ClanLabelNormalizationError("a reading preserve ID entered the delta")
    return selected


def _assert_baseline_anchors(context: BaselineContext, selected: list[int]) -> None:
    texts = context.table.texts
    if texts[ALREADY_NORMALIZED_ID] != "오다 가문":
        raise ClanLabelNormalizationError("already-normalized Oda anchor differs")
    if texts[ARAKI_ID] != "아라키가" or ARAKI_ID not in selected:
        raise ClanLabelNormalizationError("Araki normalization anchor differs")
    if NON_FAMILY_PRESERVE_ID in selected:
        raise ClanLabelNormalizationError("14603 entered the normalization delta")
    if any(entry_id in selected for entry_id in NAMED_FAMILY_PRESERVE_IDS):
        raise ClanLabelNormalizationError("14767..14776 entered the normalization delta")
    if any(entry_id in selected for entry_id in READING_PRESERVE_IDS):
        raise ClanLabelNormalizationError("14777..15034 entered the normalization delta")


def expected_overlay(stock_root: Path, context: BaselineContext | None = None) -> dict[str, Any]:
    """Model the source-free tracked overlay from pinned inputs only."""
    context = context or build_wave08_baseline(stock_root)
    selected = selected_ids(context.table.texts)
    _assert_baseline_anchors(context, selected)
    entries: list[dict[str, Any]] = []
    for entry_id in selected:
        baseline_ko = context.table.texts[entry_id]
        normalized = baseline_ko[: -len(CLAN_SUFFIX)] + NORMALIZED_SUFFIX
        if not baseline_ko.endswith(CLAN_SUFFIX) or normalized == baseline_ko:
            raise ClanLabelNormalizationError(f"normalization rule differs at {entry_id}")
        entries.append(
            {
                "id": entry_id,
                "stock_jp_utf16le_sha256": COMMON.text_hash(context.stock.table.texts[entry_id]),
                "baseline_ko_utf16le_sha256": COMMON.text_hash(baseline_ko),
                "ko": normalized,
                "ko_utf16le_sha256": COMMON.text_hash(normalized),
            }
        )
    if [entry["id"] for entry in entries] != selected:
        raise ClanLabelNormalizationError("overlay IDs differ from selected IDs")
    araki = next((entry for entry in entries if entry["id"] == ARAKI_ID), None)
    if not isinstance(araki, dict) or araki.get("ko") != "아라키 가문":
        raise ClanLabelNormalizationError("Araki output anchor differs")
    return {
        "schema": SCHEMA,
        "overlay_id": "msgdata_ko_steam_jp_clan_label_normalization_159.v1",
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": {
            "workstream": "steam_jp_common_messages_wave08",
            "candidate": WAVE08_MSGDATA_BASELINE_PIN,
            "source": "deterministic_wave08_plus_surname_msgdata_candidate",
        },
        "normalization": {
            "event_family_id_range": [EVENT_FAMILY_START_ID, EVENT_FAMILY_END_ID],
            "source_terminal_suffix": CLAN_SUFFIX,
            "replacement_suffix": NORMALIZED_SUFFIX,
            "entry_count": NORMALIZED_ENTRY_COUNT,
            "selected_ids_sha256": NORMALIZED_IDS_SHA256,
            "preserved_ids": {
                "already_normalized": [ALREADY_NORMALIZED_ID],
                "non_family": [NON_FAMILY_PRESERVE_ID],
                "named_family_range": [NAMED_FAMILY_PRESERVE_IDS[0], NAMED_FAMILY_PRESERVE_IDS[-1]],
                "reading_range": [READING_START_ID, READING_END_ID],
            },
        },
        "provenance": {
            "baseline_ko_hashes_fail_closed": True,
            "current_jp_source_hashes_fail_closed": True,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
        "entry_count": len(entries),
        "entries": entries,
    }


def load_overlay(stock_root: Path, context: BaselineContext | None = None) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    expected = expected_overlay(stock_root, context)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise ClanLabelNormalizationError("tracked clan-label overlay differs from deterministic model")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    """Return the one-file post-wave08 candidate and its private diagnostics."""
    context = build_wave08_baseline(stock_root)
    overlay, overlay_blob = load_overlay(stock_root, context)
    selected = selected_ids(context.table.texts)
    if overlay.get("entry_count") != NORMALIZED_ENTRY_COUNT:
        raise ClanLabelNormalizationError("overlay entry count differs")
    entries = overlay.get("entries")
    if not isinstance(entries, list) or [entry.get("id") for entry in entries] != selected:
        raise ClanLabelNormalizationError("overlay ID domain differs")

    texts = list(context.table.texts)
    changed: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ClanLabelNormalizationError("overlay entry is not an object")
        entry_id = entry.get("id")
        if type(entry_id) is not int or entry_id not in selected:
            raise ClanLabelNormalizationError("overlay entry ID differs")
        baseline_ko = texts[entry_id]
        if COMMON.text_hash(context.stock.table.texts[entry_id]) != entry.get("stock_jp_utf16le_sha256"):
            raise ClanLabelNormalizationError(f"stock JP source hash differs at {entry_id}")
        if COMMON.text_hash(baseline_ko) != entry.get("baseline_ko_utf16le_sha256"):
            raise ClanLabelNormalizationError(f"baseline Korean hash differs at {entry_id}")
        replacement = entry.get("ko")
        if not isinstance(replacement, str) or "\0" in replacement:
            raise ClanLabelNormalizationError(f"Korean replacement differs at {entry_id}")
        if COMMON.text_hash(replacement) != entry.get("ko_utf16le_sha256"):
            raise ClanLabelNormalizationError(f"Korean replacement hash differs at {entry_id}")
        expected = baseline_ko[: -len(CLAN_SUFFIX)] + NORMALIZED_SUFFIX
        if replacement != expected:
            raise ClanLabelNormalizationError(f"normalization text differs at {entry_id}")
        texts[entry_id] = replacement
        changed.add(entry_id)

    if changed != set(selected) or len(changed) != NORMALIZED_ENTRY_COUNT:
        raise ClanLabelNormalizationError("normalization delta differs")
    if texts[ALREADY_NORMALIZED_ID] != "오다 가문":
        raise ClanLabelNormalizationError("Oda anchor changed")
    if texts[ARAKI_ID] != "아라키 가문":
        raise ClanLabelNormalizationError("Araki output anchor changed")
    for entry_id in (NON_FAMILY_PRESERVE_ID, *NAMED_FAMILY_PRESERVE_IDS, *READING_PRESERVE_IDS):
        if texts[entry_id] != context.table.texts[entry_id]:
            raise ClanLabelNormalizationError(f"preserved baseline text changed at {entry_id}")

    rebuilt_raw = COMMON.rebuild_message_table(context.stock.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise ClanLabelNormalizationError("rebuilt clan-label table differs")
    if not COMMON._opaque_structure_preserved(context.stock.table, reparsed, rebuilt_raw):
        raise ClanLabelNormalizationError("candidate opaque structure differs")
    for entry_id, baseline_ko in enumerate(context.table.texts):
        if entry_id not in changed and reparsed.texts[entry_id] != baseline_ko:
            raise ClanLabelNormalizationError(f"non-delta text changed at {entry_id}")

    candidate = COMMON.recompress_wrapper(rebuilt_raw, context.stock.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != context.stock.packed[:8]:
        raise ClanLabelNormalizationError("candidate wrapper round-trip differs")
    candidate_spec = packed_spec(candidate)
    _require_exact_pin(candidate_spec, OUTPUT_CANDIDATE_PIN, "clan-label diagnostic candidate")
    return candidate, {
        "schema": PRIVATE_MANIFEST_SCHEMA,
        "resource": RESOURCE,
        "issue": ISSUE_NUMBER,
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "wave08_baseline": WAVE08_MSGDATA_BASELINE_PIN,
        "candidate": candidate_spec,
        "overlay": {
            "size": len(overlay_blob),
            "sha256": sha256(overlay_blob),
        },
        "normalization_delta_count": len(changed),
        "selected_ids_sha256": NORMALIZED_IDS_SHA256,
        "anchors": {
            "14542": "오다 가문",
            "14692": "아라키 가문",
        },
        "preservation": {
            "14603_preserved": True,
            "14767_14776_preserved": True,
            "14777_15034_preserved": True,
            "non_delta_texts_preserved": True,
        },
        "id_domain_preserved": True,
        "string_count_preserved": True,
        "opaque_non_string_metadata_preserved": True,
        "wrapper_prefix_preserved": True,
        "installed_game_files_modified": False,
        "sc_binary_used": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "target": {
            "base_language": "JP",
            "steam_version": "1.1.7",
        },
        "normalization": {
            "entry_count": NORMALIZED_ENTRY_COUNT,
            "selected_ids_sha256": NORMALIZED_IDS_SHA256,
            "event_family_id_range": [EVENT_FAMILY_START_ID, EVENT_FAMILY_END_ID],
            "source_terminal_suffix": CLAN_SUFFIX,
            "replacement_suffix": NORMALIZED_SUFFIX,
        },
        "expected": {
            "stock_jp": metrics["stock_jp"],
            "wave08_baseline": metrics["wave08_baseline"],
            "candidate": metrics["candidate"],
            "overlay": metrics["overlay"],
        },
        "anchors": metrics["anchors"],
        "preservation": metrics["preservation"],
        "proofs": {
            "deterministic_ab_equal": True,
            "stock_jp_hash_pinned": True,
            "wave08_baseline_hash_pinned": True,
            "baseline_ko_hashes_fail_closed": True,
            "current_jp_source_hashes_fail_closed": True,
            "id_domain_preserved": metrics["id_domain_preserved"],
            "string_count_preserved": metrics["string_count_preserved"],
            "opaque_non_string_metadata_preserved": metrics["opaque_non_string_metadata_preserved"],
            "wrapper_prefix_preserved": metrics["wrapper_prefix_preserved"],
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    context = build_wave08_baseline(stock_root)
    COMMON.atomic_write(OVERLAY_PATH, COMMON.pretty_bytes(expected_overlay(stock_root, context)))
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise ClanLabelNormalizationError("deterministic A/B clan-label build differs")
    COMMON.atomic_write(VALIDATION_PATH, COMMON.pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise ClanLabelNormalizationError("deterministic A/B clan-label build differs")
    validation, blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or blob != COMMON.pretty_bytes(expected):
        raise ClanLabelNormalizationError("tracked clan-label validation differs")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def safe_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents or resolved.exists():
        raise ClanLabelNormalizationError(f"unsafe or existing output root: {resolved}")
    return resolved


def build(stock_root: Path, output_root: Path) -> Path:
    candidate, metrics = build_blob(stock_root)
    destination = safe_output_root(output_root)
    try:
        target = destination / Path(RESOURCE)
        target.parent.mkdir(parents=True, exist_ok=False)
        target.write_bytes(candidate)
        (destination / "private_manifest.json").write_bytes(COMMON.pretty_bytes(metrics))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "verify", "build"):
        child = commands.add_parser(command)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        print(json.dumps(generate(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        print(json.dumps(verify(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(build(args.stock_root, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
