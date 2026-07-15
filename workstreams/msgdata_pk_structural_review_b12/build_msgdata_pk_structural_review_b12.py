#!/usr/bin/env python3
"""Review the sixth PK msgdata structural page with registration-stable output."""

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
B11_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_structural_review_b11"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


previous = load_module(
    "nobu16_msgdata_pk_structural_review_b12_previous",
    B11_ROOT / "build_msgdata_pk_structural_review_b11.py",
)
common = previous.common
engine = previous.engine
StructuralReviewError = previous.StructuralReviewError

BATCH_ID = "msgdata-pk-structural-review-b12-500.v1"
RESOURCE = previous.RESOURCE
OVERLAY_NAME = "msgdata_ko_pk_structural_review_b12_500.v1.json"
EVIDENCE_NAME = "msgdata_pk_structural_review_b12_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_structural_review_b12_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgdata_pk_structural_review_b12/public/{OVERLAY_NAME}"
OWNER_PATHS = previous.OWNER_PATHS + (previous.SELF_OVERLAY_PATH,)
TARGET_CATALOG_RELATIVE = previous.TARGET_CATALOG_RELATIVE
PROGRESS_RELATIVE = previous.PROGRESS_RELATIVE

EXPECTED_B11_OVERLAY_SHA256 = "9C5C16DF069E214CAD7FA82316D2603A4E8C3A8654C8F64D5696EC9308F5942E"
EXPECTED_PREDECESSOR_TARGET_COUNT = 23_924
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = "882BDBDCDA5E510ABDE723173C2C6E6DC67CD4E462CC2EB75987397463EE4A59"
EXPECTED_PRE_REVIEW_GAP_COUNT = 1_610
EXPECTED_PRE_REVIEW_GAP_IDS_SHA256 = previous.EXPECTED_POST_REVIEW_GAP_IDS_SHA256
EXPECTED_REVIEW_COUNT = 500
EXPECTED_FIRST_ID = 26_887
EXPECTED_LAST_ID = 27_493
EXPECTED_REVIEW_IDS_SHA256 = "BA8FB8B6C520E1783B1ED55BA49BBB0425820C0DC740DDFA8DE14BE87678D88D"
EXPECTED_POST_REVIEW_GAP_COUNT = 1_110
EXPECTED_POST_REVIEW_GAP_IDS_SHA256 = "A5A442486459B5F3E5AE72148E066C4FEA159BD9D792CD0BAABCAC257CAE4E0C"
REASON = "romanized_or_phonetic_lookup_key"
OFFICIAL_ROWSET_SHA256 = {
    "SC": "C5212DC0B6A6A8B7EA78EB862479EAA1EC1D37341B7FA7E3B5C50B6B40D7E98E",
    "JP": "8D3B2F6F287CA7542536F34CC943C0A9A6651C492BA80885493B6C2A3183219A",
    "EN": "C5212DC0B6A6A8B7EA78EB862479EAA1EC1D37341B7FA7E3B5C50B6B40D7E98E",
    "TC": "C5212DC0B6A6A8B7EA78EB862479EAA1EC1D37341B7FA7E3B5C50B6B40D7E98E",
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def registration_helper():
    return previous.previous.previous.previous.previous.historical_registration_tail


def script_counts(text: str) -> dict[str, int]:
    return previous.previous.previous.previous.previous.previous.script_counts(text)


def load_b11_owner(repo_root: Path) -> tuple[bytes, list[int]]:
    blob = (repo_root / previous.SELF_OVERLAY_PATH).read_bytes()
    if sha256(blob) != EXPECTED_B11_OVERLAY_SHA256:
        raise StructuralReviewError("B11 explicit predecessor changed")
    overlay = json.loads(blob.decode("utf-8"))
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if resource != RESOURCE or len(ids) != 500 or hash_json(ids) != previous.EXPECTED_REVIEW_IDS_SHA256:
        raise StructuralReviewError("B11 explicit ownership set changed")
    return blob, ids


def validate_scope(
    tables: dict[str, Any], targets: set[int], repo_root: Path,
) -> tuple[list[int], dict[int, str], set[int], dict[str, bytes]]:
    b11_selected, reason_by_id, _groups, pre_b11_claims, owner_blobs = previous.validate_scope(tables, targets, repo_root)
    b11_blob, b11_ids = load_b11_owner(repo_root)
    if b11_ids != b11_selected:
        raise StructuralReviewError("B11 artifact and classified ownership differ")
    owner_blobs = dict(owner_blobs)
    owner_blobs[previous.SELF_OVERLAY_PATH] = b11_blob
    predecessor_claims = pre_b11_claims | set(b11_ids)
    if len(predecessor_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT or hash_json(sorted(predecessor_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256:
        raise StructuralReviewError("predecessor target claim set changed")
    gap = sorted(targets - predecessor_claims)
    if len(gap) != 1610 or hash_json(gap) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    selected = gap[:500]
    if len(selected) != 500 or (selected[0], selected[-1]) != (EXPECTED_FIRST_ID, EXPECTED_LAST_ID) or hash_json(selected) != EXPECTED_REVIEW_IDS_SHA256:
        raise StructuralReviewError("sixth structural review page changed")
    if any(reason_by_id.get(entry_id) != REASON for entry_id in selected):
        raise StructuralReviewError("mixed narrative or non-key row in review page")
    post_gap = gap[500:]
    if len(post_gap) != 1110 or hash_json(post_gap) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
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
    prefix = list(previous.previous.previous.previous.previous.EXPECTED_PREDECESSOR_PATHS)
    chain = list(OWNER_PATHS) + [SELF_OVERLAY_PATH]
    historical, _successors = registration_helper()(
        rows[0]["overlay_globs"], prefix, chain, 12, repo_root
    )
    for path, blob in owner_blobs.items():
        if path in historical and (repo_root / path).read_bytes() != blob:
            raise StructuralReviewError(f"registered predecessor differs: {path}")
    if SELF_OVERLAY_PATH in historical and (repo_root / SELF_OVERLAY_PATH).read_bytes() != overlay_blob:
        raise StructuralReviewError("registered B12 differs from deterministic output")
    gap = targets - predecessor_claims
    post_gap = gap - selected
    if len(gap) != 1610 or hash_json(sorted(gap)) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    if selected & predecessor_claims or selected - gap:
        raise StructuralReviewError("B12 overlaps predecessor or target scope")
    if len(post_gap) != 1110 or hash_json(sorted(post_gap)) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    # Registration observations are deliberately normalized.  Validation above
    # still checks present self/successors, while artifacts remain historical.
    return {
        "pre_b07_registration_count": len(prefix),
        "explicit_structural_predecessor_count": 2500,
        "historical_owner_paths": list(OWNER_PATHS),
        "self_registration_states_supported": [0, 1],
        "successor_registration_tolerant": True,
        "successors_excluded_from_historical_claims": True,
        "predecessor_target_count": len(predecessor_claims),
        "predecessor_target_ids_sha256": EXPECTED_PREDECESSOR_TARGET_IDS_SHA256,
        "pre_review_gap_count": len(gap), "pre_review_gap_ids_sha256": EXPECTED_PRE_REVIEW_GAP_IDS_SHA256,
        "post_review_gap_count": len(post_gap), "post_review_gap_ids_sha256": EXPECTED_POST_REVIEW_GAP_IDS_SHA256,
    }


def make_files(game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path) -> dict[str, bytes]:
    packed_sc, tables = previous.previous.previous.previous.previous.load_tables(game_root)
    targets = previous.previous.previous.previous.previous.previous.load_target_catalog(target_catalog_path)["ids"]
    selected, reason_by_id, predecessor_claims, owner_blobs = validate_scope(tables, targets, repo_root)
    sc = tables["SC"].texts
    entries = [{"id": entry_id, "source_sc_utf16le_sha256": common.text_hash(sc[entry_id]), "ko": sc[entry_id], "status": "reviewed"} for entry_id in selected]
    pin = previous.previous.previous.previous.previous.previous.OFFICIAL_PINS["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA, "overlay_id": BATCH_ID, "resource": RESOURCE, "base_language": "SC", "entry_count": 500,
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {"size": pin["size"], "packed_sha256": pin["sha256"], "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"], "string_count": previous.previous.previous.previous.previous.previous.STRING_COUNT},
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
            "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256, "structural_before": 1610, "structural_after": 1110,
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
            "predecessor_overlap_count": 0, "post_review_structural_remaining": 1110},
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
    return {"reviewed_count": 500, "preserve_count": 500, "blocked_count": 0, "remaining_count": 1110, "files": first}


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
