#!/usr/bin/env python3
"""Review the seventh PK msgdata structural page with stable registration history."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
B12_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_structural_review_b12"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


previous = load_module(
    "nobu16_msgdata_pk_structural_review_b13_previous",
    B12_ROOT / "build_msgdata_pk_structural_review_b12.py",
)
common = previous.common
engine = previous.engine
StructuralReviewError = previous.StructuralReviewError

BATCH_ID = "msgdata-pk-structural-review-b13-500.v1"
RESOURCE = previous.RESOURCE
OVERLAY_NAME = "msgdata_ko_pk_structural_review_b13_500.v1.json"
EVIDENCE_NAME = "msgdata_pk_structural_review_b13_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_structural_review_b13_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgdata_pk_structural_review_b13/public/{OVERLAY_NAME}"
OWNER_PATHS = previous.OWNER_PATHS + (previous.SELF_OVERLAY_PATH,)
TARGET_CATALOG_RELATIVE = previous.TARGET_CATALOG_RELATIVE
PROGRESS_RELATIVE = previous.PROGRESS_RELATIVE

EXPECTED_B12_OVERLAY_SHA256 = "C3F19E3BC311D1F739149707BB8E63AA7B92447C7E4F5F4E63F1EC9F0F21ACBF"
EXPECTED_PREDECESSOR_TARGET_COUNT = 24_424
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = "C7A01905B1DDD393305AEA671D8353D002DB33B00F4185742B95ED6BAF0ACF74"
EXPECTED_PRE_REVIEW_GAP_COUNT = 1_110
EXPECTED_PRE_REVIEW_GAP_IDS_SHA256 = previous.EXPECTED_POST_REVIEW_GAP_IDS_SHA256
EXPECTED_REVIEW_COUNT = 500
EXPECTED_FIRST_ID = 27_494
EXPECTED_LAST_ID = 28_042
EXPECTED_REVIEW_IDS_SHA256 = "1DA4D5ADC241F3EB2273F472202FB43AAC55B5EFEADBBB59455428370098E544"
EXPECTED_POST_REVIEW_GAP_COUNT = 610
EXPECTED_POST_REVIEW_GAP_IDS_SHA256 = "73F5A86727318599D1D01765F724B5991AAC7F0B463F889F280753147EA026E2"
REASON = "romanized_or_phonetic_lookup_key"
OFFICIAL_ROWSET_SHA256 = {
    "SC": "D68C4E920EE0D215D3E5E79389E992C452206518DB8B06E74EC82B89FA897907",
    "JP": "AC8A08591103CEF2D266CD68938CF280344CE887676076ABF7F106CD45562839",
    "EN": "13A1E9E81681C48FB08B159984F9192BB2D71A31385B84070C8A150199FE745C",
    "TC": "3B85B96293F9FEFB77DCF508A98DAC7A6D0342FE94244F6BBBC86834D898EC26",
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def script_counts(text: str) -> dict[str, int]:
    return previous.script_counts(text)


def load_b12_owner(repo_root: Path) -> tuple[bytes, list[int]]:
    blob = (repo_root / previous.SELF_OVERLAY_PATH).read_bytes()
    if sha256(blob) != EXPECTED_B12_OVERLAY_SHA256:
        raise StructuralReviewError("B12 direct predecessor changed")
    overlay = json.loads(blob.decode("utf-8"))
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if resource != RESOURCE or len(ids) != 500 or hash_json(ids) != previous.EXPECTED_REVIEW_IDS_SHA256:
        raise StructuralReviewError("B12 direct predecessor ownership changed")
    return blob, ids


def validate_scope(
    tables: dict[str, Any], targets: set[int], repo_root: Path,
) -> tuple[list[int], dict[int, str], set[int], dict[str, bytes]]:
    b12_selected, reason_by_id, pre_b12_claims, owner_blobs = previous.validate_scope(tables, targets, repo_root)
    b12_blob, b12_ids = load_b12_owner(repo_root)
    if b12_ids != b12_selected:
        raise StructuralReviewError("B12 artifact and classified ownership differ")
    owner_blobs = dict(owner_blobs)
    owner_blobs[previous.SELF_OVERLAY_PATH] = b12_blob
    predecessor_claims = pre_b12_claims | set(b12_ids)
    if len(predecessor_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT or hash_json(sorted(predecessor_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256:
        raise StructuralReviewError("predecessor target claim set changed")
    gap = sorted(targets - predecessor_claims)
    if len(gap) != 1110 or hash_json(gap) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    selected = gap[:500]
    if len(selected) != 500 or (selected[0], selected[-1]) != (EXPECTED_FIRST_ID, EXPECTED_LAST_ID) or hash_json(selected) != EXPECTED_REVIEW_IDS_SHA256:
        raise StructuralReviewError("seventh structural review page changed")
    if any(reason_by_id.get(entry_id) != REASON for entry_id in selected):
        raise StructuralReviewError("mixed narrative or non-key row in review page")
    post_gap = gap[500:]
    if len(post_gap) != 610 or hash_json(post_gap) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    rowsets = {language: hash_json([{"id": entry_id, "utf16le_sha256": common.text_hash(table.texts[entry_id])} for entry_id in selected]) for language, table in tables.items()}
    if rowsets != OFFICIAL_ROWSET_SHA256:
        raise StructuralReviewError("official selected rowset changed")
    for entry_id in selected:
        source = tables["SC"].texts[entry_id]
        if "\x00" in source or sum(script_counts(source).values()) or not re.fullmatch(r"[A-Za-z0-9_%+_.-]+", source.strip()):
            raise StructuralReviewError(f"unsafe or narrative lookup key at ID {entry_id}")
    return selected, reason_by_id, predecessor_claims, owner_blobs


def audit_progress(
    progress_path: Path, repo_root: Path, owner_blobs: dict[str, bytes], overlay_blob: bytes,
    targets: set[int], predecessor_claims: set[int], selected: set[int],
) -> dict[str, Any]:
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    rows = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1 or not isinstance(rows[0].get("overlay_globs"), list):
        raise StructuralReviewError("progress has no unique msgdata row")
    prefix = list(previous.previous.previous.previous.previous.previous.EXPECTED_PREDECESSOR_PATHS)
    chain = list(OWNER_PATHS) + [SELF_OVERLAY_PATH]
    historical, _successors = previous.registration_helper()(
        rows[0]["overlay_globs"], prefix, chain, 13, repo_root
    )
    for path, blob in owner_blobs.items():
        if path in historical and (repo_root / path).read_bytes() != blob:
            raise StructuralReviewError(f"registered predecessor differs: {path}")
    if SELF_OVERLAY_PATH in historical and (repo_root / SELF_OVERLAY_PATH).read_bytes() != overlay_blob:
        raise StructuralReviewError("registered B13 differs from deterministic output")
    gap = targets - predecessor_claims
    post_gap = gap - selected
    if len(gap) != 1110 or hash_json(sorted(gap)) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    if selected & predecessor_claims or selected - gap:
        raise StructuralReviewError("B13 overlaps predecessor or target scope")
    if len(post_gap) != 610 or hash_json(sorted(post_gap)) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    return {
        "pre_b07_registration_count": len(prefix), "explicit_structural_predecessor_count": 3000,
        "historical_owner_paths": list(OWNER_PATHS), "direct_predecessor_path": previous.SELF_OVERLAY_PATH,
        "self_registration_states_supported": [0, 1], "successor_registration_tolerant": True,
        "successors_excluded_from_historical_claims": True,
        "predecessor_target_count": len(predecessor_claims), "predecessor_target_ids_sha256": EXPECTED_PREDECESSOR_TARGET_IDS_SHA256,
        "pre_review_gap_count": len(gap), "pre_review_gap_ids_sha256": EXPECTED_PRE_REVIEW_GAP_IDS_SHA256,
        "post_review_gap_count": len(post_gap), "post_review_gap_ids_sha256": EXPECTED_POST_REVIEW_GAP_IDS_SHA256,
    }


def make_files(game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path) -> dict[str, bytes]:
    packed_sc, tables = previous.previous.previous.previous.previous.previous.load_tables(game_root)
    targets = previous.previous.previous.previous.previous.previous.previous.load_target_catalog(target_catalog_path)["ids"]
    selected, reason_by_id, predecessor_claims, owner_blobs = validate_scope(tables, targets, repo_root)
    sc = tables["SC"].texts
    entries = [{"id": entry_id, "source_sc_utf16le_sha256": common.text_hash(sc[entry_id]), "ko": sc[entry_id], "status": "reviewed"} for entry_id in selected]
    pin = previous.previous.previous.previous.previous.previous.previous.OFFICIAL_PINS["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA, "overlay_id": BATCH_ID, "resource": RESOURCE, "base_language": "SC", "entry_count": 500,
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {"size": pin["size"], "packed_sha256": pin["sha256"], "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"], "string_count": previous.previous.previous.previous.previous.previous.previous.STRING_COUNT},
        "defaults": {"status": "reviewed"}, "entries": entries,
    }
    common.validate_overlay_shape(overlay)
    overlay_blob = encode_json(overlay)
    audit = audit_progress(progress_path, repo_root, owner_blobs, overlay_blob, targets, predecessor_claims, set(selected))
    reason_summary = {REASON: {"count": 500, "ids_sha256": EXPECTED_REVIEW_IDS_SHA256}}
    evidence = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-evidence.v1", "batch_id": BATCH_ID, "resource": RESOURCE,
        "entry_count": 500, "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "selection": {"first_id": selected[0], "last_id": selected[-1], "reviewed_count": 500,
            "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256, "structural_before": 1110, "structural_after": 610,
            "narrative_mixed_count": 0, "blocked_count": 0},
        "reason_summary": reason_summary, "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256,
        "explicit_predecessor_sha256": {path: sha256(blob) for path, blob in owner_blobs.items()}, "progress_audit": audit,
        "entries": [{"id": entry_id, "reason": reason_by_id[entry_id], "sc_utf16le_sha256": common.text_hash(sc[entry_id]),
            "replacement_utf16le_sha256": common.text_hash(sc[entry_id]), "exact_byte_preserved": True,
            "runtime_screen_reviewed": False} for entry_id in selected],
    }
    review = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-index.v1", "batch_id": BATCH_ID, "resource": RESOURCE,
        "reviewed_count": 500, "exact_byte_preserve_count": 500, "translated_narrative_count": 0, "blocked_count": 0,
        "runtime_screen_reviewed_count": 0, "reason_summary": reason_summary,
        "entries": [{"id": entry_id, "reason": REASON, "status": "reviewed"} for entry_id in selected],
    }
    first = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    second = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    if first != second:
        raise StructuralReviewError("target reconstruction is not deterministic")
    blobs = {f"public/{OVERLAY_NAME}": encode_json(overlay), f"evidence/{EVIDENCE_NAME}": encode_json(evidence), f"review/{REVIEW_NAME}": encode_json(review)}
    for relative, blob in blobs.items():
        if "\x00" in blob.decode("utf-8") or sum(script_counts(blob.decode("utf-8")).values()):
            raise StructuralReviewError(f"public artifact is not source-free: {relative}")
    artifacts = {relative: {"path": relative, "size": len(blob), "sha256": sha256(blob)} for relative, blob in blobs.items()}
    validation = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-validation.v1", "batch_id": BATCH_ID, "resource": RESOURCE, "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {"reviewed_count": 500, "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256, "exact_byte_preserve_count": 500,
            "translated_narrative_count": 0, "narrative_mixed_count": 0, "blocked_count": 0, "duplicate_id_count": 0,
            "predecessor_overlap_count": 0, "post_review_structural_remaining": 610},
        "reason_summary": reason_summary, "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256, "progress_audit": audit,
        "replacement_invariants": {"checked": 500, "exact_utf16le_byte_preserve_count": 500, "printf_preserved": True,
            "esc_preserved": True, "pua_preserved": True, "line_breaks_preserved": True, "failures": 0},
        "source_free_scan": {relative: {**script_counts(blob.decode("utf-8")), "embedded_nul_count": blob.count(b"\x00")} for relative, blob in blobs.items()},
        "target_reconstruction": first, "reproducibility": {"in_memory_target_a_b_equal": True, "artifact_json_canonical": True,
            "self_and_successor_registration_stable": True},
        "artifacts": artifacts,
        "safety": {"commercial_source_text_included": False, "complete_game_resource_included": False,
            "global_progress_modified": False, "global_readme_modified": False, "installed_game_files_modified": False,
            "deployment_performed": False, "commit_or_push_performed": False},
    }
    blobs[VALIDATION_NAME] = encode_json(validation)
    if sum(script_counts(blobs[VALIDATION_NAME].decode("utf-8")).values()) or b"\x00" in blobs[VALIDATION_NAME]:
        raise StructuralReviewError("validation artifact is not source-free")
    return blobs


def build_reproducibly(game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path, out_root: Path) -> dict[str, Any]:
    first = make_files(game_root, repo_root, target_catalog_path, progress_path)
    second = make_files(game_root, repo_root, target_catalog_path, progress_path)
    if first != second:
        raise StructuralReviewError("artifact builds are not deterministic")
    out_root = out_root.resolve()
    if not out_root.is_relative_to(repo_root.resolve()):
        raise StructuralReviewError("output must remain inside repository workspace")
    for relative, blob in first.items():
        path = out_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    return {"reviewed_count": 500, "preserve_count": 500, "blocked_count": 0, "remaining_count": 610, "files": first}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--target-catalog", type=Path, default=REPO_ROOT / TARGET_CATALOG_RELATIVE)
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_reproducibly(args.game_root.resolve(), args.repo_root.resolve(), args.target_catalog.resolve(), args.progress.resolve(), args.out_root.resolve())
    print(f"reviewed={result['reviewed_count']}")
    print(f"preserved={result['preserve_count']}")
    print(f"blocked={result['blocked_count']}")
    print(f"remaining={result['remaining_count']}")
    for relative, blob in result["files"].items():
        print(f"{relative}_sha256={sha256(blob)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
