#!/usr/bin/env python3
"""Build source-free PK msggame UI-priority batch B02."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path[:0] = [str(MSGGAME_ROOT), str(TOOLS_ROOT), str(WORKSTREAM_ROOT)]

import build_common_message_overlay as common  # noqa: E402
from build_literal_overlay import OVERLAY_SCHEMA, apply_overlay_blob, text_hash  # noqa: E402
from msggame_format import iter_literals, parse_packed_msggame, parse_record_literals, sha256  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


_TRANSLATIONS_SPEC = importlib.util.spec_from_file_location(
    "msggame_pk_ui_priority_b02_translations",
    WORKSTREAM_ROOT / "ui_translations.py",
)
if _TRANSLATIONS_SPEC is None or _TRANSLATIONS_SPEC.loader is None:
    raise RuntimeError("cannot load B02 UI translations")
_TRANSLATIONS_MODULE = importlib.util.module_from_spec(_TRANSLATIONS_SPEC)
_TRANSLATIONS_SPEC.loader.exec_module(_TRANSLATIONS_MODULE)
EXCLUSIONS = _TRANSLATIONS_MODULE.EXCLUSIONS
TRANSLATIONS = _TRANSLATIONS_MODULE.TRANSLATIONS


BATCH_ID = "msggame_pk_ui_priority_b02_53.v1"
RESOURCE = "MSG_PK/SC/msggame.bin"
OVERLAY_NAME = "msggame_ko_pk_ui_priority_b02_53.v1.json"
EVIDENCE_NAME = "msggame_pk_ui_priority_b02_evidence.v1.json"
REVIEW_NAME = "msggame_pk_ui_priority_b02_review.v1.json"
VALIDATION_NAME = "msggame_pk_ui_priority_b02_validation.v1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()
DEFAULT_PK_SC = (
    GAME_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "pk-full-messages-seoulhangang-v1"
    / "originals"
    / "MSG_PK"
    / "SC"
    / "msggame.bin"
)
DEFAULT_PK_JP = GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin"
DEFAULT_PK_EN = GAME_ROOT / "MSG_PK" / "EN" / "msggame.bin"
DEFAULT_PROGRESS = REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json"
DEFAULT_TARGET = REPO_ROOT / "data" / "public" / "translation_target_keys.v0.1.json"
B01_ROOT = REPO_ROOT / "workstreams" / "msggame_pk_ui_priority_b01"

SOURCE_PINS = {
    "SC": {
        "packed_size": 529_419,
        "packed_sha256": "BD7B33FCC7495B855B0828C7FE4E5F7ADB2DE656A9B12E20259750F94EE665D6",
        "raw_size": 1_077_200,
        "raw_sha256": "1958B2B801D37186D478284EA0E29CA96D8DA2BC087D6BEB74A4139EF01C11CE",
        "literal_count": 25_598,
    },
    "JP": {
        "packed_size": 709_290,
        "packed_sha256": "0FB9EA3B4817D208C65F587AF1F57A5BB82106367314801A13C9A534ECC47CD8",
        "raw_size": 1_571_384,
        "raw_sha256": "F00C897353C3C0084BFBFC5ED781C467945C82708F28A6D57BA0CC2710976D57",
        "literal_count": 29_149,
    },
    "EN": {
        "packed_size": 714_037,
        "packed_sha256": "14D9A20ECB35F35C91D14947921CF09F5EAF960F8FA4D70F703F2366DB1D13AF",
        "raw_size": 2_169_852,
        "raw_sha256": "03A1D07A4FFB460F393A47A047EFF596BBCE6BAADAE22EB00B3686E8AF96D39E",
        "literal_count": 25_169,
    },
}

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
BRACKETS = frozenset("[]{}<>［］｛｝〈〉《》「」『』【】〔〕")


class BatchError(ValueError):
    """Raised when a pinned input or UI translation contract changes."""


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
    relative = path.relative_to(path.parents[1]).as_posix() if path.parent.name in {"public", "evidence", "review"} else path.name
    return {"path": relative, "size": len(blob), "sha256": sha256(blob)}


def canonical_hash(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def literal_map(archive: Any) -> dict[tuple[int, int, int], Any]:
    return {(item.block_id, item.record_id, item.literal_id): item for item in iter_literals(archive)}


def script_counts(text: str) -> dict[str, int]:
    return {"cjk_unified_count": len(CJK_RE.findall(text)), "kana_count": len(KANA_RE.findall(text))}


def assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = script_counts(path.read_text(encoding="utf-8"))
        result[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise BatchError(f"commercial source script leaked into artifact: {path}")
    return result


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(char) in {"W", "F", "A"} else 1 for char in text)


def line_widths(text: str) -> list[int]:
    return [display_width(line) for line in re.split(r"\r\n|\n|\r", text)]


def bracket_sequence(text: str) -> list[str]:
    return [char for char in text if char in BRACKETS]


def load_source(path: Path, label: str) -> dict[str, Any]:
    packed = path.read_bytes()
    pin = SOURCE_PINS[label]
    if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
        raise BatchError(f"{label} packed source pin changed")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise BatchError(f"{label} raw source pin changed")
    parsed = parse_packed_msggame(packed)
    literals = literal_map(parsed.archive)
    if len(literals) != pin["literal_count"]:
        raise BatchError(f"{label} literal count changed")
    return {"path": path, "packed": packed, "raw": raw, "archive": parsed.archive, "literals": literals}


def target_coordinates(path: Path) -> tuple[set[tuple[int, int, int]], str]:
    payload = read_json(path)
    resources = payload.get("resources")
    matches = [item for item in resources if item.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise BatchError("target catalog must contain exactly one PK msggame resource")
    item = matches[0]
    coordinates = {tuple(value) for value in item.get("target_coordinates", [])}
    if len(coordinates) != 16_482 or any(len(value) != 3 for value in coordinates):
        raise BatchError("PK msggame target coordinate catalog changed")
    if canonical_hash([list(value) for value in sorted(coordinates)]) != item.get("target_keys_sha256"):
        raise BatchError("PK msggame target coordinate hash changed")
    return coordinates, item["target_keys_sha256"]


def overlay_coordinates(path: Path) -> set[tuple[int, int, int]]:
    payload = read_json(path)
    if payload.get("resource") != RESOURCE or not isinstance(payload.get("entries"), list):
        return set()
    result: set[tuple[int, int, int]] = set()
    for entry in payload["entries"]:
        coordinate = (entry.get("block_id"), entry.get("record_id"), entry.get("literal_id"))
        if not all(type(value) is int for value in coordinate):
            raise BatchError(f"invalid coordinate in {path}")
        result.add(coordinate)
    return result


def existing_coordinates(progress_path: Path) -> tuple[set[tuple[int, int, int]], set[tuple[int, int, int]]]:
    progress = read_json(progress_path)
    resources = progress.get("resources")
    matches = [item for item in resources if item.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise BatchError("progress must contain exactly one PK msggame resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list):
        raise BatchError("PK msggame overlay_globs is invalid")
    registered: set[tuple[int, int, int]] = set()
    for pattern in patterns:
        if pattern == SELF_RELATIVE:
            continue
        paths = sorted(REPO_ROOT.glob(pattern))
        if len(paths) != 1:
            raise BatchError(f"progress pattern {pattern!r} resolved to {len(paths)} files")
        registered.update(overlay_coordinates(paths[0]))
    b01: set[tuple[int, int, int]] = set()
    for path in sorted((B01_ROOT / "public").glob("*.json")) if (B01_ROOT / "public").exists() else []:
        b01.update(overlay_coordinates(path))
    translations_module = B01_ROOT / "ui_translations.py"
    if translations_module.exists():
        namespace: dict[str, Any] = {}
        exec(compile(translations_module.read_text(encoding="utf-8"), str(translations_module), "exec"), namespace)
        values = namespace.get("TRANSLATIONS", {})
        if isinstance(values, dict):
            b01.update(values)
    return registered, b01


def build(args: argparse.Namespace) -> dict[str, Any]:
    if len(TRANSLATIONS) != 53:
        raise BatchError(f"translation count changed: {len(TRANSLATIONS)}")
    if set(TRANSLATIONS) & set(EXCLUSIONS):
        raise BatchError("translated and excluded coordinates overlap")
    if any(coordinate[0] in {13, 14} for coordinate in TRANSLATIONS):
        raise BatchError("B02 translation entered reserved blocks 13 or 14")
    mandatory = (7, 2076, 0)
    if EXCLUSIONS.get(mandatory) != "dynamic_narrative_false_positive":
        raise BatchError("mandatory dynamic narrative false positive is missing")

    source_paths = {"SC": args.pk_sc.resolve(), "JP": args.pk_jp.resolve(), "EN": args.pk_en.resolve()}
    before = {label: sha256(path.read_bytes()) for label, path in source_paths.items()}
    sources = {label: load_source(path, label) for label, path in source_paths.items()}
    targets, target_hash = target_coordinates(args.target_catalog.resolve())
    registered, b01 = existing_coordinates(args.progress.resolve())
    selected_set = set(TRANSLATIONS)
    if not selected_set <= targets:
        raise BatchError("translation escaped the exact target catalog")
    if selected_set & registered:
        raise BatchError(f"translation overlaps registered overlays: {sorted(selected_set & registered)[:5]}")
    if selected_set & b01:
        raise BatchError(f"translation overlaps B01: {sorted(selected_set & b01)[:5]}")
    if not set(EXCLUSIONS) <= targets:
        raise BatchError("exclusion escaped the exact target catalog")

    selected: list[dict[str, Any]] = []
    for coordinate in sorted(TRANSLATIONS):
        replacement = TRANSLATIONS[coordinate]
        source = sources["SC"]["literals"][coordinate].text
        record_counts: dict[str, int] = {}
        official_widths: dict[str, list[int]] = {}
        official_hashes: dict[str, str] = {}
        for label in ("SC", "JP", "EN"):
            block_id, record_id, _literal_id = coordinate
            record = sources[label]["archive"].blocks[block_id].records[record_id]
            record_counts[label] = len(parse_record_literals(record))
            literal = sources[label]["literals"].get(coordinate)
            if literal is None:
                raise BatchError(f"{label} lacks aligned coordinate {coordinate}")
            official_widths[label] = line_widths(literal.text)
            official_hashes[label] = text_hash(literal.text)
        if record_counts["SC"] != 1 or record_counts["JP"] < 1 or record_counts["EN"] < 1:
            raise BatchError(f"selected coordinate is not a complete single-SC-literal record: {coordinate}")
        mismatches = common.invariant_mismatches(source, replacement)
        if mismatches:
            raise BatchError(f"placeholder/control/newline mismatch at {coordinate}: {mismatches}")
        if bracket_sequence(source) != bracket_sequence(replacement):
            raise BatchError(f"bracket sequence changed at {coordinate}")
        counts = script_counts(replacement)
        if counts != {"cjk_unified_count": 0, "kana_count": 0} or HANGUL_RE.search(replacement) is None:
            raise BatchError(f"replacement script policy failed at {coordinate}")
        replacement_widths = line_widths(replacement)
        width_limit = max(max(widths) for widths in official_widths.values()) + 4
        if max(replacement_widths) > width_limit:
            raise BatchError(
                f"replacement display width exceeds multilingual budget at {coordinate}: "
                f"{max(replacement_widths)} > {width_limit}"
            )
        selected.append(
            {
                "coordinate": coordinate,
                "replacement": replacement,
                "official_hashes": official_hashes,
                "replacement_hash": text_hash(replacement),
                "record_literal_counts": record_counts,
                "official_line_widths": official_widths,
                "replacement_line_widths": replacement_widths,
                "display_width_limit": width_limit,
                "invariants": common.message_invariants(source),
            }
        )

    stock = sources["SC"]
    overlay_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "source_sc_utf16le_sha256": item["official_hashes"]["SC"],
            "ko": item["replacement"],
        }
        for item in selected
    ]
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "selection_policy": {
            "priority": "complete_ui_components_outside_blocks_13_14",
            "dynamic_fragments_excluded": True,
            "event_dialogue_excluded": True,
            "source_text_embedded": False,
        },
        "stock_sc": {
            "packed_size": len(stock["packed"]),
            "packed_sha256": sha256(stock["packed"]),
            "raw_size": len(stock["raw"]),
            "raw_sha256": sha256(stock["raw"]),
            "record_count": stock["archive"].record_count,
            "literal_slot_count": len(stock["literals"]),
        },
        "entries": overlay_entries,
    }
    evidence_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "review_method": "agent_complete_ui_record_semantic_review",
            "pk_sc_utf16le_sha256": item["official_hashes"]["SC"],
            "pk_jp_utf16le_sha256": item["official_hashes"]["JP"],
            "pk_en_utf16le_sha256": item["official_hashes"]["EN"],
            "replacement_utf16le_sha256": item["replacement_hash"],
            "record_literal_counts": item["record_literal_counts"],
            "official_line_display_widths": item["official_line_widths"],
            "replacement_line_display_widths": item["replacement_line_widths"],
            "display_width_limit": item["display_width_limit"],
            "placeholder_control_newline_invariants_exact": True,
            "bracket_sequence_equal": True,
            "display_width_within_multilingual_budget": True,
            "complete_independent_ui_literal": True,
        }
        for item in selected
    ]
    evidence = {
        "schema": "nobu16.kr.msggame-pk-ui-priority-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "source_free": True,
        "scope": {
            "excluded_blocks": [13, 14],
            "selected_count": len(selected),
            "review_exclusion_count": len(EXCLUSIONS),
            "selection": "menu_button_confirmation_settings_help_system_tooltip_and_objective_ui",
        },
        "target_catalog": {
            "path": args.target_catalog.resolve().relative_to(REPO_ROOT).as_posix(),
            "coordinate_count": len(targets),
            "coordinates_sha256": target_hash,
            "selected_is_subset": True,
        },
        "overlap_checks": {
            "registered_overlay_overlap_count": 0,
            "ui_priority_b01_overlap_count": 0,
            "blocks_13_14_overlap_count": 0,
        },
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msggame-pk-ui-priority-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "agent_ui_priority_complete_literals_translated_dynamic_and_dialogue_excluded",
        "selected_count": len(selected),
        "excluded_count": len(EXCLUSIONS),
        "entries": [
            {
                "block_id": item["coordinate"][0],
                "record_id": item["coordinate"][1],
                "literal_id": item["coordinate"][2],
                "status": "translated",
                "review_method": "agent_complete_ui_record_semantic_review",
                "runtime_reviewed": False,
            }
            for item in selected
        ]
        + [
            {
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "literal_id": coordinate[2],
                "status": "excluded",
                "reason": reason,
                "runtime_reviewed": False,
            }
            for coordinate, reason in sorted(EXCLUSIONS.items())
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
    rebuilt, manifest = apply_overlay_blob(stock["packed"], overlay)
    rebuilt_literals = literal_map(parse_packed_msggame(rebuilt).archive)
    if set(rebuilt_literals) != set(stock["literals"]):
        raise BatchError("offline reconstruction changed literal coordinates")
    for item in selected:
        if rebuilt_literals[item["coordinate"]].text != item["replacement"]:
            raise BatchError(f"offline reconstruction mismatch at {item['coordinate']}")
    after = {label: sha256(path.read_bytes()) for label, path in source_paths.items()}
    if before != after:
        raise BatchError("read-only source changed during build")

    validation = {
        "schema": "nobu16.kr.msggame-pk-ui-priority-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "counts": {"translated": len(selected), "excluded_review_items": len(EXCLUSIONS)},
        "coordinate_sets": {
            "selected_sha256": canonical_hash([list(value) for value in sorted(selected_set)]),
            "excluded_sha256": canonical_hash([list(value) for value in sorted(EXCLUSIONS)]),
            "selected_excluded_disjoint": True,
            "selected_target_subset": True,
            "selected_registered_disjoint": True,
            "selected_b01_disjoint": True,
            "selected_blocks_13_14_disjoint": True,
        },
        "proofs": {
            "complete_single_sc_literal_with_full_jp_en_record_context": True,
            "placeholder_control_code_newline_preserved": True,
            "display_width_budget_preserved": True,
            "bracket_sequence_preserved": True,
            "all_replacements_have_hangul": True,
            "dynamic_fragments_excluded": True,
            "event_dialogue_excluded": True,
            "mandatory_dynamic_narrative_false_positive_excluded": True,
        },
        "offline_binary_validation": {
            "entry_count": manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": sha256(rebuilt),
            "literal_coordinates_preserved": True,
            "installed_game_file_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
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
    assert_source_free((validation_path,))
    return {
        "entry_count": len(selected),
        "excluded_count": len(EXCLUSIONS),
        "target_packed_sha256": sha256(rebuilt),
        "artifacts": {**artifacts, "validation": validation_artifact},
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--pk-sc", type=Path, default=DEFAULT_PK_SC)
    value.add_argument("--pk-jp", type=Path, default=DEFAULT_PK_JP)
    value.add_argument("--pk-en", type=Path, default=DEFAULT_PK_EN)
    value.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    value.add_argument("--target-catalog", type=Path, default=DEFAULT_TARGET)
    value.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return value


def main() -> int:
    result = build(parser().parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
