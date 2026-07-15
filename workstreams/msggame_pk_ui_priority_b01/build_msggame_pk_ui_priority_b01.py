#!/usr/bin/env python3
"""Build the source-free PK msggame UI-priority translation batch B01."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
B03_ROOT = REPO_ROOT / "workstreams" / "switch_msggame_v13_human_review_b03"
sys.path[:0] = [str(WORKSTREAM_ROOT), str(B03_ROOT)]

import build_switch_msggame_v13_human_review_b03 as previous  # noqa: E402


_TRANSLATIONS_SPEC = importlib.util.spec_from_file_location(
    "msggame_pk_ui_priority_b01_translations",
    WORKSTREAM_ROOT / "ui_translations.py",
)
if _TRANSLATIONS_SPEC is None or _TRANSLATIONS_SPEC.loader is None:
    raise RuntimeError("cannot load B01 UI translations")
_TRANSLATIONS_MODULE = importlib.util.module_from_spec(_TRANSLATIONS_SPEC)
_TRANSLATIONS_SPEC.loader.exec_module(_TRANSLATIONS_MODULE)
TRANSLATIONS = _TRANSLATIONS_MODULE.TRANSLATIONS


recovery = previous.recovery
BATCH_ID = "pk_msggame_ui_priority_b01_150.v1"
RESOURCE = recovery.RESOURCE
OVERLAY_NAME = "msggame_ko_pk_ui_priority_b01_150.v1.json"
EVIDENCE_NAME = "msggame_pk_ui_priority_b01_evidence.v1.json"
REVIEW_NAME = "msggame_pk_ui_priority_b01_review.v1.json"
VALIDATION_NAME = "msggame_pk_ui_priority_b01_validation.v1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()
B03_RELATIVE = (
    B03_ROOT / "public" / previous.OVERLAY_NAME
).relative_to(REPO_ROOT).as_posix()
B03_OVERLAY_PIN = {
    "size": 34_570,
    "sha256": "6279D3C7D7139EED15670309F7DAD3E993359821985DA3194E392439B3C77302",
}
PREDECESSOR_PATHS_PIN = "5D93E45C7A82201B811A22BDD069D942C58CF93CFEF77938636CED2FF3A03907"
PREDECESSOR_COORDINATE_COUNT = 10_149
SELECTED_COORDINATES_PIN = "CB5EFAF169E00B4EA19B125877E8F4DEC52917E4096CE0F5DE659E8BF9DC7017"
FALSE_POSITIVE = (7, 2076, 0)
FALSE_POSITIVE_SKELETON_PIN = "A9037545625B6D4A8020180B954BB73D5E3E4AB13CA5D9A8A2C7BEEA63DE2990"
EN_PACKED_PIN = {
    "size": 714_037,
    "sha256": "14D9A20ECB35F35C91D14947921CF09F5EAF960F8FA4D70F703F2366DB1D13AF",
    "raw_size": 2_169_852,
    "raw_sha256": "03A1D07A4FFB460F393A47A047EFF596BBCE6BAADAE22EB00B3686E8AF96D39E",
}


MENU_NAVIGATION_IDS = frozenset({273, 277, 285, 363, 442, 589, 612})
CONFIGURATION_IDS = frozenset(
    {
        357, 366, 368, 370, 473, 475, 476, 481, 482, 488, 489,
        570, 571, 572, 573, 574, 575, 576, 577, 578, 581, 582,
        586, 587, 603, 604, 605, 606, 619, 620,
    }
)
BATTLE_HELP_IDS = frozenset(
    {
        329, 333, 334, 335, 336, 337, 338, 342, 344, 345, 346,
        347, 348, 349, 350, 390, 396, 410, 444, 453, 454, 463,
        465, 479, 500, 524, 526, 535, 545, 549, 551, 552, 553,
        554, 555, 556, 557, 558, 559, 561, 562, 563, 564, 565,
        566, 567, 568, 569, 579, 580, 607, 609, 610, 617, 618,
        621, 622, 623, 624,
    }
)


class BatchError(ValueError):
    """Raised when a pinned input or translation contract changes."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BatchError(f"JSON root is not an object: {path}")
    return value


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    if path.parent.name in {"public", "evidence", "review"}:
        relative = Path(path.parent.name) / path.name
    else:
        relative = Path(path.name)
    return {"path": relative.as_posix(), "size": len(blob), "sha256": recovery.sha256(blob)}


def assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = recovery.script_counts(path.read_text(encoding="utf-8"))
        result[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise BatchError(f"commercial source script leaked into artifact: {path}")
    return result


def _overlay_coordinates(path: Path) -> set[tuple[int, int, int]]:
    overlay = read_json(path)
    if overlay.get("resource") != RESOURCE or not isinstance(overlay.get("entries"), list):
        raise BatchError(f"invalid existing msggame overlay: {path}")
    coordinates: set[tuple[int, int, int]] = set()
    for entry in overlay["entries"]:
        coordinate = (entry.get("block_id"), entry.get("record_id"), entry.get("literal_id"))
        if not all(type(value) is int for value in coordinate):
            raise BatchError(f"invalid existing coordinate: {path}")
        coordinates.add(coordinate)
    return coordinates


def collect_existing(progress_path: Path) -> dict[str, Any]:
    """Pin the exact B03 predecessor prefix and tolerate self/successors."""

    progress = read_json(progress_path)
    resources = progress.get("resources")
    matches = [item for item in resources if item.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise BatchError("progress must contain exactly one PK msggame resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise BatchError("PK msggame overlay_globs is invalid")
    if patterns.count(B03_RELATIVE) != 1:
        raise BatchError("B03 predecessor must be registered exactly once")
    self_count = patterns.count(SELF_RELATIVE)
    if self_count not in (0, 1):
        raise BatchError("self overlay must be absent or registered exactly once")

    marker = patterns.index(B03_RELATIVE)
    predecessor_patterns = patterns[: marker + 1]
    if recovery.canonical_hash(predecessor_patterns) != PREDECESSOR_PATHS_PIN:
        raise BatchError("pinned predecessor overlay prefix changed")

    resolved: dict[str, Path] = {}
    for pattern in patterns:
        found = sorted(REPO_ROOT.glob(pattern))
        if len(found) != 1:
            raise BatchError(f"progress pattern {pattern!r} resolved to {len(found)} files")
        resolved[pattern] = found[0]

    b03_path = resolved[B03_RELATIVE]
    if b03_path.stat().st_size != B03_OVERLAY_PIN["size"] or recovery.sha256(b03_path.read_bytes()) != B03_OVERLAY_PIN["sha256"]:
        raise BatchError("B03 predecessor overlay pin changed")

    predecessor_coordinates: set[tuple[int, int, int]] = set()
    predecessor_inputs: list[dict[str, Any]] = []
    for relative in predecessor_patterns:
        path = resolved[relative]
        predecessor_coordinates.update(_overlay_coordinates(path))
        predecessor_inputs.append(
            {"path": relative, "size": path.stat().st_size, "sha256": recovery.sha256(path.read_bytes())}
        )
    if len(predecessor_coordinates) != PREDECESSOR_COORDINATE_COUNT:
        raise BatchError(f"predecessor coordinate union changed: {len(predecessor_coordinates)}")

    all_coordinates: set[tuple[int, int, int]] = set()
    for relative, path in resolved.items():
        if relative != SELF_RELATIVE:
            all_coordinates.update(_overlay_coordinates(path))
    return {
        "predecessor_coordinates": predecessor_coordinates,
        "all_coordinates": all_coordinates,
        "predecessor_inputs": predecessor_inputs,
        "predecessor_normalized_sha256": recovery.canonical_hash(predecessor_inputs),
        "self_registration_count": self_count,
    }


def load_en(path: Path) -> dict[str, Any]:
    packed = path.read_bytes()
    if len(packed) != EN_PACKED_PIN["size"] or recovery.sha256(packed) != EN_PACKED_PIN["sha256"]:
        raise BatchError("PK EN msggame packed pin changed")
    _header, raw = recovery.decompress_wrapper(packed)
    if len(raw) != EN_PACKED_PIN["raw_size"] or recovery.sha256(raw) != EN_PACKED_PIN["raw_sha256"]:
        raise BatchError("PK EN msggame raw pin changed")
    parsed = recovery.parse_packed_msggame(packed)
    if recovery.rebuild_raw_msggame(parsed.archive) != raw:
        raise BatchError("PK EN msggame parse/rebuild is not byte-identical")
    return {"path": path, "packed": packed, "raw": raw, "archive": parsed.archive}


def category_for(coordinate: tuple[int, int, int], replacement: str) -> str:
    record_id = coordinate[1]
    if replacement.startswith("“") and replacement.endswith("”") and "\n" not in replacement:
        return "ui_label_or_title"
    if record_id in MENU_NAVIGATION_IDS:
        return "menu_navigation_and_input"
    if record_id in CONFIGURATION_IDS:
        return "settings_unlock_and_configuration"
    if record_id in BATTLE_HELP_IDS:
        return "battle_ui_and_system_help"
    return "management_tooltip_and_tutorial"


def _literal_hashes(literals: dict[tuple[int, int, int], Any], key: tuple[int, int]) -> list[str]:
    return [recovery.text_hash(literals[coordinate].text) for coordinate in sorted(literals) if coordinate[:2] == key]


def build(args: argparse.Namespace) -> dict[str, Any]:
    pk_jp_path = args.pk_jp.resolve()
    pk_sc_path = args.pk_sc.resolve()
    pk_en_path = args.pk_en.resolve()
    progress_path = args.progress.resolve()
    target_path = args.target_catalog.resolve()
    input_paths = (pk_jp_path, pk_sc_path, pk_en_path, progress_path, target_path)
    before = {str(path): recovery.sha256(path.read_bytes()) for path in input_paths}

    pk_jp = recovery.prior.load_standard_source(pk_jp_path, "pk_jp")
    pk_sc = recovery.prior.load_standard_source(pk_sc_path, "pk_sc")
    pk_en = load_en(pk_en_path)
    target = recovery.load_target_catalog(target_path)
    existing = collect_existing(progress_path)
    jp_literals = recovery.literal_map(pk_jp["archive"])
    sc_literals = recovery.literal_map(pk_sc["archive"])
    en_literals = recovery.literal_map(pk_en["archive"])
    sc_record_literal_counts = Counter(coordinate[:2] for coordinate in sc_literals)

    remaining_before = target["coordinates"] - existing["predecessor_coordinates"]
    structural_pool = sorted(
        coordinate
        for coordinate in remaining_before
        if coordinate in sc_literals
        and coordinate[0] == 13
        and coordinate[1] >= 256
        and coordinate[2] == 0
        and sc_record_literal_counts[coordinate[:2]] == 1
    )
    selected_coordinates = sorted(TRANSLATIONS)
    selected_set = set(selected_coordinates)
    if len(selected_coordinates) != 150 or structural_pool != selected_coordinates:
        raise BatchError("UI-priority structural pool changed")
    selected_hash = recovery.canonical_hash([list(value) for value in selected_coordinates])
    if selected_hash != SELECTED_COORDINATES_PIN:
        raise BatchError("selected coordinate pin changed")
    if selected_set & existing["all_coordinates"]:
        raise BatchError("translation overlaps an existing PK msggame overlay")
    if not selected_set <= target["coordinates"]:
        raise BatchError("translation escaped the exact target catalog")
    if FALSE_POSITIVE in selected_set or FALSE_POSITIVE in existing["predecessor_coordinates"]:
        raise BatchError("dynamic narrative false positive entered a translated overlay")
    if FALSE_POSITIVE not in target["coordinates"]:
        raise BatchError("dynamic narrative false positive left target catalog")

    selected: list[dict[str, Any]] = []
    for coordinate in selected_coordinates:
        source = sc_literals[coordinate].text
        replacement = TRANSLATIONS[coordinate]
        mismatches = recovery.invariant_mismatches(source, replacement)
        if mismatches:
            raise BatchError(f"invariant mismatch at {coordinate}: {mismatches}")
        if recovery.msggame_translation.bracket_sequence(source) != recovery.msggame_translation.bracket_sequence(replacement):
            raise BatchError(f"bracket sequence changed at {coordinate}")
        if recovery.delimiter_roles(source) != recovery.delimiter_roles(replacement):
            raise BatchError(f"delimiter roles changed at {coordinate}")
        if recovery.script_counts(replacement) != {"cjk_unified_count": 0, "kana_count": 0}:
            raise BatchError(f"forbidden source script remains at {coordinate}")
        if not recovery.prior.has_hangul_syllable(replacement):
            raise BatchError(f"replacement lacks Hangul at {coordinate}")
        selected.append(
            {
                "coordinate": coordinate,
                "replacement": replacement,
                "category": category_for(coordinate, replacement),
                "sc_hash": recovery.text_hash(source),
                "jp_hash": recovery.text_hash(jp_literals[coordinate].text) if coordinate in jp_literals else None,
                "en_hash": recovery.text_hash(en_literals[coordinate].text) if coordinate in en_literals else None,
                "replacement_hash": recovery.text_hash(replacement),
                "source_structure": recovery.source_structure(source),
                "replacement_structure": recovery.source_structure(replacement),
            }
        )
    category_counts = dict(sorted(Counter(item["category"] for item in selected).items()))

    fp_key = FALSE_POSITIVE[:2]
    sc_records = recovery.prior.record_map(pk_sc["archive"])
    jp_records = recovery.prior.record_map(pk_jp["archive"])
    en_records = recovery.prior.record_map(pk_en["archive"])
    fp_sc_skeleton = recovery.sha256(recovery.prior.record_skeleton(sc_records[fp_key]))
    fp_en_skeleton = recovery.sha256(recovery.prior.record_skeleton(en_records[fp_key]))
    if fp_sc_skeleton != FALSE_POSITIVE_SKELETON_PIN or fp_en_skeleton != fp_sc_skeleton:
        raise BatchError("dynamic narrative SC/EN record skeleton changed")
    fp_sc_hashes = _literal_hashes(sc_literals, fp_key)
    fp_jp_hashes = _literal_hashes(jp_literals, fp_key)
    fp_en_hashes = _literal_hashes(en_literals, fp_key)
    if not (len(fp_sc_hashes) == 2 and len(fp_jp_hashes) == 1 and len(fp_en_hashes) == 2):
        raise BatchError("dynamic narrative literal layout changed")

    overlay_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "source_sc_utf16le_sha256": item["sc_hash"],
            "ko": item["replacement"],
        }
        for item in selected
    ]
    overlay = {
        "schema": recovery.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "translation_provenance": {
            "kind": "agent_ui_priority_full_record_translation",
            "context_languages": ["SC", "JP", "EN"],
            "source_text_embedded": False,
            "runtime_reviewed": False,
        },
        "stock_sc": {
            "packed_size": len(pk_sc["packed"]),
            "packed_sha256": recovery.sha256(pk_sc["packed"]),
            "raw_size": len(pk_sc["raw"]),
            "raw_sha256": recovery.sha256(pk_sc["raw"]),
            "record_count": pk_sc["archive"].record_count,
            "literal_slot_count": len(sc_literals),
        },
        "entries": overlay_entries,
    }

    evidence_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "category": item["category"],
            "review_method": "agent_full_record_ui_context",
            "pk_sc_utf16le_sha256": item["sc_hash"],
            "pk_jp_utf16le_sha256": item["jp_hash"],
            "pk_en_utf16le_sha256": item["en_hash"],
            "replacement_utf16le_sha256": item["replacement_hash"],
            "pk_sc_structure": item["source_structure"],
            "replacement_structure": item["replacement_structure"],
            "complete_single_literal_record": True,
            "invariants_exact": True,
            "bracket_sequence_equal": True,
            "delimiter_role_sequence_equal": True,
        }
        for item in selected
    ]
    false_positive_evidence = {
        "block_id": FALSE_POSITIVE[0],
        "record_id": FALSE_POSITIVE[1],
        "literal_id": FALSE_POSITIVE[2],
        "status": "excluded",
        "reason": "dynamic_narrative_false_positive_return_to_castle",
        "paired_literal_id": 1,
        "dynamic_value_between_sc_literals": True,
        "standalone_ui_button": False,
        "sc_literal_count": len(fp_sc_hashes),
        "jp_literal_count": len(fp_jp_hashes),
        "en_literal_count": len(fp_en_hashes),
        "sc_literal_utf16le_sha256": fp_sc_hashes,
        "jp_literal_utf16le_sha256": fp_jp_hashes,
        "en_literal_utf16le_sha256": fp_en_hashes,
        "sc_record_skeleton_sha256": fp_sc_skeleton,
        "jp_record_skeleton_sha256": recovery.sha256(recovery.prior.record_skeleton(jp_records[fp_key])),
        "en_record_skeleton_sha256": fp_en_skeleton,
        "contains_commercial_source_text": False,
    }
    evidence = {
        "schema": "nobu16.kr.pk-msggame-ui-priority-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "source_free": True,
        "pinned_sources": {
            "pk_sc_packed_sha256": recovery.sha256(pk_sc["packed"]),
            "pk_jp_packed_sha256": recovery.sha256(pk_jp["packed"]),
            "pk_en_packed_sha256": recovery.sha256(pk_en["packed"]),
        },
        "selection": {
            "policy": "remaining_block13_record256plus_complete_single_sc_literal",
            "entry_count": len(selected),
            "coordinates_sha256": selected_hash,
            "category_counts": category_counts,
            "first_coordinate": list(selected_coordinates[0]),
            "last_coordinate": list(selected_coordinates[-1]),
        },
        "target_catalog": {
            "path": target_path.relative_to(REPO_ROOT).as_posix(),
            "coordinate_count": len(target["coordinates"]),
            "coordinates_sha256": target["hash"],
            "selected_is_subset": True,
        },
        "existing_overlay_exclusion": {
            "predecessor_coordinate_union": len(existing["predecessor_coordinates"]),
            "predecessor_inputs": existing["predecessor_inputs"],
            "normalized_input_sha256": existing["predecessor_normalized_sha256"],
            "predecessor_prefix_sha256": PREDECESSOR_PATHS_PIN,
            "self_path": SELF_RELATIVE,
            "self_registration_states_supported": [0, 1],
            "successor_overlays_tolerated": True,
        },
        "false_positive_audit": false_positive_evidence,
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.pk-msggame-ui-priority-review.v1",
        "batch_id": BATCH_ID,
        "quality_state": "agent_ui_translation_pending_runtime_review",
        "candidate_count": 151,
        "selected_count": len(selected),
        "excluded_count": 1,
        "category_counts": category_counts,
        "entries": [
            {
                "block_id": item["coordinate"][0],
                "record_id": item["coordinate"][1],
                "literal_id": item["coordinate"][2],
                "category": item["category"],
                "status": "translated",
                "semantic_review_completed": True,
                "human_review_required": True,
                "runtime_reviewed": False,
            }
            for item in selected
        ] + [
            {
                "block_id": FALSE_POSITIVE[0],
                "record_id": FALSE_POSITIVE[1],
                "literal_id": FALSE_POSITIVE[2],
                "category": "dynamic_narrative_false_positive",
                "status": "excluded",
                "reason": false_positive_evidence["reason"],
                "semantic_review_completed": True,
                "human_review_required": False,
                "runtime_reviewed": False,
            }
        ],
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts = {
        "overlay": write_json(overlay_path, overlay),
        "evidence": write_json(evidence_path, evidence),
        "review": write_json(review_path, review),
    }
    source_free_scan = assert_source_free((overlay_path, evidence_path, review_path))

    rebuilt, binary_manifest = recovery.apply_overlay_blob(pk_sc["packed"], overlay)
    parsed = recovery.parse_packed_msggame(rebuilt)
    rebuilt_literals = recovery.literal_map(parsed.archive)
    if set(rebuilt_literals) != set(sc_literals):
        raise BatchError("offline reconstruction changed literal coordinates")
    for item in selected:
        if rebuilt_literals[item["coordinate"]].text != item["replacement"]:
            raise BatchError(f"offline replacement mismatch at {item['coordinate']}")

    after = {str(path): recovery.sha256(path.read_bytes()) for path in input_paths}
    if before != after:
        raise BatchError("read-only input changed during build")
    validation = {
        "schema": "nobu16.kr.pk-msggame-ui-priority-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "review_scope": {"candidate_count": 151, "translated": len(selected), "excluded": 1},
        "category_counts": category_counts,
        "progress_effect": {
            "target_count": len(target["coordinates"]),
            "predecessor_translated_count": len(existing["predecessor_coordinates"]),
            "post_batch_translated_count": len(existing["predecessor_coordinates"]) + len(selected),
            "post_batch_remaining_count": len(target["coordinates"]) - len(existing["predecessor_coordinates"]) - len(selected),
        },
        "coordinate_sets": {
            "selected_sha256": selected_hash,
            "selected_existing_disjoint": True,
            "selected_predecessor_disjoint": True,
            "selected_target_subset": True,
            "false_positive_not_selected": True,
        },
        "proofs": {
            "all_selected_records_have_one_sc_literal": True,
            "all_replacements_preserve_pk_sc_invariants": True,
            "all_replacements_preserve_bracket_sequence": True,
            "all_replacements_preserve_delimiter_role_sequence": True,
            "dynamic_narrative_false_positive_excluded": True,
            "self_registration_states_supported": [0, 1],
            "successor_registration_does_not_change_selection": True,
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": recovery.sha256(rebuilt),
            "literal_coordinates_preserved": True,
            "installed_game_file_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": recovery.sha256(SCRIPT_PATH.read_bytes())},
        "safety": {
            "installed_game_files_modified": False,
            "executable_modified": False,
            "dll_injection": False,
            "process_memory_access": False,
            "registry_modified": False,
            "root_progress_modified": False,
            "root_readme_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_artifact = write_json(validation_path, validation)
    return {
        "entry_count": len(selected),
        "excluded_count": 1,
        "category_counts": category_counts,
        "selected_coordinates_sha256": selected_hash,
        "target_packed_sha256": recovery.sha256(rebuilt),
        "artifacts": {**artifacts, "validation": validation_artifact},
        "self_registration_count": existing["self_registration_count"],
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--pk-jp", type=Path, default=GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin")
    value.add_argument("--pk-sc", type=Path, default=recovery.DEFAULT_PK_SC)
    value.add_argument("--pk-en", type=Path, default=GAME_ROOT / "MSG_PK" / "EN" / "msggame.bin")
    value.add_argument("--progress", type=Path, default=recovery.DEFAULT_PROGRESS)
    value.add_argument("--target-catalog", type=Path, default=recovery.DEFAULT_TARGET_CATALOG)
    value.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return value


def main() -> int:
    result = build(parser().parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
