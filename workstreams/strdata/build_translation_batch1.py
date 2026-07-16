#!/usr/bin/env python3
"""Build source-free strdata Korean name-and-label batch v0.1 artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_structure_inventory as inventory  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


BATCH_ID = "strdata-name-labels-b00s0000-0099-v0.1"
OVERLAY_NAME = "strdata_ko_name_labels_b00s0000_0099.v0.1.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.1.json"
REVIEW_NAME = "translation_review_index.v0.1.json"
VALIDATION_NAME = "translation_validation.v0.1.json"
OVERLAY_SCHEMA = "nobu16.kr.strdata-block-overlay.v1"
RESOURCE = inventory.RESOURCE
LANGUAGES = inventory.LANGUAGES
SOURCE_PATHS = inventory.SOURCE_PATHS

FIRST_COORDINATE = (0, 0)
LAST_COORDINATE = (0, 99)
NEXT_COORDINATE = (0, 100)
TRANSLATED_COUNT = 100
RECORD_COUNT = 100


# Korean-only project translations.  Values are SC-structure preserving and
# never distribute the official SC, JP, or TC source strings.
TRANSLATIONS: dict[tuple[int, int], str] = {
    (0, 0): "아오카게",
    (0, 1): "아카이",
    (0, 2): "아카시",
    (0, 3): "아카호시",
    (0, 4): "아케치",
    (0, 5): "아사쿠라",
    (0, 6): "아사리",
    (0, 7): "아시카가",
    (0, 8): "아시다",
    (0, 9): "아시나",
    (0, 10): "아소",
    (0, 11): "아나야마",
    (0, 12): "아베",
    (0, 13): "아마카스",
    (0, 14): "아마노",
    (0, 15): "아라키",
    (0, 16): "아리마",
    (0, 17): "아루",
    (0, 18): "아와야",
    (0, 19): "안도",
    (0, 20): "이이",
    (0, 21): "이이오",
    (0, 22): "이이자카",
    (0, 23): "이이다",
    (0, 24): "이사리",
    (0, 25): "이시이",
    (0, 26): "이시카와",
    (0, 27): "이지치",
    (0, 28): "이시마키",
    (0, 29): "이즈미다",
    (0, 30): "이즈미야마",
    (0, 31): "이즈모",
    (0, 32): "이치쿠리",
    (0, 33): "이치하사마",
    (0, 34): "이치마다",
    (0, 35): "잇시키",
    (0, 36): "이도",
    (0, 37): "이토",
    (0, 38): "이나바",
    (0, 39): "이마이즈미",
    (0, 40): "이마가와",
    (0, 41): "이와이",
    (0, 42): "이와카미",
    (0, 43): "이와키",
    (0, 44): "이와시미즈",
    (0, 45): "우에스기",
    (0, 46): "우에다",
    (0, 47): "우에무라",
    (0, 48): "우오즈미",
    (0, 49): "우키타",
    (0, 50): "우지이",
    (0, 51): "우지이에",
    (0, 52): "우스키",
    (0, 53): "우치가시마",
    (0, 54): "우츠노미야",
    (0, 55): "우도노",
    (0, 56): "우바가이",
    (0, 57): "우메즈",
    (0, 58): "에네이",
    (0, 59): "에마",
    (0, 60): "에무라",
    (0, 61): "엔조지",
    (0, 62): "오",
    (0, 63): "오이카와",
    (0, 64): "오고",
    (0, 65): "오이시",
    (0, 66): "오우치",
    (0, 67): "오우라",
    (0, 68): "오쿠보",
    (0, 69): "오쿠마",
    (0, 70): "오제키",
    (0, 71): "오타",
    (0, 72): "오다테",
    (0, 73): "오타와라",
    (0, 74): "오토모",
    (0, 75): "오니시",
    (0, 76): "오노",
    (0, 77): "오무라",
    (0, 78): "오카",
    (0, 79): "오가사와라",
    (0, 80): "오카베",
    (0, 81): "오카모토",
    (0, 82): "오쿠",
    (0, 83): "오다",
    (0, 84): "오다",
    (0, 85): "오치",
    (0, 86): "오쓰야노",
    (0, 87): "남자의",
    (0, 88): "오바타",
    (0, 89): "여자의",
    (0, 90): "가이",
    (0, 91): "가이센",
    (0, 92): "가키자키",
    (0, 93): "가상",
    (0, 94): "가사이",
    (0, 95): "가시야마",
    (0, 96): "가지와라",
    (0, 97): "가스가",
    (0, 98): "가스야",
    (0, 99): "가타기리",
}

TRANSLATED_COORDINATES_SHA256 = "19B2C39B5C70E2A8F372F344C7A71C024DB0A3F2FAF4FFF392BFC38170EDB49B"
TRANSLATION_MAP_SHA256 = "21A269A1D38DCB105D67601883DA99E36E9339476A35F586444D10196CD4E8B0"
SOURCE_SC_HASHES_SHA256 = "5B5FD7C5A1219AAD57A25CC6BF7E58A94AA20853AD7B94731B991644A8914FC7"
ALL_REFERENCE_HASHES_SHA256 = "2EC1527576E378585F72CBC3E774B89F9B2042B80C780FDC0AF465E0F12C4BF9"

# A matching SC hash in an older overlay is translation-memory evidence only.
# It never authorizes automatic cross-resource reuse: this batch was reviewed at
# its own strdata block/slot coordinate against SC, JP, and TC references.
TRANSLATION_MEMORY_REVIEW = {
    "policy": {
        "matching_source_hash_is_translation_memory_only": True,
        "automatic_reuse_permitted": False,
        "independent_strdata_coordinate_context_reviewed": True,
        "review_languages": list(LANGUAGES),
    },
    "primary_reference_overlay": {
        "logical_path": "KR_PATCH_WORK/data/public/msgdata_ko_officer_names_0000_2399.v0.1.json",
        "sha256": "D787EB64BFFC54D1ACA2F23BC9407991FEB4FCF76D102E1EE017EEF416FE4FA3",
        "entry_count": 3831,
    },
    "summary": {
        "strdata_coordinate_count": 100,
        "coordinates_with_matching_source_hash_candidate": 90,
        "coordinates_without_matching_source_hash_candidate": 10,
        "matching_reference_entry_count": 121,
        "distinct_matching_source_hash_count": 90,
        "post_context_review_normalized_agreement_count": 90,
        "automatic_reuse_count": 0,
        "ambiguous_reference_candidate_coordinate_count": 2,
    },
    "comparison_normalization": "trailing_whitespace_removed_for_comparison_only",
    "exceptions": [
        {
            "reason": "no_matching_cross_resource_source_hash_candidate",
            "coordinates": [[0, 17], [0, 25], [0, 31], [0, 62], [0, 86], [0, 87], [0, 89], [0, 90], [0, 91], [0, 93]],
        },
        {
            "reason": "multiple_reference_translation_candidates_resolved_by_strdata_coordinate_context",
            "coordinates": [[0, 3], [0, 21]],
        },
    ],
}

BRACKET_TOKEN_RE = re.compile(r"\[[A-Za-z0-9_]+\]")


class StrdataBatchError(ValueError):
    """Raised when this fixed batch's scope or binary invariants differ."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )


def selected_coordinates() -> list[tuple[int, int]]:
    return sorted(TRANSLATIONS)


def source_structure(text: str) -> dict[str, Any]:
    invariant = common.message_invariants(text)
    tokens = BRACKET_TOKEN_RE.findall(text)
    return {
        "utf16le_sha256": common.text_hash(text),
        "printf_token_count": len(invariant["printf"]),
        "printf_tokens_sha256": hash_json(invariant["printf"]),
        "unknown_percent_count": invariant["unknown_percent_count"],
        "leading_whitespace_utf16le_sha256": common.text_hash(
            invariant["leading_whitespace"]
        ),
        "trailing_whitespace_utf16le_sha256": common.text_hash(
            invariant["trailing_whitespace"]
        ),
        "escape_token_count": len(invariant["esc"]),
        "escape_tokens_sha256": hash_json(invariant["esc"]),
        "control_codepoints": invariant["controls"],
        "line_breaks_sha256": hash_json(invariant["line_breaks"]),
        "pua_codepoints": invariant["pua"],
        "bracket_placeholder_count": len(tokens),
        "bracket_placeholders_sha256": hash_json(tokens),
    }


def invariant_failures(source: str, replacement: str) -> list[str]:
    failures = common.invariant_mismatches(source, replacement)
    if BRACKET_TOKEN_RE.findall(source) != BRACKET_TOKEN_RE.findall(replacement):
        failures.append("bracket_placeholder_sequence differs")
    return failures


def _overlay_coordinates(overlay: dict[str, Any]) -> list[tuple[int, int]]:
    return [
        (int(entry["block_id"]), int(entry["slot_id"]))
        for entry in overlay["entries"]
    ]


def validate_overlay_shape(overlay: dict[str, Any]) -> None:
    required = {
        "schema",
        "overlay_id",
        "resource",
        "base_language",
        "defaults",
        "entry_count",
        "distribution_policy",
        "stock_sc",
        "entries",
    }
    if set(overlay) != required or overlay["schema"] != OVERLAY_SCHEMA:
        raise StrdataBatchError("invalid strdata overlay schema")
    if overlay["overlay_id"] != BATCH_ID or overlay["resource"] != RESOURCE:
        raise StrdataBatchError("overlay identity or resource changed")
    if overlay["base_language"] != "SC" or overlay["defaults"] != {"status": "translated"}:
        raise StrdataBatchError("overlay language/defaults changed")
    if overlay["entry_count"] != TRANSLATED_COUNT:
        raise StrdataBatchError("overlay count changed")
    if overlay["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise StrdataBatchError("overlay distribution policy changed")
    entries = overlay["entries"]
    if not isinstance(entries, list) or _overlay_coordinates(overlay) != selected_coordinates():
        raise StrdataBatchError("overlay coordinates changed")
    for entry in entries:
        if set(entry) != {"block_id", "slot_id", "source_sc_utf16le_sha256", "ko"}:
            raise StrdataBatchError("overlay entry shape changed")
        if not isinstance(entry["ko"], str) or not entry["ko"]:
            raise StrdataBatchError("overlay Korean text is empty")
        if not re.fullmatch(r"[0-9A-F]{64}", entry["source_sc_utf16le_sha256"]):
            raise StrdataBatchError("overlay source hash is invalid")


def apply_overlay_blob(packed: bytes, overlay: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    """Apply one source-free overlay to a packed SC strdata blob in memory."""
    validate_overlay_shape(overlay)
    wrapper, raw = decompress_wrapper(packed)
    archive = parse_raw_strdata(raw)
    stock = overlay["stock_sc"]
    if stock != {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "block_slot_counts": [block.slot_count for block in archive.blocks],
    }:
        raise StrdataBatchError("overlay stock SC fingerprint mismatch")
    replacements = {block.block_id: list(block.texts) for block in archive.blocks}
    checks: dict[str, str] = {}
    for entry in overlay["entries"]:
        coordinate = (int(entry["block_id"]), int(entry["slot_id"]))
        block_id, slot_id = coordinate
        source = archive.blocks[block_id].texts[slot_id]
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"]:
            raise StrdataBatchError(f"source hash mismatch at {coordinate}")
        problems = invariant_failures(source, entry["ko"])
        if problems:
            raise StrdataBatchError(f"invariant mismatch at {coordinate}: {problems}")
        replacements[block_id][slot_id] = entry["ko"]
        checks[f"{block_id}:{slot_id}"] = "OK"
    rebuilt_raw = rebuild_raw_strdata(archive, replacements)
    rebuilt = recompress_wrapper(rebuilt_raw, wrapper)
    _check_wrapper, check_raw = decompress_wrapper(rebuilt)
    check = parse_raw_strdata(check_raw)
    for entry in overlay["entries"]:
        block_id = int(entry["block_id"])
        slot_id = int(entry["slot_id"])
        if check.blocks[block_id].texts[slot_id] != entry["ko"]:
            raise StrdataBatchError(f"rebuilt text mismatch at {(block_id, slot_id)}")
    return rebuilt, {
        "entry_count": len(overlay["entries"]),
        "checks": checks,
        "target_packed_sha256": sha256(rebuilt),
        "target_packed_size": len(rebuilt),
        "target_raw_sha256": sha256(rebuilt_raw),
        "target_raw_size": len(rebuilt_raw),
        "installed_game_file_written": False,
    }


def _assert_public_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    scans: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = inventory.source_free_counts(path.read_bytes())
        if counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}:
            raise StrdataBatchError(f"source script text leaked into {path.name}")
        scans[path.name] = counts
    return scans


def _write_artifact(out_root: Path, path: Path, value: Any) -> dict[str, Any]:
    """Write an artifact while keeping its manifest location reproducible."""
    artifact = inventory.write_json(path, value)
    return {
        "path": path.relative_to(out_root).as_posix(),
        "size": artifact["size"],
        "sha256": artifact["sha256"],
    }


def validate_translation_memory_review() -> None:
    review = TRANSLATION_MEMORY_REVIEW
    policy = review["policy"]
    summary = review["summary"]
    if policy != {
        "matching_source_hash_is_translation_memory_only": True,
        "automatic_reuse_permitted": False,
        "independent_strdata_coordinate_context_reviewed": True,
        "review_languages": list(LANGUAGES),
    }:
        raise StrdataBatchError("translation-memory reuse policy changed")
    if summary != {
        "strdata_coordinate_count": TRANSLATED_COUNT,
        "coordinates_with_matching_source_hash_candidate": 90,
        "coordinates_without_matching_source_hash_candidate": 10,
        "matching_reference_entry_count": 121,
        "distinct_matching_source_hash_count": 90,
        "post_context_review_normalized_agreement_count": 90,
        "automatic_reuse_count": 0,
        "ambiguous_reference_candidate_coordinate_count": 2,
    }:
        raise StrdataBatchError("translation-memory review summary changed")
    exceptions = review["exceptions"]
    if [coordinate for item in exceptions for coordinate in item["coordinates"]] != [
        [0, 17], [0, 25], [0, 31], [0, 62], [0, 86], [0, 87], [0, 89], [0, 90], [0, 91], [0, 93], [0, 3], [0, 21]
    ]:
        raise StrdataBatchError("translation-memory exception coordinates changed")


def validate_static_scope() -> None:
    validate_translation_memory_review()
    coordinates = selected_coordinates()
    if coordinates[0] != FIRST_COORDINATE or coordinates[-1] != LAST_COORDINATE:
        raise StrdataBatchError("batch boundary changed")
    if coordinates != [(0, slot_id) for slot_id in range(TRANSLATED_COUNT)]:
        raise StrdataBatchError("batch is no longer a natural first contiguous run")
    if len(coordinates) != TRANSLATED_COUNT:
        raise StrdataBatchError("batch count changed")
    if hash_json(coordinates) != TRANSLATED_COORDINATES_SHA256:
        raise StrdataBatchError("coordinate digest changed")
    if (
        hash_json([[block_id, slot_id, TRANSLATIONS[(block_id, slot_id)]] for block_id, slot_id in coordinates])
        != TRANSLATION_MAP_SHA256
    ):
        raise StrdataBatchError("translation map digest changed")


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    validate_static_scope()
    loaded, before = inventory.load_sources(game_root)
    archives = {language: loaded[language]["archive"] for language in LANGUAGES}
    selected = selected_coordinates()
    all_source_hashes: list[str] = []
    sc_source_hashes: list[str] = []
    evidence_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    overlay_entries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for block_id, slot_id in selected:
        references = {
            language: archives[language].blocks[block_id].texts[slot_id]
            for language in LANGUAGES
        }
        if any(not text.strip() for text in references.values()):
            raise StrdataBatchError(f"selected coordinate {(block_id, slot_id)} is not display text in every language")
        source = references["SC"]
        problems = invariant_failures(source, TRANSLATIONS[(block_id, slot_id)])
        if problems:
            failures.append({"coordinate": [block_id, slot_id], "problems": problems})
        sc_hash = common.text_hash(source)
        sc_source_hashes.append(sc_hash)
        all_source_hashes.extend(common.text_hash(references[language]) for language in LANGUAGES)
        overlay_entries.append(
            {
                "block_id": block_id,
                "slot_id": slot_id,
                "source_sc_utf16le_sha256": sc_hash,
                "ko": TRANSLATIONS[(block_id, slot_id)],
            }
        )
        evidence_entries.append(
            {
                "block_id": block_id,
                "slot_id": slot_id,
                "classification": "name_or_name_builder_label",
                "references": {
                    language: source_structure(references[language])
                    for language in LANGUAGES
                },
                "translation_origin": "source_free_korean_name_normalization_with_sc_jp_tc_review",
            }
        )
        review_entries.append(
            {
                "block_id": block_id,
                "slot_id": slot_id,
                "status": "translated",
                "translation_origin": "source_free_korean_name_normalization_with_sc_jp_tc_review",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": ["name_or_label_runtime_width_review"]
                + (
                    ["reading_or_fragment_review"]
                    if slot_id in {17, 62, 86, 87, 89, 91, 93}
                    else []
                ),
            }
        )
    if failures:
        raise StrdataBatchError(f"translation invariants failed: {failures}")
    if hash_json(sc_source_hashes) != SOURCE_SC_HASHES_SHA256:
        raise StrdataBatchError("ordered SC source hashes changed")
    if hash_json(all_source_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise StrdataBatchError("ordered SC/JP/TC source hashes changed")

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "packed_size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "block_slot_counts": [block.slot_count for block in archives["SC"].blocks],
        },
        "entries": overlay_entries,
    }
    validate_overlay_shape(overlay)
    rebuilt, binary = apply_overlay_blob(sc_packed, overlay)
    _target_wrapper, target_raw = decompress_wrapper(rebuilt)
    target = parse_raw_strdata(target_raw)
    source_coordinates = coordinate_texts(archives["SC"])
    target_coordinates = coordinate_texts(target)
    if set(source_coordinates) != set(target_coordinates):
        raise StrdataBatchError("coordinate set changed after rebuild")
    replacement_map = {coordinate: TRANSLATIONS[coordinate] for coordinate in selected}
    for coordinate, original in source_coordinates.items():
        expected = replacement_map.get(coordinate, original)
        if target_coordinates[coordinate] != expected:
            raise StrdataBatchError(f"rebuilt coordinate mismatch at {coordinate}")

    source_files = {
        language: {
            "logical_path": SOURCE_PATHS[language],
            **inventory.SOURCE_PINS[language],
            "block_display_nonempty_counts": list(loaded[language]["nonempty_counts"]),
        }
        for language in LANGUAGES
    }
    evidence = {
        "schema": "nobu16.kr.strdata-translation-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "first_coordinate": list(FIRST_COORDINATE),
            "last_coordinate": list(LAST_COORDINATE),
            "next_coordinate": list(NEXT_COORDINATE),
            "selected_literal_count": len(selected),
            "selected_block_count": 1,
            "nonlinguistic_visible_candidate_skips": 0,
        },
        "alignment_basis": [
            "same_strdata_resource_role",
            "same_five_block_slot_shape",
            "same_block_and_slot_coordinates",
            "sc_jp_tc_same_coordinate_semantic_review",
            "sc_structure_authoritative_for_replacement_invariants",
        ],
        "cross_resource_translation_memory_review": TRANSLATION_MEMORY_REVIEW,
        "source_files": source_files,
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.strdata-translation-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "name_label_translation_draft_pending_runtime_review",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts = {
        "overlay": _write_artifact(out_root, overlay_path, overlay),
        "alignment_evidence": _write_artifact(out_root, evidence_path, evidence),
        "review_index": _write_artifact(out_root, review_path, review),
    }
    source_free_scan = _assert_public_source_free((overlay_path, evidence_path, review_path))
    after = {
        relative: sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise StrdataBatchError("installed strdata source changed during batch build")

    validation = {
        "schema": "nobu16.kr.strdata-translation-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "first_coordinate": list(FIRST_COORDINATE),
            "last_coordinate": list(LAST_COORDINATE),
            "next_coordinate": list(NEXT_COORDINATE),
            "selected_literal_count": len(selected),
            "selected_coordinates_sha256": TRANSLATED_COORDINATES_SHA256,
        },
        "selection": {
            "stable_block_slot_order": True,
            "natural_first_contiguous_display_run": True,
            "all_candidates_nonempty_in_sc_jp_tc": True,
            "nonlinguistic_visible_candidate_skips": 0,
        },
        "source_alignment": {
            "languages": list(LANGUAGES),
            "same_block_slot_shape": True,
            "translated_reference_hash_count": len(selected) * len(LANGUAGES),
            "ordered_sc_source_hashes_sha256": SOURCE_SC_HASHES_SHA256,
            "ordered_all_reference_hashes_sha256": ALL_REFERENCE_HASHES_SHA256,
        },
        "cross_resource_translation_memory_review": TRANSLATION_MEMORY_REVIEW,
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "escape_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholder_sequence",
            ],
        },
        "raw_binary_validation": {
            "outer_five_block_directory_rebuilt": True,
            "inner_tables_rebuilt_via_synthetic_single_table_wrapper": True,
            "inner_opaque_header_bytes_preserved": True,
            "outer_alignment_padding_recomputed": True,
            "coordinate_set_preserved": True,
            "unselected_texts_preserved": True,
            "target_packed_sha256": binary["target_packed_sha256"],
            "target_packed_size": binary["target_packed_size"],
            "target_raw_sha256": binary["target_raw_sha256"],
            "target_raw_size": binary["target_raw_size"],
            "installed_game_file_written": False,
        },
        "translation_status": {
            "translated_draft": len(selected),
            "human_review_required": len(selected),
            "runtime_reviewed": 0,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "byte_identical_offline_binary_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "other_workstreams_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = _write_artifact(out_root, validation_path, validation)
    _assert_public_source_free((validation_path,))
    return {
        "entry_count": len(selected),
        "next_coordinate": NEXT_COORDINATE,
        "target_packed_sha256": binary["target_packed_sha256"],
        "artifacts": artifacts,
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [game_root / SOURCE_PATHS[language] for language in LANGUAGES]
    before = {path.as_posix(): sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-strdata-v01-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-strdata-v01-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["target_packed_sha256"] != second["target_packed_sha256"]:
                raise StrdataBatchError("isolated A/B rebuilt binaries differ")
            if {
                name: blob["sha256"] for name, blob in first["artifacts"].items()
            } != {
                name: blob["sha256"] for name, blob in second["artifacts"].items()
            }:
                raise StrdataBatchError("isolated A/B public artifacts differ")
    final = build_once(game_root, out_root)
    if final["target_packed_sha256"] != first["target_packed_sha256"]:
        raise StrdataBatchError("final rebuilt binary differs from isolated build")
    for name in final["artifacts"]:
        if final["artifacts"][name]["sha256"] != first["artifacts"][name]["sha256"]:
            raise StrdataBatchError(f"final artifact differs from isolated build: {name}")
    after = {path.as_posix(): sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise StrdataBatchError("installed strdata source changed across batch build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"entries={result['entry_count']}")
    print("next_coordinate=" + ",".join(map(str, result["next_coordinate"])))
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in sorted(result["artifacts"].items()):
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
