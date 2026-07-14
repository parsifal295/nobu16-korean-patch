#!/usr/bin/env python3
"""Verify the dialogue draft, A/B generation, and standalone file-only build."""

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
import build_event_dialogue_batch as batch  # noqa: E402


GENERATED_PATHS = (
    f"public/{batch.OVERLAY_NAME}",
    "evidence/alignment_evidence.v0.1.json",
    "review/review_index.v0.1.json",
    "validation.json",
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


def artifact(path: Path, relative_path: str) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"path": relative_path, "size": len(blob), "sha256": sha256(blob)}


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
        Path(tempfile.mkdtemp(prefix="dialogue_recipe_a_", dir=scratch_root)),
        Path(tempfile.mkdtemp(prefix="dialogue_recipe_b_", dir=scratch_root)),
    ]
    results: list[dict[str, Any]] = []
    stock_before = sha256(stock_sc.read_bytes())
    for run_dir in run_dirs:
        game_root = run_dir / "stock_root"
        stock_copy = game_root / "MSG_PK" / "SC" / "msgev.bin"
        stock_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stock_sc, stock_copy)
        result = common.build_overlay(game_root, overlay_path, run_dir / "build")
        results.append(result)
    if sha256(stock_sc.read_bytes()) != stock_before:
        raise ValueError("pinned SC stock changed during isolated build")

    relative_outputs = (
        "MSG_PK/SC/msgev.bin",
        "msgev.build-manifest.json",
        "msgev_sc.recipe.json",
    )
    output_results: list[dict[str, Any]] = []
    for relative in relative_outputs:
        a_path = run_dirs[0] / "build" / Path(relative)
        b_path = run_dirs[1] / "build" / Path(relative)
        a_blob = a_path.read_bytes()
        b_blob = b_path.read_bytes()
        if a_blob != b_blob:
            raise ValueError(f"standalone A/B build mismatch for {relative}")
        output_results.append(
            {
                "path": relative,
                "size": len(a_blob),
                "sha256": sha256(a_blob),
                "a_b_byte_identical": True,
            }
        )
    if results[0]["operations"] != len(batch.TRANSLATIONS):
        raise ValueError("standalone build operation count differs from selected entries")
    return {
        "operations": results[0]["operations"],
        "outputs": output_results,
        "installed_game_files_modified": False,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    final_root = args.final_root.resolve()
    overlay_path = final_root / "public" / batch.OVERLAY_NAME
    generated = compare_generated(
        args.build_a.resolve(), args.build_b.resolve(), final_root
    )

    overlay, _ = common.load_json_strict(overlay_path)
    resource, _, normalized_entries = common.validate_overlay_shape(overlay)
    ids = batch.selected_ids()
    if [entry["id"] for entry in normalized_entries] != ids:
        raise ValueError("overlay ids differ from the declared event ranges")

    source_paths = {"SC": args.stock_sc, "JP": args.stock_jp, "EN": args.stock_en}
    sources = {
        language: batch.load_source(path, language)
        for language, path in source_paths.items()
    }
    tables = {language: values[2] for language, values in sources.items()}
    for entry in normalized_entries:
        entry_id = int(entry["id"])
        source = tables["SC"].texts[entry_id]
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"]:
            raise ValueError(f"id {entry_id} SC source hash mismatch")
        problems = common.invariant_mismatches(source, str(entry["ko"]))
        if problems:
            raise ValueError(f"id {entry_id} invariant mismatch: {problems}")

    evidence = load_json(final_root / "evidence" / "alignment_evidence.v0.1.json")
    if evidence.get("entry_count") != len(ids):
        raise ValueError("alignment evidence entry count mismatch")
    evidence_entries = evidence.get("entries")
    if not isinstance(evidence_entries, list):
        raise ValueError("alignment evidence entries must be an array")
    for expected_id, entry in zip(ids, evidence_entries, strict=True):
        if entry.get("id") != expected_id:
            raise ValueError("alignment evidence ids are not sorted and complete")
        references = entry.get("references")
        if not isinstance(references, dict):
            raise ValueError(f"id {expected_id} alignment references missing")
        for language in ("SC", "JP", "EN"):
            expected_hash = common.text_hash(tables[language].texts[expected_id])
            if references.get(language, {}).get("utf16le_sha256") != expected_hash:
                raise ValueError(f"id {expected_id} {language} evidence hash mismatch")
        if entry.get("manual_semantic_crosscheck") is not True:
            raise ValueError(f"id {expected_id} semantic crosscheck not recorded")

    review = load_json(final_root / "review" / "review_index.v0.1.json")
    batch.validate_public_shapes(evidence, review, ids)
    review_entries = review.get("entries")
    if not isinstance(review_entries, list) or len(review_entries) != len(ids):
        raise ValueError("review index entry count mismatch")
    for expected_id, entry in zip(ids, review_entries, strict=True):
        if entry.get("id") != expected_id:
            raise ValueError("review ids are not sorted and complete")
        if entry.get("automated_draft") is not True:
            raise ValueError(f"id {expected_id} is not labelled as automated draft")
        if entry.get("human_review_required") is not True:
            raise ValueError(f"id {expected_id} is not labelled for human review")
        if entry.get("runtime_reviewed") is not False:
            raise ValueError(f"id {expected_id} runtime status is not conservative")

    source_free_results: list[dict[str, Any]] = []
    for relative in GENERATED_PATHS:
        text = (final_root / relative).read_text(encoding="utf-8")
        cjk_count = batch.cjk_unified_count(text)
        kana_count = batch.kana_count(text)
        if cjk_count or kana_count:
            raise ValueError(
                f"public artifact has CJK Unified or kana characters: {relative}"
            )
        source_free_results.append(
            {
                "path": relative,
                "cjk_unified_count": 0,
                "kana_count": 0,
                "passed": True,
            }
        )

    generation_validation = load_json(final_root / "validation.json")
    batch.validate_generation_validation_shape(generation_validation)
    expected_font_integration = batch.font_v5_integration()
    if generation_validation.get("font_integration") != expected_font_integration:
        raise ValueError("font-v5 integration evidence differs from the pinned baseline")

    standalone = isolated_build(
        args.scratch_root.resolve(), args.stock_sc.resolve(), overlay_path
    )
    verification = {
        "schema": "nobu16.kr.event-dialogue-verification.v1",
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
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
        },
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
        "font_integration": expected_font_integration,
        "standalone_file_only_build": standalone,
        "determinism": {
            "generator_a_b_final_byte_identical": True,
            "standalone_recipe_a_b_byte_identical": True,
        },
        "safety": {
            "installed_game_files_modified": False,
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
    out_path = final_root / "verification.json"
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
