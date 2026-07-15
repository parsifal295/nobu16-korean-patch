#!/usr/bin/env python3
"""Review and byte-preserve the next 500 PK msgdata structural rows after B07."""

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
B07_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_structural_review_b07"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


previous = load_module(
    "nobu16_msgdata_pk_structural_review_b08_previous",
    B07_ROOT / "build_msgdata_pk_structural_review_b07.py",
)
engine = previous.engine
common = previous.common
StructuralReviewError = previous.StructuralReviewError

BATCH_ID = "msgdata-pk-structural-review-b08-500.v1"
RESOURCE = previous.RESOURCE
OVERLAY_NAME = "msgdata_ko_pk_structural_review_b08_500.v1.json"
EVIDENCE_NAME = "msgdata_pk_structural_review_b08_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_structural_review_b08_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgdata_pk_structural_review_b08/public/{OVERLAY_NAME}"
B07_OVERLAY_PATH = previous.SELF_OVERLAY_PATH
TARGET_CATALOG_RELATIVE = previous.TARGET_CATALOG_RELATIVE
PROGRESS_RELATIVE = previous.PROGRESS_RELATIVE

EXPECTED_B07_OVERLAY_SHA256 = "FA6BED36350E9EEE61F0034257269152AA126891921C9F08D90D14770C9C5006"
EXPECTED_PREDECESSOR_TARGET_COUNT = 21_924
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = "A0A2580C914F7FA4C42BDF141D945A3376E5F904DCD00C5EAE5798673E065D2B"
EXPECTED_PRE_REVIEW_GAP_COUNT = 3_610
EXPECTED_PRE_REVIEW_GAP_IDS_SHA256 = previous.EXPECTED_POST_REVIEW_GAP_IDS_SHA256
EXPECTED_REVIEW_COUNT = 500
EXPECTED_FIRST_ID = 19_199
EXPECTED_LAST_ID = 19_820
EXPECTED_REVIEW_IDS_SHA256 = "65130D53D533B45BFA2F38AD779692E0B78C178A493C85CCE50153C9FBBF894C"
EXPECTED_POST_REVIEW_GAP_COUNT = 3_110
EXPECTED_POST_REVIEW_GAP_IDS_SHA256 = "40EA6B0474C0741A97244F60CC6E91A6A6084C768377837D647A8AF1F64F9887"

REASON_PINS = {
    "placeholder_dummy_not_a_translatable_display_message": {
        "count": 487,
        "ids_sha256": "D6FAE539084F18B326BB8C065FD30E815F833CBFE2CA35472D8B422C3E2B3105",
    },
    "romanized_or_phonetic_lookup_key": {
        "count": 13,
        "ids_sha256": "0A2C1F18B63C69B9EBEDA3B414E4BD443E2D84406F11E32E31929CE7E1EA405F",
    },
}
OFFICIAL_ROWSET_SHA256 = {
    "SC": "66554207B59BDB338A81F23265783EFB83765323FAD962FD3A6BD1D0ACE9E78B",
    "JP": "EC2BBDE656B94A5723C5C41DE6E6CAF0DA97252CAF8C50128D64A9047EAA12C9",
    "EN": "632F22DFDE4EC3664895CC64A911638A1891291188D8CCC52F43A9C381C00077",
    "TC": "0A4B24F06FE70827FA6AB3623EF48DE0365EC1A3C0155D65976B19CA4711531B",
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_b07_claims(repo_root: Path) -> tuple[bytes, list[int]]:
    path = repo_root / B07_OVERLAY_PATH
    blob = path.read_bytes()
    if sha256(blob) != EXPECTED_B07_OVERLAY_SHA256:
        raise StructuralReviewError("B07 overlay changed")
    overlay = json.loads(blob.decode("utf-8"))
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if (
        resource != RESOURCE
        or len(ids) != previous.EXPECTED_REVIEW_COUNT
        or hash_json(ids) != previous.EXPECTED_REVIEW_IDS_SHA256
    ):
        raise StructuralReviewError("B07 explicit ownership set changed")
    return blob, ids


def validate_scope(
    tables: dict[str, Any], targets: set[int], repo_root: Path
) -> tuple[list[int], dict[int, str], dict[str, tuple[int, ...]], set[int], bytes]:
    b07_blob, b07_ids = load_b07_claims(repo_root)
    b07_selected, reason_by_id, _groups, b06_claims = previous.validate_scope(tables, targets)
    if b07_ids != b07_selected:
        raise StructuralReviewError("B07 artifact and classified ownership differ")
    predecessor_claims = b06_claims | set(b07_ids)
    if (
        len(predecessor_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT
        or hash_json(sorted(predecessor_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256
    ):
        raise StructuralReviewError("predecessor target claim set changed")
    gap = sorted(targets - predecessor_claims)
    if len(gap) != EXPECTED_PRE_REVIEW_GAP_COUNT or hash_json(gap) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review structural gap changed")
    selected = gap[:EXPECTED_REVIEW_COUNT]
    if (
        len(selected) != EXPECTED_REVIEW_COUNT
        or (selected[0], selected[-1]) != (EXPECTED_FIRST_ID, EXPECTED_LAST_ID)
        or hash_json(selected) != EXPECTED_REVIEW_IDS_SHA256
    ):
        raise StructuralReviewError("second structural review page changed")
    selected_groups = {
        reason: tuple(entry_id for entry_id in selected if reason_by_id[entry_id] == reason)
        for reason in REASON_PINS
    }
    if sum(map(len, selected_groups.values())) != EXPECTED_REVIEW_COUNT:
        raise StructuralReviewError("unclassified or mixed narrative row in review page")
    for reason, pin in REASON_PINS.items():
        ids = selected_groups[reason]
        if len(ids) != pin["count"] or hash_json(list(ids)) != pin["ids_sha256"]:
            raise StructuralReviewError(f"review reason partition changed: {reason}")
    post_gap = gap[EXPECTED_REVIEW_COUNT:]
    if len(post_gap) != EXPECTED_POST_REVIEW_GAP_COUNT or hash_json(post_gap) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review structural gap changed")
    rowsets = {
        language: hash_json([
            {"id": entry_id, "utf16le_sha256": common.text_hash(table.texts[entry_id])}
            for entry_id in selected
        ])
        for language, table in tables.items()
    }
    if rowsets != OFFICIAL_ROWSET_SHA256:
        raise StructuralReviewError("official selected rowset changed")
    return selected, reason_by_id, selected_groups, predecessor_claims, b07_blob


def validate_preservation(selected: list[int], reason_by_id: dict[int, str], tables: dict[str, Any]) -> None:
    sc = tables["SC"].texts
    for entry_id in selected:
        source = sc[entry_id]
        reason = reason_by_id[entry_id]
        if "\x00" in source or sum(previous.previous.script_counts(source).values()):
            raise StructuralReviewError(f"source-free preservation failed at ID {entry_id}")
        if reason == "placeholder_dummy_not_a_translatable_display_message":
            valid = source.strip().lower() == "dummy"
        elif reason == "romanized_or_phonetic_lookup_key":
            valid = bool(re.fullmatch(r"[a-z0-9_]+", source.strip()))
        else:
            valid = False
        if not valid:
            raise StructuralReviewError(f"narrative or unsafe structural value mixed at ID {entry_id}")


def audit_progress(
    progress_path: Path,
    repo_root: Path,
    b07_blob: bytes,
    overlay_blob: bytes,
    targets: set[int],
    predecessor_claims: set[int],
    selected: set[int],
) -> dict[str, Any]:
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    rows = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1 or not isinstance(rows[0].get("overlay_globs"), list):
        raise StructuralReviewError("progress has no unique msgdata row")
    prefix = list(previous.EXPECTED_PREDECESSOR_PATHS)
    tail, _successors = previous.historical_registration_tail(
        rows[0]["overlay_globs"],
        prefix,
        [B07_OVERLAY_PATH, SELF_OVERLAY_PATH],
        8,
        repo_root,
    )
    if B07_OVERLAY_PATH in tail and (repo_root / B07_OVERLAY_PATH).read_bytes() != b07_blob:
        raise StructuralReviewError("registered B07 differs from explicit ownership artifact")
    if SELF_OVERLAY_PATH in tail and (repo_root / SELF_OVERLAY_PATH).read_bytes() != overlay_blob:
        raise StructuralReviewError("registered B08 differs from deterministic output")
    gap = targets - predecessor_claims
    post_gap = gap - selected
    if len(gap) != EXPECTED_PRE_REVIEW_GAP_COUNT or hash_json(sorted(gap)) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    if selected & predecessor_claims or selected - gap:
        raise StructuralReviewError("B08 overlaps predecessors or target scope")
    if len(post_gap) != EXPECTED_POST_REVIEW_GAP_COUNT or hash_json(sorted(post_gap)) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    return {
        "pre_b07_registration_count": len(prefix),
        "b07_explicit_ownership_count": 500,
        "b07_registration_count": tail.count(B07_OVERLAY_PATH),
        "self_registration_count": tail.count(SELF_OVERLAY_PATH),
        "predecessor_target_count": len(predecessor_claims),
        "predecessor_target_ids_sha256": EXPECTED_PREDECESSOR_TARGET_IDS_SHA256,
        "pre_review_gap_count": len(gap),
        "pre_review_gap_ids_sha256": EXPECTED_PRE_REVIEW_GAP_IDS_SHA256,
        "post_review_gap_count": len(post_gap),
        "post_review_gap_ids_sha256": EXPECTED_POST_REVIEW_GAP_IDS_SHA256,
    }


def make_files(game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path) -> dict[str, bytes]:
    packed_sc, tables = previous.load_tables(game_root)
    targets = previous.previous.load_target_catalog(target_catalog_path)["ids"]
    selected, reason_by_id, groups, predecessor_claims, b07_blob = validate_scope(tables, targets, repo_root)
    validate_preservation(selected, reason_by_id, tables)
    sc = tables["SC"].texts
    entries = [
        {"id": entry_id, "source_sc_utf16le_sha256": common.text_hash(sc[entry_id]), "ko": sc[entry_id], "status": "reviewed"}
        for entry_id in selected
    ]
    pin = previous.previous.OFFICIAL_PINS["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {
            "size": pin["size"], "packed_sha256": pin["sha256"], "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"], "string_count": previous.previous.STRING_COUNT,
        },
        "defaults": {"status": "reviewed"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)
    overlay_blob = encode_json(overlay)
    audit = audit_progress(progress_path, repo_root, b07_blob, overlay_blob, targets, predecessor_claims, set(selected))
    audit["b07_registration_count"] = 0
    audit["self_registration_count"] = 0
    reason_summary = {reason: {"count": len(ids), "ids_sha256": REASON_PINS[reason]["ids_sha256"]} for reason, ids in groups.items()}
    evidence = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-evidence.v1", "batch_id": BATCH_ID,
        "resource": RESOURCE, "entry_count": len(entries), "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "selection": {"first_id": selected[0], "last_id": selected[-1], "reviewed_count": len(selected),
            "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256, "structural_before": EXPECTED_PRE_REVIEW_GAP_COUNT,
            "structural_after": EXPECTED_POST_REVIEW_GAP_COUNT, "narrative_mixed_count": 0, "blocked_count": 0},
        "reason_summary": reason_summary, "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256,
        "progress_audit": audit,
        "entries": [{"id": entry_id, "reason": reason_by_id[entry_id],
            "sc_utf16le_sha256": common.text_hash(sc[entry_id]), "replacement_utf16le_sha256": common.text_hash(sc[entry_id]),
            "exact_byte_preserved": True, "runtime_screen_reviewed": False} for entry_id in selected],
    }
    review = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-index.v1", "batch_id": BATCH_ID, "resource": RESOURCE,
        "reviewed_count": len(entries), "exact_byte_preserve_count": len(entries), "translated_narrative_count": 0,
        "blocked_count": 0, "runtime_screen_reviewed_count": 0, "reason_summary": reason_summary,
        "entries": [{"id": entry_id, "reason": reason_by_id[entry_id], "status": "reviewed"} for entry_id in selected],
    }
    first = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    second = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    if first != second:
        raise StructuralReviewError("target reconstruction is not deterministic")
    blobs = {f"public/{OVERLAY_NAME}": encode_json(overlay), f"evidence/{EVIDENCE_NAME}": encode_json(evidence), f"review/{REVIEW_NAME}": encode_json(review)}
    for relative, blob in blobs.items():
        if "\x00" in blob.decode("utf-8") or sum(previous.previous.script_counts(blob.decode("utf-8")).values()):
            raise StructuralReviewError(f"public artifact is not source-free: {relative}")
    artifacts = {relative: {"path": relative, "size": len(blob), "sha256": sha256(blob)} for relative, blob in blobs.items()}
    validation = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-validation.v1", "batch_id": BATCH_ID, "resource": RESOURCE,
        "passed": True, "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {"reviewed_count": 500, "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256,
            "exact_byte_preserve_count": 500, "translated_narrative_count": 0, "narrative_mixed_count": 0,
            "blocked_count": 0, "duplicate_id_count": 0, "predecessor_overlap_count": 0,
            "post_review_structural_remaining": EXPECTED_POST_REVIEW_GAP_COUNT},
        "reason_summary": reason_summary, "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256,
        "progress_audit": audit,
        "replacement_invariants": {"checked": 500, "exact_utf16le_byte_preserve_count": 500,
            "printf_preserved": True, "esc_preserved": True, "pua_preserved": True, "line_breaks_preserved": True, "failures": 0},
        "source_free_scan": {relative: {**previous.previous.script_counts(blob.decode("utf-8")), "embedded_nul_count": blob.count(b"\x00")} for relative, blob in blobs.items()},
        "target_reconstruction": first, "reproducibility": {"in_memory_target_a_b_equal": True, "artifact_json_canonical": True},
        "artifacts": artifacts,
        "safety": {"commercial_source_text_included": False, "complete_game_resource_included": False,
            "global_progress_modified": False, "global_readme_modified": False, "installed_game_files_modified": False,
            "deployment_performed": False, "commit_or_push_performed": False},
    }
    blobs[VALIDATION_NAME] = encode_json(validation)
    if sum(previous.previous.script_counts(blobs[VALIDATION_NAME].decode("utf-8")).values()) or b"\x00" in blobs[VALIDATION_NAME]:
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
    return {"reviewed_count": 500, "preserve_count": 500, "blocked_count": 0, "remaining_count": 3110, "files": first}


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
