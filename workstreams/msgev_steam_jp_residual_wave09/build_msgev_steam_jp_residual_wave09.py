#!/usr/bin/env python3
"""Build a bounded, JP-only Wave09 residual-event overlay for ``msgev.bin``.

The input is reconstructed entirely in memory from the pristine Steam 1.1.7
Japanese resource and the deterministic Wave08 baseline.  Tracked artifacts
contain only project-authored Korean, integer IDs, hashes, and structural
proofs; they never include Japanese source strings or a complete game binary.
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
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from translations import EVENT_LABEL_IDS, EVENT_STORY_IDS, TARGET_IDS, TARGET_TRANSLATIONS


REPO = HERE.parents[1]


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE08 = import_file(
    "msgev_steam_jp_residual_wave09_wave08",
    REPO
    / "workstreams"
    / "steam_jp_common_messages_wave08"
    / "build_wave08_integration.py",
)
COMMON = WAVE08.COMMON


SCHEMA = "nobu16.kr.steam-jp-msgev-residual-wave09-overlay.v1"
TRACE_SCHEMA = "nobu16.kr.steam-jp-msgev-residual-wave09-hash-trace.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgev-residual-wave09-validation.v1"
PRIVATE_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgev-residual-wave09-private-candidate.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
NAME = "msgev.bin"

OVERLAY_PATH = HERE / "public" / "msgev_ko_steam_jp_residual_wave09_66.v1.json"
TRACE_PATH = HERE / "evidence" / "msgev_residual_wave09_hash_anchors.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = WAVE08.DEFAULT_STOCK_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "msgev_steam_jp_residual_wave09_candidate"

# This is the post-Wave08 / post-surname deterministic JP baseline, not an
# installed game file.  It is deliberately pinned before a residual row may be
# replaced, which prevents silent overlap with existing work.
WAVE08_BASELINE_PIN = {
    "size": 1_039_928,
    "sha256": "39E8FEE6C4A7F1EB5018F01FB9446C9866E85BF13509C2CE099849E7AA3AAECD",
    "packed_sha256": "39E8FEE6C4A7F1EB5018F01FB9446C9866E85BF13509C2CE099849E7AA3AAECD",
    "raw_size": 1_035_840,
    "raw_sha256": "E1D78EBEDC2B6C42036D2D967CF7A83C0703DAA6B477D333F516EE476626C033",
    "string_count": 17_916,
}

OUTPUT_CANDIDATE_PIN: dict[str, Any] | None = {
    "size": 1_040_799,
    "sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "packed_sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "raw_size": 1_036_708,
    "raw_sha256": "6D87086EA6B533EAB3F3745DB7564E8D7842E7DD603AD765B2D6D900644E00FB",
    "string_count": 17_916,
}

EVENT_STORY_IDS_SHA256 = "71224967C0B366AE5D8FCBF641D74E1281B0B4982B4C3F31442070FAE8B4B95D"
EVENT_LABEL_IDS_SHA256 = "E08266E2FFF2E45F4EBD13402E3DC89E238691664C7D3FFBDDC5F1228736FC09"
TARGET_IDS_SHA256 = "ACF81701ED58889837F38211CD91691B58795D0A9E3C2F9151F3748E473E047E"
EXPECTED_BASE_EXACT_CONTRACT_OVERLAP = 5


class MsgEvResidualWave09Error(ValueError):
    """A JP source, baseline, overlay, or binary contract differed."""


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
        "sha256": sha256(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }


def path_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def require_exact(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise MsgEvResidualWave09Error(
            f"{label} differs: expected={expected!r}, actual={actual!r}"
        )


def _exact_contract_ids() -> set[int]:
    """Return source-equal Wave08 coordinates, which remain owned/no-op rows."""
    path = (
        REPO
        / "workstreams"
        / "steam_jp_common_messages_wave08"
        / "public"
        / "exact_contract"
        / "msgev_exact_contract_83.v1.json"
    )
    value, _blob = COMMON.read_json(path)
    if value.get("resource") != RESOURCE or value.get("entry_count") != 83:
        raise MsgEvResidualWave09Error("Wave08 exact-contract scope differs")
    mappings = value.get("mappings")
    if not isinstance(mappings, list) or len(mappings) != 83:
        raise MsgEvResidualWave09Error("Wave08 exact-contract mappings differ")
    ids: set[int] = set()
    for row in mappings:
        if not (isinstance(row, list) and len(row) == 3 and type(row[0]) is int):
            raise MsgEvResidualWave09Error("Wave08 exact-contract mapping row differs")
        ids.add(row[0])
    if len(ids) != 83:
        raise MsgEvResidualWave09Error("Wave08 exact-contract ID uniqueness differs")
    return ids


def owned_wave08_ids() -> set[int]:
    """Collect all currently owned ``msgev`` coordinates before Wave09."""
    base_overlays, _base_blobs = COMMON.load_public_overlays()
    base = base_overlays.get(NAME)
    if not isinstance(base, dict) or base.get("resource") != RESOURCE:
        raise MsgEvResidualWave09Error("base msgev overlay is unavailable")
    base_ids = {int(entry["id"]) for entry in base.get("entries", [])}
    if len(base_ids) != int(base.get("entry_count", -1)):
        raise MsgEvResidualWave09Error("base msgev ID domain differs")

    deltas, _artifacts = WAVE08.load_semantic_overlays()
    semantic_ids = {int(entry["id"]) for entry in deltas.get(RESOURCE, [])}
    if len(semantic_ids) != 69:
        raise MsgEvResidualWave09Error("Wave08 semantic msgev domain differs")
    exact_ids = _exact_contract_ids()
    if base_ids & semantic_ids or semantic_ids & exact_ids:
        raise MsgEvResidualWave09Error("semantic Wave08 ownership overlaps unexpectedly")
    if len(base_ids & exact_ids) != EXPECTED_BASE_EXACT_CONTRACT_OVERLAP:
        raise MsgEvResidualWave09Error("base/exact Wave08 ownership overlap differs")
    owned = base_ids | semantic_ids | exact_ids
    return owned


def build_wave08_baseline(stock_root: Path) -> BaselineContext:
    """Rebuild and exact-pin the current post-Wave08 Korean baseline."""
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgev",
    )
    candidates, wave08_metrics = WAVE08.build_all(stock_root)
    packed = candidates.get(NAME)
    if not isinstance(packed, bytes):
        raise MsgEvResidualWave09Error("Wave08 msgev candidate is absent")
    require_exact(packed_spec(packed), WAVE08_BASELINE_PIN, "post-Wave08 msgev baseline pin")
    require_exact(
        wave08_metrics.get("candidates", {}).get(NAME),
        WAVE08_BASELINE_PIN,
        "Wave08 msgev metadata baseline pin",
    )
    _header, raw = COMMON.decompress_wrapper(packed)
    table = COMMON.parse_message_table(raw)
    if table.string_count != stock.table.string_count:
        raise MsgEvResidualWave09Error("stock and Wave08 baseline text domains differ")
    return BaselineContext(stock, packed, raw, table, wave08_metrics)


def category_for(entry_id: int) -> str:
    if entry_id in EVENT_STORY_IDS:
        return "event_story_residual"
    if entry_id in EVENT_LABEL_IDS:
        return "event_branch_or_condition_label"
    raise MsgEvResidualWave09Error(f"unclassified target ID: {entry_id}")


def format_signature(text: str) -> str:
    """Hash only structural invariants; never write source text to artifacts."""
    return COMMON.canonical_hash(COMMON.common.message_invariants(text))


def validate_target_domain(context: BaselineContext) -> None:
    if tuple(TARGET_TRANSLATIONS) != TARGET_IDS:
        raise MsgEvResidualWave09Error("translation insertion order differs")
    if TARGET_IDS != EVENT_STORY_IDS + EVENT_LABEL_IDS:
        raise MsgEvResidualWave09Error("target scope differs from declared batches")
    if tuple(sorted(TARGET_IDS)) != TARGET_IDS or len(set(TARGET_IDS)) != len(TARGET_IDS):
        raise MsgEvResidualWave09Error("target IDs are not sorted and unique")
    if len(EVENT_STORY_IDS) != 50 or len(EVENT_LABEL_IDS) != 16 or len(TARGET_IDS) != 66:
        raise MsgEvResidualWave09Error("bounded Wave09 target counts differ")
    if 10961 in TARGET_IDS:
        raise MsgEvResidualWave09Error("already Korean Wave08 coordinate entered Wave09")
    expected_hashes = {
        "event_story": EVENT_STORY_IDS_SHA256,
        "event_label": EVENT_LABEL_IDS_SHA256,
        "target": TARGET_IDS_SHA256,
    }
    observed_hashes = {
        "event_story": COMMON.canonical_hash(list(EVENT_STORY_IDS)),
        "event_label": COMMON.canonical_hash(list(EVENT_LABEL_IDS)),
        "target": COMMON.canonical_hash(list(TARGET_IDS)),
    }
    if any(not value for value in expected_hashes.values()) or expected_hashes != observed_hashes:
        raise MsgEvResidualWave09Error("target ID hash anchors differ")

    owned = owned_wave08_ids()
    overlap = sorted(set(TARGET_IDS) & owned)
    if overlap:
        raise MsgEvResidualWave09Error(f"Wave09 overlaps an already owned coordinate: {overlap}")

    for entry_id in TARGET_IDS:
        if not 0 <= entry_id < context.stock.table.string_count:
            raise MsgEvResidualWave09Error(f"target ID outside msgev domain: {entry_id}")
        source = context.stock.table.texts[entry_id]
        baseline = context.table.texts[entry_id]
        replacement = TARGET_TRANSLATIONS[entry_id]
        if baseline != source:
            raise MsgEvResidualWave09Error(
                f"target baseline is no longer a pristine JP residual: {entry_id}"
            )
        if not source or not replacement:
            raise MsgEvResidualWave09Error(f"empty source or replacement at {entry_id}")
        mismatches = COMMON.common.invariant_mismatches(source, replacement)
        if mismatches:
            raise MsgEvResidualWave09Error(
                f"format invariant differs at {entry_id}: {mismatches}"
            )


def trace_entry(context: BaselineContext, entry_id: int) -> dict[str, Any]:
    source = context.stock.table.texts[entry_id]
    baseline = context.table.texts[entry_id]
    replacement = TARGET_TRANSLATIONS[entry_id]
    return {
        "id": entry_id,
        "category": category_for(entry_id),
        "source_jp_utf16le_sha256": COMMON.text_hash(source),
        "wave08_baseline_utf16le_sha256": COMMON.text_hash(baseline),
        "ko_utf16le_sha256": COMMON.text_hash(replacement),
        "format_invariants_sha256": format_signature(source),
    }


def expected_trace(context: BaselineContext) -> dict[str, Any]:
    validate_target_domain(context)
    return {
        "schema": TRACE_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": {
            "workstream": "steam_jp_common_messages_wave08",
            "candidate": WAVE08_BASELINE_PIN,
            "source": "deterministic_wave08_plus_surname_recovery",
        },
        "scope": {
            "event_story_ids": list(EVENT_STORY_IDS),
            "event_label_ids": list(EVENT_LABEL_IDS),
            "target_ids_sha256": TARGET_IDS_SHA256,
        },
        "entry_count": len(TARGET_IDS),
        "entries": [trace_entry(context, entry_id) for entry_id in TARGET_IDS],
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
    }


def expected_overlay(context: BaselineContext) -> dict[str, Any]:
    validate_target_domain(context)
    trace_by_id = {row["id"]: row for row in expected_trace(context)["entries"]}
    return {
        "schema": SCHEMA,
        "overlay_id": "msgev_ko_steam_jp_residual_wave09_66.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": {
            "workstream": "steam_jp_common_messages_wave08",
            "candidate": WAVE08_BASELINE_PIN,
            "source": "deterministic_wave08_plus_surname_recovery",
        },
        "scope": {
            "event_story_entry_count": len(EVENT_STORY_IDS),
            "event_label_entry_count": len(EVENT_LABEL_IDS),
            "ids_sha256": TARGET_IDS_SHA256,
        },
        "provenance": {
            "current_jp_source_hashes_fail_closed": True,
            "wave08_baseline_hashes_fail_closed": True,
            "format_invariants_fail_closed": True,
            "existing_coordinate_overlap_checked": True,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
        "entry_count": len(TARGET_IDS),
        "entries": [
            {
                **trace_by_id[entry_id],
                "ko": TARGET_TRANSLATIONS[entry_id],
            }
            for entry_id in TARGET_IDS
        ],
    }


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    """Build the one-resource Wave09 candidate without touching game files."""
    context = build_wave08_baseline(stock_root)
    validate_target_domain(context)
    texts = list(context.table.texts)
    for entry_id in TARGET_IDS:
        texts[entry_id] = TARGET_TRANSLATIONS[entry_id]

    rebuilt_raw = COMMON.rebuild_message_table(context.stock.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise MsgEvResidualWave09Error("rebuilt message table differs")
    if not COMMON._opaque_structure_preserved(context.stock.table, reparsed, rebuilt_raw):
        raise MsgEvResidualWave09Error("opaque msgev metadata differs")
    for entry_id, baseline in enumerate(context.table.texts):
        if entry_id not in TARGET_IDS and reparsed.texts[entry_id] != baseline:
            raise MsgEvResidualWave09Error(f"non-target text changed: {entry_id}")

    packed = COMMON.recompress_wrapper(rebuilt_raw, context.stock.packed)
    _header, roundtrip = COMMON.decompress_wrapper(packed)
    if roundtrip != rebuilt_raw or packed[:8] != context.stock.packed[:8]:
        raise MsgEvResidualWave09Error("wrapper round-trip or prefix differs")
    candidate = packed_spec(packed)
    if OUTPUT_CANDIDATE_PIN is not None:
        require_exact(candidate, OUTPUT_CANDIDATE_PIN, "Wave09 output candidate pin")
    return packed, {
        "status": "PASS",
        "resource": RESOURCE,
        "wave08_baseline": WAVE08_BASELINE_PIN,
        "residual_event_story_delta_count": len(EVENT_STORY_IDS),
        "residual_event_label_delta_count": len(EVENT_LABEL_IDS),
        "residual_delta_count": len(TARGET_IDS),
        "candidate": candidate,
        "target_ids_sha256": TARGET_IDS_SHA256,
        "id_domain_preserved": True,
        "string_count_preserved": True,
        "opaque_non_string_metadata_preserved": True,
        "non_target_texts_preserved": True,
        "wrapper_prefix_preserved": True,
        "format_invariants_preserved": True,
        "existing_coordinate_overlap_checked": True,
        "sc_binary_used": False,
        "sc_runtime_path_used": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "target": {
            "base_language": "JP",
            "steam_version": "1.1.7",
            "resource": RESOURCE,
        },
        "translation": {
            "event_story_delta_count": len(EVENT_STORY_IDS),
            "event_label_delta_count": len(EVENT_LABEL_IDS),
            "total_delta_count": len(TARGET_IDS),
            "target_ids_sha256": TARGET_IDS_SHA256,
        },
        "expected": {
            "wave08_baseline": WAVE08_BASELINE_PIN,
            "candidate": metrics["candidate"],
            "overlay": path_spec(OVERLAY_PATH),
            "trace": path_spec(TRACE_PATH),
        },
        "proofs": {
            "deterministic_ab_equal": True,
            "pristine_jp_hashes_fail_closed": True,
            "wave08_baseline_hashes_fail_closed": True,
            "format_invariants_preserved": True,
            "existing_coordinate_overlap_checked": True,
            "id_domain_preserved": True,
            "non_target_texts_preserved": True,
            "opaque_non_string_metadata_preserved": True,
            "wrapper_prefix_preserved": True,
        },
        "safety": {
            "complete_candidate_binaries_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    """Write source-free tracked artifacts for the current pinned input only."""
    context = build_wave08_baseline(stock_root)
    trace = expected_trace(context)
    overlay = expected_overlay(context)
    COMMON.atomic_write(TRACE_PATH, COMMON.pretty_bytes(trace))
    COMMON.atomic_write(OVERLAY_PATH, COMMON.pretty_bytes(overlay))
    _packed, metrics = build_blob(stock_root)
    COMMON.atomic_write(VALIDATION_PATH, COMMON.pretty_bytes(validation_model(metrics)))
    return metrics


def verify(stock_root: Path) -> dict[str, Any]:
    """Perform a read-only deterministic verification of all public artifacts."""
    if OUTPUT_CANDIDATE_PIN is None:
        raise MsgEvResidualWave09Error("output candidate pin is not committed")
    context = build_wave08_baseline(stock_root)
    expected_trace_value = expected_trace(context)
    expected_overlay_value = expected_overlay(context)
    trace, trace_blob = COMMON.read_json(TRACE_PATH)
    overlay, overlay_blob = COMMON.read_json(OVERLAY_PATH)
    if trace != expected_trace_value or trace_blob != COMMON.pretty_bytes(expected_trace_value):
        raise MsgEvResidualWave09Error("tracked Wave09 hash trace differs")
    if overlay != expected_overlay_value or overlay_blob != COMMON.pretty_bytes(expected_overlay_value):
        raise MsgEvResidualWave09Error("tracked Wave09 overlay differs")

    first_packed, first = build_blob(stock_root)
    second_packed, second = build_blob(stock_root)
    if first_packed != second_packed or first != second:
        raise MsgEvResidualWave09Error("deterministic A/B build differs")
    validation, validation_blob = COMMON.read_json(VALIDATION_PATH)
    expected_validation = validation_model(first)
    if validation != expected_validation or validation_blob != COMMON.pretty_bytes(expected_validation):
        raise MsgEvResidualWave09Error("tracked Wave09 validation differs")
    return {**first, "deterministic_ab_equal": True}


def output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    if resolved == tmp or tmp not in resolved.parents or resolved.exists():
        raise MsgEvResidualWave09Error(f"unsafe or existing output root: {resolved}")
    return resolved


def build(stock_root: Path, destination: Path) -> Path:
    destination = output_root(destination)
    packed, metrics = build_blob(stock_root)
    target = destination / Path(RESOURCE)
    target.parent.mkdir(parents=True, exist_ok=False)
    target.write_bytes(packed)
    manifest = {
        "schema": PRIVATE_MANIFEST_SCHEMA,
        "resource": RESOURCE,
        "candidate": metrics["candidate"],
        "residual_delta_count": len(TARGET_IDS),
        "target_ids_sha256": TARGET_IDS_SHA256,
    }
    COMMON.atomic_write(destination / "private_manifest.json", COMMON.pretty_bytes(manifest))
    return destination


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
    elif args.command == "verify":
        result = verify(args.stock_root)
    else:
        destination = build(args.stock_root, args.output_root)
        result = {"status": "BUILT", "output_root": str(destination)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
