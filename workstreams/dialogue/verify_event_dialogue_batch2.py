#!/usr/bin/env python3
"""Verify batch2 generation, alignment evidence, and isolated file-only builds."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch2 as batch  # noqa: E402


GENERATED_PATHS = (
    f"public/{batch.OVERLAY_NAME}",
    f"evidence/{batch.EVIDENCE_NAME}",
    f"review/{batch.REVIEW_NAME}",
    batch.VALIDATION_NAME,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes().decode("utf-8-sig"), object_pairs_hook=common.strict_object
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def compare_generated(a: Path, b: Path, final_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for relative in GENERATED_PATHS:
        a_blob = (a / relative).read_bytes()
        b_blob = (b / relative).read_bytes()
        final_blob = (final_root / relative).read_bytes()
        if a_blob != b_blob or a_blob != final_blob:
            raise ValueError(f"A/B/final mismatch for {relative}")
        results.append(
            {
                "path": relative,
                "size": len(final_blob),
                "sha256": sha256(final_blob),
                "a_b_final_byte_identical": True,
            }
        )
    return results


def isolated_build(
    scratch_root: Path, stock_sc: Path, overlay_path: Path
) -> dict[str, Any]:
    scratch_root.mkdir(parents=True, exist_ok=True)
    run_dirs = [
        Path(tempfile.mkdtemp(prefix="dialogue_batch2_recipe_a_", dir=scratch_root)),
        Path(tempfile.mkdtemp(prefix="dialogue_batch2_recipe_b_", dir=scratch_root)),
    ]
    builder_results: list[dict[str, Any]] = []
    stock_before = sha256(stock_sc.read_bytes())
    for run_dir in run_dirs:
        game_root = run_dir / "stock_root"
        stock_copy = game_root / "MSG_PK" / "SC" / "msgev.bin"
        stock_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stock_sc, stock_copy)
        builder_results.append(
            common.build_overlay(game_root, overlay_path, run_dir / "build")
        )
    if sha256(stock_sc.read_bytes()) != stock_before:
        raise ValueError("pinned SC stock changed during isolated build")

    outputs: list[dict[str, Any]] = []
    for relative in (
        "MSG_PK/SC/msgev.bin",
        "msgev.build-manifest.json",
        "msgev_sc.recipe.json",
    ):
        a_blob = (run_dirs[0] / "build" / Path(relative)).read_bytes()
        b_blob = (run_dirs[1] / "build" / Path(relative)).read_bytes()
        if a_blob != b_blob:
            raise ValueError(f"isolated A/B build mismatch for {relative}")
        outputs.append(
            {
                "path": relative,
                "size": len(a_blob),
                "sha256": sha256(a_blob),
                "a_b_byte_identical": True,
            }
        )
    operation_count = int(builder_results[0]["operations"])
    if operation_count != len(batch.TRANSLATIONS):
        raise ValueError("isolated operation count differs from batch2 entries")
    return {
        "operations": operation_count,
        "outputs": outputs,
        "pinned_stock_sha256_before_after": stock_before,
        "installed_game_files_modified": False,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    final_root = args.final_root.resolve()
    generated = compare_generated(
        args.build_a.resolve(), args.build_b.resolve(), final_root
    )
    overlay_path = final_root / "public" / batch.OVERLAY_NAME
    overlay, _ = common.load_json_strict(overlay_path)
    resource, _, normalized_entries = common.validate_overlay_shape(overlay)
    ids = batch.selected_ids()
    if [entry["id"] for entry in normalized_entries] != ids:
        raise ValueError("overlay ids differ from exact batch2 range")

    source_paths = {"SC": args.stock_sc, "JP": args.stock_jp, "EN": args.stock_en}
    sources = {
        language: batch.load_source(path, language)
        for language, path in source_paths.items()
    }
    tables = {language: values[2] for language, values in sources.items()}
    for entry in normalized_entries:
        entry_id = int(entry["id"])
        source_sc = tables["SC"].texts[entry_id]
        if common.text_hash(source_sc) != entry["source_sc_utf16le_sha256"]:
            raise ValueError(f"id {entry_id} SC source hash mismatch")
        problems = common.invariant_mismatches(source_sc, str(entry["ko"]))
        if problems:
            raise ValueError(f"id {entry_id} invariant mismatch: {problems}")

    evidence = load_json(final_root / "evidence" / batch.EVIDENCE_NAME)
    review = load_json(final_root / "review" / batch.REVIEW_NAME)
    batch.validate_public_shapes(evidence, review, ids)
    if evidence.get("batch_id") != batch.BATCH_ID:
        raise ValueError("alignment evidence batch id mismatch")
    if evidence.get("event_ranges") != list(batch.EVENTS):
        raise ValueError("alignment evidence event ranges mismatch")
    source_files = evidence.get("source_files")
    if not isinstance(source_files, dict):
        raise ValueError("alignment evidence source files missing")
    for language in ("SC", "JP", "EN"):
        expected_pin = {**batch.SOURCE_PINS[language], "string_count": batch.STRING_COUNT}
        if source_files.get(language) != expected_pin:
            raise ValueError(f"alignment evidence {language} source pin mismatch")
    boundary_anchors = evidence.get("boundary_anchors")
    expected_boundary_ids = [3229, 3230, 3244, 3245, 3260, 3261, 3276, 3277, 3286, 3287, 3308, 3309]
    if not isinstance(boundary_anchors, list) or [
        anchor.get("id") for anchor in boundary_anchors
    ] != expected_boundary_ids:
        raise ValueError("alignment evidence boundary anchors mismatch")
    for anchor in boundary_anchors:
        boundary_id = int(anchor["id"])
        hashes = anchor.get("hashes")
        if not isinstance(hashes, dict):
            raise ValueError(f"boundary {boundary_id} hashes missing")
        for language in ("SC", "JP", "EN"):
            expected_hash = common.text_hash(tables[language].texts[boundary_id])
            if hashes.get(language) != expected_hash:
                raise ValueError(f"boundary {boundary_id} {language} hash mismatch")
    evidence_entries = evidence.get("entries")
    review_entries = review.get("entries")
    if not isinstance(evidence_entries, list) or not isinstance(review_entries, list):
        raise ValueError("batch2 evidence or review entries are not arrays")
    for expected_id, evidence_entry, review_entry in zip(
        ids, evidence_entries, review_entries, strict=True
    ):
        if evidence_entry.get("id") != expected_id or review_entry.get("id") != expected_id:
            raise ValueError("batch2 evidence/review ids are not sorted and complete")
        references = evidence_entry.get("references")
        if not isinstance(references, dict):
            raise ValueError(f"id {expected_id} references missing")
        for language in ("SC", "JP", "EN"):
            expected_hash = common.text_hash(tables[language].texts[expected_id])
            if references.get(language, {}).get("utf16le_sha256") != expected_hash:
                raise ValueError(f"id {expected_id} {language} evidence hash mismatch")
        if evidence_entry.get("manual_semantic_crosscheck") is not True:
            raise ValueError(f"id {expected_id} semantic crosscheck not recorded")
        if review_entry.get("automated_draft") is not True:
            raise ValueError(f"id {expected_id} draft origin is not conservative")
        if review_entry.get("human_review_required") is not True:
            raise ValueError(f"id {expected_id} human review is not required")
        if review_entry.get("runtime_reviewed") is not False:
            raise ValueError(f"id {expected_id} runtime status is not conservative")
        if review_entry.get("uncertainty_flags") != batch.UNCERTAINTY_FLAGS.get(
            expected_id, []
        ):
            raise ValueError(f"id {expected_id} uncertainty flags mismatch")

    source_free_results: list[dict[str, Any]] = []
    for relative in GENERATED_PATHS:
        text = (final_root / relative).read_text(encoding="utf-8")
        cjk_count = batch.cjk_unified_count(text)
        kana_count = batch.kana_count(text)
        if cjk_count or kana_count:
            raise ValueError(f"source script found in public artifact: {relative}")
        source_free_results.append(
            {
                "path": relative,
                "cjk_unified_count": 0,
                "kana_count": 0,
                "passed": True,
            }
        )

    generation_validation = load_json(final_root / batch.VALIDATION_NAME)
    batch.validate_generation_validation_shape(generation_validation)
    expected_followup = batch.font_followup()
    if generation_validation.get("font_followup") != expected_followup:
        raise ValueError("font follow-up evidence differs from current Korean text")
    if generation_validation.get("selected_entry_count") != len(ids):
        raise ValueError("generation validation entry count mismatch")
    expected_artifacts = {
        "overlay": generated[0],
        "alignment_evidence": generated[1],
        "review_index": generated[2],
    }
    recorded_artifacts = generation_validation.get("artifacts")
    if not isinstance(recorded_artifacts, dict):
        raise ValueError("generation validation artifact records missing")
    for name, generated_item in expected_artifacts.items():
        expected_record = {
            "path": generated_item["path"],
            "size": generated_item["size"],
            "sha256": generated_item["sha256"],
        }
        if recorded_artifacts.get(name) != expected_record:
            raise ValueError(f"generation validation {name} record mismatch")
    generator = generation_validation.get("generator")
    expected_generator = {
        "path": batch.SCRIPT_PATH.name,
        "sha256": sha256(batch.SCRIPT_PATH.read_bytes()),
        "dependencies": {
            "build_event_dialogue_batch.py": sha256(
                (batch.WORKSTREAM_DIR / "build_event_dialogue_batch.py").read_bytes()
            ),
            "build_common_message_overlay.py": sha256(
                (batch.TOOLS_DIR / "build_common_message_overlay.py").read_bytes()
            ),
        },
    }
    if generator != expected_generator:
        raise ValueError("generation validation generator provenance mismatch")

    standalone = isolated_build(
        args.scratch_root.resolve(), args.stock_sc.resolve(), overlay_path
    )
    verification = {
        "schema": "nobu16.kr.event-dialogue-verification.v2",
        "batch_id": batch.BATCH_ID,
        "passed": True,
        "resource": resource,
        "events": list(batch.EVENTS),
        "entry_count": len(ids),
        "generated_artifacts": generated,
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": batch.STRING_COUNT,
            "selected_id_hashes_verified": len(ids) * 3,
            "manual_semantic_crosschecks_recorded": len(ids),
        },
        "replacement_invariants": {"checked": len(ids), "failures": 0},
        "draft_review_state": {
            "automated_draft": len(ids),
            "human_review_required": len(ids),
            "runtime_reviewed": 0,
            "specific_uncertainty_entries": len(batch.UNCERTAINTY_FLAGS),
        },
        "source_free_scan": source_free_results,
        "strict_schema": {
            "artifacts_checked": [
                "overlay",
                "alignment_evidence",
                "review_index",
                "validation",
            ],
            "duplicate_or_case_colliding_keys_rejected": True,
            "unexpected_keys_rejected": True,
            "passed": True,
        },
        "font_followup": expected_followup,
        "standalone_file_only_build": standalone,
        "determinism": {
            "generator_a_b_final_byte_identical": True,
            "standalone_recipe_a_b_byte_identical": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "current_font_v6_or_installer_modified": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "complete_commercial_resource_in_workstream": False,
        },
        "verifier": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
    }
    encoded = batch.encode_json(verification)
    out_path = final_root / batch.VERIFICATION_NAME
    out_path.write_bytes(encoded)
    return {
        "path": out_path,
        "sha256": sha256(encoded),
        "entry_count": len(ids),
        "standalone": standalone,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-a", type=Path, required=True)
    parser.add_argument("--build-b", type=Path, required=True)
    parser.add_argument("--final-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument(
        "--stock-sc",
        type=Path,
        default=batch.WORKSPACE_ROOT
        / "KR_PATCH_WORK"
        / "backups"
        / "officer_name_probe_v0_1"
        / "msgev.SC.stock.bin",
    )
    parser.add_argument(
        "--stock-jp",
        type=Path,
        default=batch.WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgev.bin",
    )
    parser.add_argument(
        "--stock-en",
        type=Path,
        default=batch.WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgev.bin",
    )
    return parser.parse_args()


def main() -> int:
    try:
        result = verify(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"verification={result['path']}")
    print(f"verification_sha256={result['sha256']}")
    print(f"entries={result['entry_count']}")
    print(f"standalone_operations={result['standalone']['operations']}")
    print("passed=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
