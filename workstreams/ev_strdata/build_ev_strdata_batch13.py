#!/usr/bin/env python3
"""Build source-free ev_strdata event-label batch v0.13 artifacts."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402


BATCH_ID = "ev-strdata-event-labels-2207-2406-v0.13"
OVERLAY_NAME = "ev_strdata_ko_event_labels_2207_2406.v0.13.json"
EVIDENCE_NAME = "alignment_evidence.v0.13.json"
REVIEW_NAME = "review_index.v0.13.json"
VALIDATION_NAME = "validation.v0.13.json"

INSPECT_START = 2207
INSPECT_END = 2406
DEFERRED_START = 2207
DEFERRED_END = 2399
TRANSLATED_START = 2400
TRANSLATED_END = 2406
NEXT_START_ID = 2407
INSPECTED_COUNT = INSPECT_END - INSPECT_START + 1
DEFERRED_COUNT = DEFERRED_END - DEFERRED_START + 1
TRANSLATED_COUNT = TRANSLATED_END - TRANSLATED_START + 1

ANALYSIS_START = 2207
ANALYSIS_END = 3200
ANALYSIS_COUNT = ANALYSIS_END - ANALYSIS_START + 1

TRANSLATIONS: dict[int, dict[str, str]] = {
    2400: {
        "ko": "모베쓰중 두령",
        "source_sc_utf16le_sha256": "B7E71D9D2ED8654335EF733CE40A0DB7C05AB5F1E830C2726A10645AF32AB0AA",
    },
    2401: {
        "ko": "아카이시중 두령",
        "source_sc_utf16le_sha256": "4957A5AD8EE900CBE4F7DCC1ECB4724FCEEC9FE178A3A53D35E6185BDF3F317B",
    },
    2402: {
        "ko": "도와다중 두령",
        "source_sc_utf16le_sha256": "C89B202FDEDE0C954C1BB3740D40F8D83B315FBCAA6512C7CE2770EAADE88BDC",
    },
    2403: {
        "ko": "시치노헤중 두령",
        "source_sc_utf16le_sha256": "B4E07BD3611826AE6C61D964EE36EA3DA0A567FBF2331BBF68302A9155CA68EB",
    },
    2404: {
        "ko": "다야마중 두령",
        "source_sc_utf16le_sha256": "F79C82BFF133561CBF6E4C66AC9110A62C6AE14C44E20DAAAD57FB72548CBCFA",
    },
    2405: {
        "ko": "구지중 두령",
        "source_sc_utf16le_sha256": "87AA1DF2BE9C564C0691037E2F290E0B7078D8EC28D36050E492FFA24D6E4044",
    },
    2406: {
        "ko": "히에누키중 두령",
        "source_sc_utf16le_sha256": "977AC38F267A187564AB01988B2AD21E6FEDF563C988116D6E47087F17456BC8",
    },
}

DEFERRED_REFERENCE_HASHES = {
    "SC": "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
    "JP": "143A3833C55A7B51DBBEB8B0E0475770C90A4756005D69FCBB117DDBF4611BFC",
    "TC": "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
}

# This reviewed profile contains only classifications and numeric ranges.  The
# pinned commercial strings used to derive it are never copied into the repo.
ANALYSIS_RUNS = (
    (2207, 2399, "code_placeholder"),
    (2400, 2448, "regional_group_leader_label"),
    (2449, 2449, "other_display_candidate"),
    (2450, 2543, "regional_group_leader_label"),
    (2544, 2544, "other_display_candidate"),
    (2545, 2547, "regional_group_leader_label"),
    (2548, 2548, "other_display_candidate"),
    (2549, 2580, "regional_group_leader_label"),
    (2581, 2779, "code_placeholder"),
    (2780, 2997, "other_display_candidate"),
    (2998, 2999, "code_placeholder"),
    (3000, 3104, "other_display_candidate"),
    (3105, 3115, "code_placeholder"),
    (3116, 3117, "other_display_candidate"),
    (3118, 3200, "code_placeholder"),
)
ANALYSIS_CLASS_COUNTS = {
    "code_placeholder": 488,
    "other_display_candidate": 328,
    "regional_group_leader_label": 178,
}


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def validate_static_profile() -> None:
    expected_start = ANALYSIS_START
    counts: Counter[str] = Counter()
    for start_id, end_id, classification in ANALYSIS_RUNS:
        if start_id != expected_start or end_id < start_id:
            raise shared.EvStrDataError("v0.13 analysis runs are not contiguous")
        counts[classification] += end_id - start_id + 1
        expected_start = end_id + 1
    if expected_start != ANALYSIS_END + 1:
        raise shared.EvStrDataError("v0.13 analysis runs do not cover the full range")
    if dict(counts) != ANALYSIS_CLASS_COUNTS or sum(counts.values()) != ANALYSIS_COUNT:
        raise shared.EvStrDataError("v0.13 analysis class counts differ from reviewed pins")


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> dict[int, str]:
    validate_static_profile()
    for entry_id in range(DEFERRED_START, DEFERRED_END + 1):
        for language in shared.LANGUAGES:
            source = loaded[language]["table"].texts[entry_id]
            if common.text_hash(source) != DEFERRED_REFERENCE_HASHES[language]:
                raise shared.EvStrDataError(
                    f"id {entry_id} {language}: deferred placeholder hash mismatch"
                )

    expected_ids = list(range(TRANSLATED_START, TRANSLATED_END + 1))
    if sorted(TRANSLATIONS) != expected_ids:
        raise shared.EvStrDataError("v0.13 translation ids are not the exact reviewed range")

    translations: dict[int, str] = {}
    replacement_by_source_hash: dict[str, str] = {}
    for entry_id in expected_ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        source_hash = common.text_hash(source_sc)
        pinned = TRANSLATIONS[entry_id]
        if source_hash != pinned["source_sc_utf16le_sha256"]:
            raise shared.EvStrDataError(f"id {entry_id}: SC translation pin mismatch")
        if any(not loaded[language]["table"].texts[entry_id].strip() for language in shared.LANGUAGES):
            raise shared.EvStrDataError(f"id {entry_id}: empty aligned display label")
        replacement = pinned["ko"]
        failures = shared.replacement_failures(source_sc, replacement)
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
        prior = replacement_by_source_hash.setdefault(source_hash, replacement)
        if prior != replacement:
            raise shared.EvStrDataError(
                f"id {entry_id}: repeated SC source has inconsistent Korean translations"
            )
        translations[entry_id] = replacement
    return translations


def section_structure_summary(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for language in shared.LANGUAGES:
        texts = loaded[language]["table"].texts[ANALYSIS_START : ANALYSIS_END + 1]
        structures = [shared.text_structure(text) for text in texts]
        source_hashes = [common.text_hash(text) for text in texts]
        summary[language] = {
            "entry_count": len(texts),
            "nonempty_count": sum(bool(text.strip()) for text in texts),
            "unique_text_hash_count": len(set(source_hashes)),
            "ordered_text_hashes_sha256": shared.hash_json(source_hashes),
            "ids_with_printf_tokens": sum(item["printf_token_count"] > 0 for item in structures),
            "ids_with_unknown_percent": sum(item["unknown_percent_count"] > 0 for item in structures),
            "ids_with_escape_tokens": sum(item["escape_token_count"] > 0 for item in structures),
            "ids_with_control_codepoints": sum(bool(item["control_codepoints"]) for item in structures),
            "ids_with_line_breaks": sum(
                item["line_breaks_sha256"] != shared.hash_json([]) for item in structures
            ),
            "ids_with_private_use_codepoints": sum(bool(item["pua_codepoints"]) for item in structures),
            "ids_with_bracket_placeholders": sum(
                item["bracket_placeholder_count"] > 0 for item in structures
            ),
        }
    return summary


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    translations = validate_batch_sources(loaded)
    ids = list(translations)

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        replacement = translations[entry_id]
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "classification": "regional_group_leader_label",
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": shared.text_structure(
                            loaded[language]["table"].texts[entry_id]
                        ),
                    }
                    for language in shared.LANGUAGES
                },
                "translation_origin": "manual_sc_jp_tc_alignment_exact_sc_hash_pin",
            }
        )

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": shared.RESOURCE,
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": shared.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": shared.sha256(sc_raw),
            "string_count": shared.STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **shared.SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": shared.STRING_COUNT,
        }
        for language in shared.LANGUAGES
    }
    boundary_ids = (
        INSPECT_START - 1,
        INSPECT_START,
        DEFERRED_END,
        TRANSLATED_START,
        TRANSLATED_END,
        NEXT_START_ID,
        ANALYSIS_END,
    )
    deferred_range = {
        "start_id": DEFERRED_START,
        "end_id": DEFERRED_END,
        "count": DEFERRED_COUNT,
        "status": "deferred",
        "classification": "code_placeholder",
        "reason": "repeated_internal_placeholder_not_a_display_translation_target",
        "reference_utf16le_sha256": DEFERRED_REFERENCE_HASHES,
        "excluded_from_overlay_and_translation_progress": True,
    }
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v13",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": INSPECT_START,
            "end_id": INSPECT_END,
            "next_start_id": NEXT_START_ID,
            "inspected_entry_count": INSPECTED_COUNT,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "deferred_code_placeholder_count": DEFERRED_COUNT,
            "functional_section": "event_labels_regional_group_leaders_initial_batch",
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "sc_jp_tc_semantic_review",
            "exact_sc_hash_pins_for_every_translation",
            "repeated_source_requires_identical_korean_translation",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata resource; TC is the third "
            "reference alongside SC and JP. Official strings are represented only by hashes."
        ),
        "source_files": source_files,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(
                        loaded[language]["table"].texts[entry_id]
                    )
                    for language in shared.LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "inspected_entry_count": INSPECTED_COUNT,
        "translated_entry_count": TRANSLATED_COUNT,
        "deferred_entry_count": DEFERRED_COUNT,
        "entries": evidence_entries,
        "deferred_ranges": [deferred_range],
        "extended_structure_analysis": {
            "start_id": ANALYSIS_START,
            "end_id": ANALYSIS_END,
            "entry_count": ANALYSIS_COUNT,
            "classification_method": (
                "manual_sc_jp_tc_role_review_over_fully_pinned_resources_without_source_export"
            ),
            "class_counts": ANALYSIS_CLASS_COUNTS,
            "runs": [
                {
                    "start_id": start_id,
                    "end_id": end_id,
                    "count": end_id - start_id + 1,
                    "classification": classification,
                }
                for start_id, end_id, classification in ANALYSIS_RUNS
            ],
            "language_structure_summary": section_structure_summary(loaded),
        },
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v13",
        "batch_id": BATCH_ID,
        "quality_state": "event_label_draft_pending_runtime_review",
        "inspected_entry_count": INSPECTED_COUNT,
        "translated_entry_count": TRANSLATED_COUNT,
        "deferred_entry_count": DEFERRED_COUNT,
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": "regional_group_leader_label",
                "translation_origin": "manual_sc_jp_tc_alignment_exact_sc_hash_pin",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": (
                    ["rare_place_reading"] if entry_id == TRANSLATED_START else []
                ),
            }
            for entry_id in ids
        ],
        "deferred_ranges": [deferred_range],
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shared.encode_json(value))

    source_free_scan = {
        path.relative_to(out_root).as_posix(): shared.source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(
        counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for counts in source_free_scan.values()
    ):
        raise shared.EvStrDataError(
            "v0.13 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.13 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v13",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": INSPECT_START,
            "end_id": INSPECT_END,
            "next_start_id": NEXT_START_ID,
            "inspected_entry_count": INSPECTED_COUNT,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "deferred_code_placeholder_count": DEFERRED_COUNT,
            "translated_ids_sha256": shared.hash_json(ids),
            "deferred_ids_sha256": shared.hash_json(
                list(range(DEFERRED_START, DEFERRED_END + 1))
            ),
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
        },
        "extended_structure_analysis": {
            "start_id": ANALYSIS_START,
            "end_id": ANALYSIS_END,
            "entry_count": ANALYSIS_COUNT,
            "class_counts": ANALYSIS_CLASS_COUNTS,
            "run_count": len(ANALYSIS_RUNS),
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "inspected_reference_hash_count": INSPECTED_COUNT * len(shared.LANGUAGES),
            "translated_reference_hash_count": TRANSLATED_COUNT * len(shared.LANGUAGES),
            "translated_ids_nonempty_in_all_references": TRANSLATED_COUNT,
            "source_files": source_files,
        },
        "translation": {
            "manual_sc_jp_tc_aligned_count": TRANSLATED_COUNT,
            "exact_sc_hash_pins_checked": TRANSLATED_COUNT,
            "source_text_embedded": False,
            "terminology_policy": "project_proper_name_plus_compact_gukinjung_leader_pattern",
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": len(
                {TRANSLATIONS[entry_id]["source_sc_utf16le_sha256"] for entry_id in ids}
            ),
            "translated_repeated_source_group_count": 0,
            "deferred_unique_source_hash_count": 1,
            "deferred_repeated_entry_count": DEFERRED_COUNT,
            "failures": 0,
        },
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(shared.LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {
            **binary,
            "installed_target_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": shared.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "existing_v01_through_v012_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.13 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "inspected_count": INSPECTED_COUNT,
        "deferred_count": DEFERRED_COUNT,
        "next_start_id": NEXT_START_ID,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [
        game_root / "MSG" / language / "ev_strdata.bin"
        for language in shared.LANGUAGES
    ]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr13-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr13-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.13 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.13 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.13 build")
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
    print(f"inspected={result['inspected_count']}")
    print(f"translated={result['entry_count']}")
    print(f"deferred={result['deferred_count']}")
    print(f"next_start_id={result['next_start_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
