#!/usr/bin/env python3
"""Review and byte-preserve the third 500-row PK msgdata structural page."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
B08_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_structural_review_b08"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


previous = load_module(
    "nobu16_msgdata_pk_structural_review_b09_previous",
    B08_ROOT / "build_msgdata_pk_structural_review_b08.py",
)
common = previous.common
engine = previous.engine
StructuralReviewError = previous.StructuralReviewError

BATCH_ID = "msgdata-pk-structural-review-b09-500.v1"
RESOURCE = previous.RESOURCE
OVERLAY_NAME = "msgdata_ko_pk_structural_review_b09_500.v1.json"
EVIDENCE_NAME = "msgdata_pk_structural_review_b09_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_structural_review_b09_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgdata_pk_structural_review_b09/public/{OVERLAY_NAME}"
B07_OVERLAY_PATH = previous.B07_OVERLAY_PATH
B08_OVERLAY_PATH = previous.SELF_OVERLAY_PATH
TARGET_CATALOG_RELATIVE = previous.TARGET_CATALOG_RELATIVE
PROGRESS_RELATIVE = previous.PROGRESS_RELATIVE

EXPECTED_B07_OVERLAY_SHA256 = previous.EXPECTED_B07_OVERLAY_SHA256
EXPECTED_B08_OVERLAY_SHA256 = "8A262817778418CE6F86D11DAE7C7F56837376D83522AECB09A1930C68EECD04"
EXPECTED_PREDECESSOR_TARGET_COUNT = 22_424
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = "D17BBE660DE06E92F95D67F07A6DF4E450C9C837DC9D33C07BC0F77A78674785"
EXPECTED_PRE_REVIEW_GAP_COUNT = 3_110
EXPECTED_PRE_REVIEW_GAP_IDS_SHA256 = previous.EXPECTED_POST_REVIEW_GAP_IDS_SHA256
EXPECTED_REVIEW_COUNT = 500
EXPECTED_FIRST_ID = 19_821
EXPECTED_LAST_ID = 20_378
EXPECTED_REVIEW_IDS_SHA256 = "735FBC9DD82F8E1BEF2A0CCCD42477DCDD691CEAA0D960DBD89FB28A2B35DF55"
EXPECTED_POST_REVIEW_GAP_COUNT = 2_610
EXPECTED_POST_REVIEW_GAP_IDS_SHA256 = "728546C32585FC9EEB7DE022A4CFB0722C20118406C3F7FEA0D0A7FE9E1041F4"
REASON = "placeholder_dummy_not_a_translatable_display_message"
OFFICIAL_ROWSET_SHA256 = {
    "SC": "0EA37EE65757B1A3EF2454D49532C3EF651630E84AE9820138FE1F1BDF2EDFB4",
    "JP": "8350B87DD47611F23BB442D584AC8512F10213DD2219674AE68D158C3DD009F1",
    "EN": "32DF97D9FEA00557E7B30236DA3D512F0F8E9A6C3F59496F7815011AC979086B",
    "TC": "0EA37EE65757B1A3EF2454D49532C3EF651630E84AE9820138FE1F1BDF2EDFB4",
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_explicit_owner(
    repo_root: Path, logical_path: str, expected_sha256: str,
    expected_count: int, expected_ids_sha256: str,
) -> tuple[bytes, list[int]]:
    blob = (repo_root / logical_path).read_bytes()
    if sha256(blob) != expected_sha256:
        raise StructuralReviewError(f"explicit predecessor changed: {logical_path}")
    overlay = json.loads(blob.decode("utf-8"))
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if resource != RESOURCE or len(ids) != expected_count or hash_json(ids) != expected_ids_sha256:
        raise StructuralReviewError(f"explicit predecessor ownership changed: {logical_path}")
    return blob, ids


def validate_scope(
    tables: dict[str, Any], targets: set[int], repo_root: Path,
) -> tuple[list[int], dict[int, str], set[int], dict[str, bytes]]:
    b07_blob, b07_ids = load_explicit_owner(
        repo_root, B07_OVERLAY_PATH, EXPECTED_B07_OVERLAY_SHA256,
        previous.previous.EXPECTED_REVIEW_COUNT, previous.previous.EXPECTED_REVIEW_IDS_SHA256,
    )
    b08_blob, b08_ids = load_explicit_owner(
        repo_root, B08_OVERLAY_PATH, EXPECTED_B08_OVERLAY_SHA256,
        previous.EXPECTED_REVIEW_COUNT, previous.EXPECTED_REVIEW_IDS_SHA256,
    )
    b08_selected, reason_by_id, _groups, pre_b08_claims, _ = previous.validate_scope(tables, targets, repo_root)
    if b08_ids != b08_selected or set(b07_ids).isdisjoint(pre_b08_claims):
        raise StructuralReviewError("B07/B08 explicit ownership chain changed")
    predecessor_claims = pre_b08_claims | set(b08_ids)
    if (
        len(predecessor_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT
        or hash_json(sorted(predecessor_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256
    ):
        raise StructuralReviewError("predecessor target claim set changed")
    gap = sorted(targets - predecessor_claims)
    if len(gap) != EXPECTED_PRE_REVIEW_GAP_COUNT or hash_json(gap) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    selected = gap[:EXPECTED_REVIEW_COUNT]
    if (
        len(selected) != EXPECTED_REVIEW_COUNT
        or (selected[0], selected[-1]) != (EXPECTED_FIRST_ID, EXPECTED_LAST_ID)
        or hash_json(selected) != EXPECTED_REVIEW_IDS_SHA256
    ):
        raise StructuralReviewError("third structural review page changed")
    if any(reason_by_id.get(entry_id) != REASON for entry_id in selected):
        raise StructuralReviewError("mixed narrative or non-dummy row in review page")
    post_gap = gap[EXPECTED_REVIEW_COUNT:]
    if len(post_gap) != EXPECTED_POST_REVIEW_GAP_COUNT or hash_json(post_gap) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    rowsets = {
        language: hash_json([
            {"id": entry_id, "utf16le_sha256": common.text_hash(table.texts[entry_id])}
            for entry_id in selected
        ])
        for language, table in tables.items()
    }
    if rowsets != OFFICIAL_ROWSET_SHA256:
        raise StructuralReviewError("official selected rowset changed")
    for entry_id in selected:
        source = tables["SC"].texts[entry_id]
        if source.strip().lower() != "dummy" or "\x00" in source:
            raise StructuralReviewError(f"unsafe dummy preservation at ID {entry_id}")
        if sum(previous.previous.previous.script_counts(source).values()):
            raise StructuralReviewError(f"source script mixed at ID {entry_id}")
    return selected, reason_by_id, predecessor_claims, {B07_OVERLAY_PATH: b07_blob, B08_OVERLAY_PATH: b08_blob}


def audit_progress(
    progress_path: Path, repo_root: Path, owner_blobs: dict[str, bytes], overlay_blob: bytes,
    targets: set[int], predecessor_claims: set[int], selected: set[int],
) -> dict[str, Any]:
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    rows = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1 or not isinstance(rows[0].get("overlay_globs"), list):
        raise StructuralReviewError("progress has no unique msgdata row")
    prefix = list(previous.previous.EXPECTED_PREDECESSOR_PATHS)
    tail, _successors = previous.previous.historical_registration_tail(
        rows[0]["overlay_globs"],
        prefix,
        [B07_OVERLAY_PATH, B08_OVERLAY_PATH, SELF_OVERLAY_PATH],
        9,
        repo_root,
    )
    for logical_path, blob in owner_blobs.items():
        if logical_path in tail and (repo_root / logical_path).read_bytes() != blob:
            raise StructuralReviewError(f"registered predecessor differs: {logical_path}")
    if SELF_OVERLAY_PATH in tail and (repo_root / SELF_OVERLAY_PATH).read_bytes() != overlay_blob:
        raise StructuralReviewError("registered B09 differs from deterministic output")
    gap = targets - predecessor_claims
    post_gap = gap - selected
    if len(gap) != EXPECTED_PRE_REVIEW_GAP_COUNT or hash_json(sorted(gap)) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    if selected & predecessor_claims or selected - gap:
        raise StructuralReviewError("B09 overlaps predecessor or target scope")
    if len(post_gap) != EXPECTED_POST_REVIEW_GAP_COUNT or hash_json(sorted(post_gap)) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    return {
        "pre_b07_registration_count": len(prefix),
        "b07_explicit_ownership_count": 500, "b08_explicit_ownership_count": 500,
        "b07_registration_count": tail.count(B07_OVERLAY_PATH),
        "b08_registration_count": tail.count(B08_OVERLAY_PATH),
        "self_registration_count": tail.count(SELF_OVERLAY_PATH),
        "predecessor_target_count": len(predecessor_claims),
        "predecessor_target_ids_sha256": EXPECTED_PREDECESSOR_TARGET_IDS_SHA256,
        "pre_review_gap_count": len(gap), "pre_review_gap_ids_sha256": EXPECTED_PRE_REVIEW_GAP_IDS_SHA256,
        "post_review_gap_count": len(post_gap), "post_review_gap_ids_sha256": EXPECTED_POST_REVIEW_GAP_IDS_SHA256,
    }


def make_files(game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path) -> dict[str, bytes]:
    packed_sc, tables = previous.previous.load_tables(game_root)
    targets = previous.previous.previous.load_target_catalog(target_catalog_path)["ids"]
    selected, reason_by_id, predecessor_claims, owner_blobs = validate_scope(tables, targets, repo_root)
    sc = tables["SC"].texts
    entries = [{"id": entry_id, "source_sc_utf16le_sha256": common.text_hash(sc[entry_id]),
        "ko": sc[entry_id], "status": "reviewed"} for entry_id in selected]
    pin = previous.previous.previous.OFFICIAL_PINS["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA, "overlay_id": BATCH_ID, "resource": RESOURCE, "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {"size": pin["size"], "packed_sha256": pin["sha256"], "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"], "string_count": previous.previous.previous.STRING_COUNT},
        "defaults": {"status": "reviewed"}, "entries": entries,
    }
    common.validate_overlay_shape(overlay)
    overlay_blob = encode_json(overlay)
    audit = audit_progress(progress_path, repo_root, owner_blobs, overlay_blob, targets, predecessor_claims, set(selected))
    for key in ("b07_registration_count", "b08_registration_count", "self_registration_count"):
        audit[key] = 0
    reason_summary = {REASON: {"count": 500, "ids_sha256": EXPECTED_REVIEW_IDS_SHA256}}
    evidence = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-evidence.v1", "batch_id": BATCH_ID, "resource": RESOURCE,
        "entry_count": 500, "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "selection": {"first_id": selected[0], "last_id": selected[-1], "reviewed_count": 500,
            "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256, "structural_before": EXPECTED_PRE_REVIEW_GAP_COUNT,
            "structural_after": EXPECTED_POST_REVIEW_GAP_COUNT, "narrative_mixed_count": 0, "blocked_count": 0},
        "reason_summary": reason_summary, "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256,
        "explicit_predecessor_sha256": {path: sha256(blob) for path, blob in owner_blobs.items()}, "progress_audit": audit,
        "entries": [{"id": entry_id, "reason": reason_by_id[entry_id],
            "sc_utf16le_sha256": common.text_hash(sc[entry_id]), "replacement_utf16le_sha256": common.text_hash(sc[entry_id]),
            "exact_byte_preserved": True, "runtime_screen_reviewed": False} for entry_id in selected],
    }
    review = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-index.v1", "batch_id": BATCH_ID, "resource": RESOURCE,
        "reviewed_count": 500, "exact_byte_preserve_count": 500, "translated_narrative_count": 0,
        "blocked_count": 0, "runtime_screen_reviewed_count": 0, "reason_summary": reason_summary,
        "entries": [{"id": entry_id, "reason": REASON, "status": "reviewed"} for entry_id in selected],
    }
    first = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    second = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    if first != second:
        raise StructuralReviewError("target reconstruction is not deterministic")
    blobs = {f"public/{OVERLAY_NAME}": encode_json(overlay), f"evidence/{EVIDENCE_NAME}": encode_json(evidence), f"review/{REVIEW_NAME}": encode_json(review)}
    for relative, blob in blobs.items():
        if "\x00" in blob.decode("utf-8") or sum(previous.previous.previous.script_counts(blob.decode("utf-8")).values()):
            raise StructuralReviewError(f"public artifact is not source-free: {relative}")
    artifacts = {relative: {"path": relative, "size": len(blob), "sha256": sha256(blob)} for relative, blob in blobs.items()}
    validation = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-validation.v1", "batch_id": BATCH_ID,
        "resource": RESOURCE, "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {"reviewed_count": 500, "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256,
            "exact_byte_preserve_count": 500, "translated_narrative_count": 0, "narrative_mixed_count": 0,
            "blocked_count": 0, "duplicate_id_count": 0, "predecessor_overlap_count": 0,
            "post_review_structural_remaining": EXPECTED_POST_REVIEW_GAP_COUNT},
        "reason_summary": reason_summary, "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256,
        "progress_audit": audit,
        "replacement_invariants": {"checked": 500, "exact_utf16le_byte_preserve_count": 500,
            "printf_preserved": True, "esc_preserved": True, "pua_preserved": True, "line_breaks_preserved": True, "failures": 0},
        "source_free_scan": {relative: {**previous.previous.previous.script_counts(blob.decode("utf-8")),
            "embedded_nul_count": blob.count(b"\x00")} for relative, blob in blobs.items()},
        "target_reconstruction": first, "reproducibility": {"in_memory_target_a_b_equal": True, "artifact_json_canonical": True},
        "artifacts": artifacts,
        "safety": {"commercial_source_text_included": False, "complete_game_resource_included": False,
            "global_progress_modified": False, "global_readme_modified": False, "installed_game_files_modified": False,
            "deployment_performed": False, "commit_or_push_performed": False},
    }
    blobs[VALIDATION_NAME] = encode_json(validation)
    if sum(previous.previous.previous.script_counts(blobs[VALIDATION_NAME].decode("utf-8")).values()) or b"\x00" in blobs[VALIDATION_NAME]:
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
    return {"reviewed_count": 500, "preserve_count": 500, "blocked_count": 0, "remaining_count": 2610, "files": first}


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
