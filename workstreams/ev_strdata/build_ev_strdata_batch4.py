#!/usr/bin/env python3
"""Build source-free MSG/SC/ev_strdata officer-name batch4 artifacts."""

from __future__ import annotations

import argparse
import sys
import tempfile
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


BATCH_ID = "ev-strdata-officer-names-0550-0749-v0.4"
OVERLAY_NAME = "ev_strdata_ko_officer_names_0550_0749.v0.4.json"
EVIDENCE_NAME = "alignment_evidence.v0.4.json"
REVIEW_NAME = "review_index.v0.4.json"
VALIDATION_NAME = "validation.v0.4.json"
SCOPE_START = 550
SCOPE_END = 749
NEXT_START_ID = 750
SELECTED_COUNT = SCOPE_END - SCOPE_START + 1


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def load_translations(sc_table: Any) -> dict[int, str]:
    seed_path = REPO_ROOT / shared.SEED_RELATIVE
    seed_blob = seed_path.read_bytes()
    if shared.sha256(seed_blob) != shared.SEED_SHA256:
        raise shared.EvStrDataError("pinned officer-name seed overlay changed")
    seed = shared.load_json(seed_path)
    entries = seed.get("entries")
    if not isinstance(entries, list):
        raise shared.EvStrDataError("seed entries must be an array")
    by_id = {
        int(entry["id"]): entry
        for entry in entries
        if isinstance(entry, dict) and "id" in entry
    }
    translations: dict[int, str] = {}
    for entry_id in range(SCOPE_START, SCOPE_END + 1):
        entry = by_id.get(entry_id)
        if entry is None:
            raise shared.EvStrDataError(f"seed has no officer-name entry {entry_id}")
        source = sc_table.texts[entry_id]
        if not source.strip():
            raise shared.EvStrDataError(f"selected SC id {entry_id} is not display text")
        if entry.get("source_sc_utf16le_sha256") != common.text_hash(source):
            raise shared.EvStrDataError(
                f"id {entry_id}: seed source hash does not match ev_strdata SC"
            )
        replacement = entry.get("ko")
        if not isinstance(replacement, str) or not replacement.strip():
            raise shared.EvStrDataError(f"id {entry_id}: seed Korean name is empty")
        failures = shared.replacement_failures(source, replacement)
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
        translations[entry_id] = replacement
    return translations


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    sc_table = loaded["SC"]["table"]
    translations = load_translations(sc_table)
    ids = list(translations)
    if ids != list(range(SCOPE_START, SCOPE_END + 1)):
        raise shared.EvStrDataError("selected ids are not the exact contiguous batch range")

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    failures: list[str] = []
    for entry_id in ids:
        source_sc = sc_table.texts[entry_id]
        replacement = translations[entry_id]
        failures.extend(
            f"id {entry_id}: {failure}"
            for failure in shared.replacement_failures(source_sc, replacement)
        )
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
                "translation_reuse_exact_sc_hash_match": True,
            }
        )
    if failures:
        raise shared.EvStrDataError(f"replacement invariant failures: {failures[:5]}")

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
    boundary_ids = (SCOPE_START - 1, SCOPE_START, SCOPE_END, NEXT_START_ID)
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v4",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "next_start_id": NEXT_START_ID,
            "selected_display_entry_count": len(ids),
            "functional_section": "officer_full_name_catalog_continuation_batch",
            "boundary_reason": "continued the officer-name section to the 200-entry batch cap",
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "selected_ids_nonempty_in_sc_jp_tc",
            "existing_korean_officer_name_reused_only_on_exact_sc_hash_match",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata.bin; TC is the third "
            "reference alongside SC and JP."
        ),
        "source_files": source_files,
        "translation_seed": {
            "relative_path": shared.SEED_RELATIVE.as_posix(),
            "sha256": shared.SEED_SHA256,
            "commercial_source_text_included": False,
        },
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
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v4",
        "batch_id": BATCH_ID,
        "quality_state": "project_officer_name_draft_pending_runtime_review",
        "entry_count": len(ids),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "translation_origin": "existing_officer_name_overlay_exact_sc_hash_match",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": [],
            }
            for entry_id in ids
        ],
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
            "public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during the build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v4",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "next_start_id": NEXT_START_ID,
            "selected_display_entry_count": len(ids),
            "selected_ids_sha256": shared.hash_json(ids),
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "selected_reference_hash_count": len(ids) * len(shared.LANGUAGES),
            "selected_ids_nonempty_in_all_references": len(ids),
            "source_files": source_files,
        },
        "translation_reuse": {
            "seed_relative_path": shared.SEED_RELATIVE.as_posix(),
            "seed_sha256": shared.SEED_SHA256,
            "exact_sc_hash_matches": len(ids),
            "mismatches": 0,
        },
        "replacement_invariants": {
            "checked": len(ids),
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
            "existing_v01_v02_v03_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    return {
        "entry_count": len(ids),
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr4-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr4-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError("final public artifacts differ from isolated A/B output")
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across reproducible build")
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
    print(f"next_start_id={result['next_start_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
