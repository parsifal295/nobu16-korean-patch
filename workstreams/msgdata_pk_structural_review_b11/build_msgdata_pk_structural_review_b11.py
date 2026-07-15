#!/usr/bin/env python3
"""Review and byte-preserve the fifth 500-row PK msgdata structural page."""

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
B10_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_structural_review_b10"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


previous = load_module(
    "nobu16_msgdata_pk_structural_review_b11_previous",
    B10_ROOT / "build_msgdata_pk_structural_review_b10.py",
)
common = previous.common
engine = previous.engine
StructuralReviewError = previous.StructuralReviewError

BATCH_ID = "msgdata-pk-structural-review-b11-500.v1"
RESOURCE = previous.RESOURCE
OVERLAY_NAME = "msgdata_ko_pk_structural_review_b11_500.v1.json"
EVIDENCE_NAME = "msgdata_pk_structural_review_b11_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_structural_review_b11_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgdata_pk_structural_review_b11/public/{OVERLAY_NAME}"
OWNER_PATHS = (
    previous.B07_OVERLAY_PATH,
    previous.B08_OVERLAY_PATH,
    previous.B09_OVERLAY_PATH,
    previous.SELF_OVERLAY_PATH,
)
TARGET_CATALOG_RELATIVE = previous.TARGET_CATALOG_RELATIVE
PROGRESS_RELATIVE = previous.PROGRESS_RELATIVE

EXPECTED_B10_OVERLAY_SHA256 = "34F47ED438AFF11D37BD5D60DC42BBD9EA7AD42CC5691098F48FC15DB6B6C23D"
EXPECTED_PREDECESSOR_TARGET_COUNT = 23_424
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = "1043EE00D4AA82897ADF1D92FAE8563DC9585DD804DCA88F15BF26AF3EA72A93"
EXPECTED_PRE_REVIEW_GAP_COUNT = 2_110
EXPECTED_PRE_REVIEW_GAP_IDS_SHA256 = previous.EXPECTED_POST_REVIEW_GAP_IDS_SHA256
EXPECTED_REVIEW_COUNT = 500
EXPECTED_FIRST_ID = 24_744
EXPECTED_LAST_ID = 26_886
EXPECTED_REVIEW_IDS_SHA256 = "8FA21BEF915AAE152DBE66166D462A5576E906C4B75CC6BD27F9C5F9E7FCC2CF"
EXPECTED_POST_REVIEW_GAP_COUNT = 1_610
EXPECTED_POST_REVIEW_GAP_IDS_SHA256 = "F64C74B50B40FE5FBF7FD1D66E51F0023D0B9A3888484E96310FC0BFC157C566"
REASON_PINS = {
    "format_or_control_only_token": {"count": 1, "ids_sha256": "FCCCD607EB8FE9927F4C47E8A74B1E2E7B68BBAA6CFECD4F73C11CDCA3D7967D"},
    "placeholder_dummy_not_a_translatable_display_message": {"count": 38, "ids_sha256": "DBB528C2A57229244553C87B776EC4156A81E5B78E2A4A1937A9F5FC91AC79A5"},
    "romanized_or_phonetic_lookup_key": {"count": 461, "ids_sha256": "9772D6F12A4B9F87171916027692AFCACDD61C4759888C604181A8B988EA417D"},
}
OFFICIAL_ROWSET_SHA256 = {
    "SC": "7BFA0B3235D2A9BC0AA1A492A090CFA31AA90D51C538FA4D256008A2FA86C916",
    "JP": "2744CD2F1FCC4E2CE7EACB858BBB5C9713B185FFA4FC8F752C2DFBB4C3440480",
    "EN": "5180E431BF53D1C75ED84359BB16E9835B66AF4EBBD488BF5A2B78697B09D8AD",
    "TC": "3452836088E7FEF409DF126C847DF881651B4580DE7E57DF53C17AFD40972887",
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_b10_owner(repo_root: Path) -> tuple[bytes, list[int]]:
    blob = (repo_root / previous.SELF_OVERLAY_PATH).read_bytes()
    if sha256(blob) != EXPECTED_B10_OVERLAY_SHA256:
        raise StructuralReviewError("B10 explicit predecessor changed")
    overlay = json.loads(blob.decode("utf-8"))
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if resource != RESOURCE or len(ids) != 500 or hash_json(ids) != previous.EXPECTED_REVIEW_IDS_SHA256:
        raise StructuralReviewError("B10 explicit ownership set changed")
    return blob, ids


def validate_scope(
    tables: dict[str, Any], targets: set[int], repo_root: Path,
) -> tuple[list[int], dict[int, str], dict[str, tuple[int, ...]], set[int], dict[str, bytes]]:
    b10_selected, reason_by_id, _groups, pre_b10_claims, owner_blobs = previous.validate_scope(tables, targets, repo_root)
    b10_blob, b10_ids = load_b10_owner(repo_root)
    if b10_ids != b10_selected:
        raise StructuralReviewError("B10 artifact and classified ownership differ")
    owner_blobs = dict(owner_blobs)
    owner_blobs[previous.SELF_OVERLAY_PATH] = b10_blob
    predecessor_claims = pre_b10_claims | set(b10_ids)
    if len(predecessor_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT or hash_json(sorted(predecessor_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256:
        raise StructuralReviewError("predecessor target claim set changed")
    gap = sorted(targets - predecessor_claims)
    if len(gap) != EXPECTED_PRE_REVIEW_GAP_COUNT or hash_json(gap) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    selected = gap[:EXPECTED_REVIEW_COUNT]
    if len(selected) != 500 or (selected[0], selected[-1]) != (EXPECTED_FIRST_ID, EXPECTED_LAST_ID) or hash_json(selected) != EXPECTED_REVIEW_IDS_SHA256:
        raise StructuralReviewError("fifth structural review page changed")
    groups = {reason: tuple(entry_id for entry_id in selected if reason_by_id.get(entry_id) == reason) for reason in REASON_PINS}
    if sum(map(len, groups.values())) != 500:
        raise StructuralReviewError("mixed narrative or unclassified review row")
    for reason, pin in REASON_PINS.items():
        if len(groups[reason]) != pin["count"] or hash_json(list(groups[reason])) != pin["ids_sha256"]:
            raise StructuralReviewError(f"reason partition changed: {reason}")
    post_gap = gap[500:]
    if len(post_gap) != EXPECTED_POST_REVIEW_GAP_COUNT or hash_json(post_gap) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    rowsets = {language: hash_json([{"id": entry_id, "utf16le_sha256": common.text_hash(table.texts[entry_id])} for entry_id in selected]) for language, table in tables.items()}
    if rowsets != OFFICIAL_ROWSET_SHA256:
        raise StructuralReviewError("official selected rowset changed")
    script_counts = previous.previous.previous.previous.previous.script_counts
    for entry_id in selected:
        source = tables["SC"].texts[entry_id]
        reason = reason_by_id[entry_id]
        if "\x00" in source or sum(script_counts(source).values()):
            raise StructuralReviewError(f"source script mixed at ID {entry_id}")
        valid = (
            source.strip().lower() == "dummy" if reason == "placeholder_dummy_not_a_translatable_display_message"
            else bool(re.fullmatch(r"[A-Za-z0-9_%+_.-]+", source.strip())) if reason == "romanized_or_phonetic_lookup_key"
            else not engine.has_semantic_alphanumeric(source) if reason == "format_or_control_only_token"
            else False
        )
        if not valid:
            raise StructuralReviewError(f"unsafe or narrative value at ID {entry_id}")
    return selected, reason_by_id, groups, predecessor_claims, owner_blobs


def audit_progress(
    progress_path: Path, repo_root: Path, owner_blobs: dict[str, bytes], overlay_blob: bytes,
    targets: set[int], predecessor_claims: set[int], selected: set[int],
) -> dict[str, Any]:
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    rows = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1 or not isinstance(rows[0].get("overlay_globs"), list):
        raise StructuralReviewError("progress has no unique msgdata row")
    prefix = list(previous.previous.previous.previous.EXPECTED_PREDECESSOR_PATHS)
    patterns = rows[0]["overlay_globs"]
    if patterns[:len(prefix)] != prefix:
        raise StructuralReviewError("pre-B07 registration order changed")
    chain = list(OWNER_PATHS) + [SELF_OVERLAY_PATH]
    tail = patterns[len(prefix):]
    if tail not in [chain[:index] for index in range(len(chain) + 1)]:
        raise StructuralReviewError("unexpected structural registration order or duplicate")
    for path, blob in owner_blobs.items():
        if path in tail and (repo_root / path).read_bytes() != blob:
            raise StructuralReviewError(f"registered predecessor differs: {path}")
    if SELF_OVERLAY_PATH in tail and (repo_root / SELF_OVERLAY_PATH).read_bytes() != overlay_blob:
        raise StructuralReviewError("registered B11 differs from deterministic output")
    gap = targets - predecessor_claims
    post_gap = gap - selected
    if len(gap) != 2110 or hash_json(sorted(gap)) != EXPECTED_PRE_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    if selected & predecessor_claims or selected - gap:
        raise StructuralReviewError("B11 overlaps predecessor or target scope")
    if len(post_gap) != 1610 or hash_json(sorted(post_gap)) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    return {
        "pre_b07_registration_count": len(prefix), "explicit_structural_predecessor_count": 2000,
        "predecessor_registration_counts": {path: tail.count(path) for path in OWNER_PATHS},
        "self_registration_count": tail.count(SELF_OVERLAY_PATH),
        "predecessor_target_count": len(predecessor_claims), "predecessor_target_ids_sha256": EXPECTED_PREDECESSOR_TARGET_IDS_SHA256,
        "pre_review_gap_count": len(gap), "pre_review_gap_ids_sha256": EXPECTED_PRE_REVIEW_GAP_IDS_SHA256,
        "post_review_gap_count": len(post_gap), "post_review_gap_ids_sha256": EXPECTED_POST_REVIEW_GAP_IDS_SHA256,
    }


def make_files(game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path) -> dict[str, bytes]:
    packed_sc, tables = previous.previous.previous.previous.load_tables(game_root)
    targets = previous.previous.previous.previous.previous.load_target_catalog(target_catalog_path)["ids"]
    selected, reason_by_id, groups, predecessor_claims, owner_blobs = validate_scope(tables, targets, repo_root)
    sc = tables["SC"].texts
    entries = [{"id": entry_id, "source_sc_utf16le_sha256": common.text_hash(sc[entry_id]), "ko": sc[entry_id], "status": "reviewed"} for entry_id in selected]
    pin = previous.previous.previous.previous.previous.OFFICIAL_PINS["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA, "overlay_id": BATCH_ID, "resource": RESOURCE, "base_language": "SC", "entry_count": 500,
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {"size": pin["size"], "packed_sha256": pin["sha256"], "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"], "string_count": previous.previous.previous.previous.previous.STRING_COUNT},
        "defaults": {"status": "reviewed"}, "entries": entries,
    }
    common.validate_overlay_shape(overlay)
    overlay_blob = encode_json(overlay)
    audit = audit_progress(progress_path, repo_root, owner_blobs, overlay_blob, targets, predecessor_claims, set(selected))
    reason_summary = {reason: {"count": len(ids), "ids_sha256": REASON_PINS[reason]["ids_sha256"]} for reason, ids in groups.items()}
    evidence = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-evidence.v1", "batch_id": BATCH_ID, "resource": RESOURCE,
        "entry_count": 500, "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "selection": {"first_id": selected[0], "last_id": selected[-1], "reviewed_count": 500,
            "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256, "structural_before": 2110, "structural_after": 1610,
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
        "entries": [{"id": entry_id, "reason": reason_by_id[entry_id], "status": "reviewed"} for entry_id in selected],
    }
    first = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    second = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    if first != second:
        raise StructuralReviewError("target reconstruction is not deterministic")
    blobs = {f"public/{OVERLAY_NAME}": encode_json(overlay), f"evidence/{EVIDENCE_NAME}": encode_json(evidence), f"review/{REVIEW_NAME}": encode_json(review)}
    script_counts = previous.previous.previous.previous.previous.script_counts
    for relative, blob in blobs.items():
        if "\x00" in blob.decode("utf-8") or sum(script_counts(blob.decode("utf-8")).values()):
            raise StructuralReviewError(f"public artifact is not source-free: {relative}")
    artifacts = {relative: {"path": relative, "size": len(blob), "sha256": sha256(blob)} for relative, blob in blobs.items()}
    validation = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-validation.v1", "batch_id": BATCH_ID, "resource": RESOURCE, "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {"reviewed_count": 500, "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256, "exact_byte_preserve_count": 500,
            "translated_narrative_count": 0, "narrative_mixed_count": 0, "blocked_count": 0, "duplicate_id_count": 0,
            "predecessor_overlap_count": 0, "post_review_structural_remaining": 1610},
        "reason_summary": reason_summary, "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256, "progress_audit": audit,
        "replacement_invariants": {"checked": 500, "exact_utf16le_byte_preserve_count": 500, "printf_preserved": True,
            "esc_preserved": True, "pua_preserved": True, "line_breaks_preserved": True, "failures": 0},
        "source_free_scan": {relative: {**script_counts(blob.decode("utf-8")), "embedded_nul_count": blob.count(b"\x00")} for relative, blob in blobs.items()},
        "target_reconstruction": first, "reproducibility": {"in_memory_target_a_b_equal": True, "artifact_json_canonical": True},
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
    return {"reviewed_count": 500, "preserve_count": 500, "blocked_count": 0, "remaining_count": 1610, "files": first}


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
