#!/usr/bin/env python3
"""Review and byte-preserve the first 500 remaining PK msgdata structural rows."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
BATCH06_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_native_batch06"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


previous = load_module(
    "nobu16_msgdata_pk_structural_review_b07_previous",
    BATCH06_ROOT / "build_msgdata_pk_native_batch06.py",
)
engine = previous.engine
common = previous.common
StructuralReviewError = previous.BatchError

BATCH_ID = "msgdata-pk-structural-review-b07-500.v1"
RESOURCE = previous.RESOURCE
OVERLAY_NAME = "msgdata_ko_pk_structural_review_b07_500.v1.json"
EVIDENCE_NAME = "msgdata_pk_structural_review_b07_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_structural_review_b07_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgdata_pk_structural_review_b07/public/{OVERLAY_NAME}"
TARGET_CATALOG_RELATIVE = previous.TARGET_CATALOG_RELATIVE
PROGRESS_RELATIVE = previous.PROGRESS_RELATIVE

EXPECTED_PREDECESSOR_PATHS = tuple(row[0] for row in previous.OWNER_OVERLAYS) + (
    previous.SELF_OVERLAY_LOGICAL_PATH,
)
EXPECTED_BATCH06_OVERLAY_SHA256 = "53A64CC10C28D48A829F984FEAB3D3F3A27318C2E5A3EE814DF39380EF8DF181"
EXPECTED_PREDECESSOR_TARGET_COUNT = 21_424
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = "8E9E4A718351EA535E82E497F9383FA859B12FE2342411C53D96F0399A3D01E7"
EXPECTED_STRUCTURAL_COUNT = 4_110
EXPECTED_STRUCTURAL_IDS_SHA256 = "83756A7BE8E0E324EF0FC4B0513E7410CF27A3156C0F0084F8E7A2F93A7DE6EA"
EXPECTED_REVIEW_COUNT = 500
EXPECTED_FIRST_ID = 6_651
EXPECTED_LAST_ID = 19_198
EXPECTED_REVIEW_IDS_SHA256 = "3C1218B128933A7A325F0B1FC3B8715D7EC7744E7CBF77549AA690759B57E579"
EXPECTED_POST_REVIEW_GAP_COUNT = 3_610
EXPECTED_POST_REVIEW_GAP_IDS_SHA256 = "00CCD5BF47F9867BA8825CDD985E628F96EDB5F1F861750020FB0756EF2217A4"

REASON_PINS = {
    "format_or_control_only_token": {
        "count": 3,
        "ids_sha256": "2197DEADFACAF112C4C21F4DF099657AFA60E228FBDE885385F7E96B9236856F",
    },
    "placeholder_dummy_not_a_translatable_display_message": {
        "count": 439,
        "ids_sha256": "2B138214DF9DDCAEE1F3D7666AA4A920008986A334829F679896C7DEA6431FBD",
    },
    "romanized_or_phonetic_lookup_key": {
        "count": 58,
        "ids_sha256": "63495DAA681EC540F365FF950A14DF7C4383EDC45893229631763D5FFD842DE6",
    },
}
OFFICIAL_ROWSET_SHA256 = {
    "SC": "3727D8D470DD83AA8C98748418412857D84536C8F03F8BA25A06C09CE3868E30",
    "JP": "40408AA9361634F3A034276B0CCDFC42D67326B300D271984764C173CE3AE68B",
    "EN": "47EFE2D10B7180118FCB4BDADFC9B98F8BCBE4ED74A57E6904DB0A3ECB08ABAE",
    "TC": "BDB454EDE686185D6A9B8AE3EDFBDC04971D032C3D11C282E7A37CE8E6E188D5",
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


STRUCTURAL_REGISTRATION_RE = re.compile(
    r"workstreams/msgdata_pk_structural_review_b(\d{2})/public/"
    r"msgdata_ko_pk_structural_review_b\1_(500|final_110)\.v1\.json"
)


def historical_registration_tail(
    patterns: list[str],
    prefix: list[str],
    chain_through_self: list[str],
    current_batch: int,
    repo_root: Path,
) -> tuple[list[str], list[str]]:
    """Return this batch's historical tail while validating later registrations.

    A completed batch must rebuild identically after sequential successor
    batches are added to the shared progress catalog.  Successors are audited
    as ordered, existing structural-review paths, but are excluded from the
    historical evidence generated for this batch.
    """

    if patterns[: len(prefix)] != prefix:
        raise StructuralReviewError("pre-B07 registration order changed")
    tail = patterns[len(prefix) :]
    historical = tail[: min(len(tail), len(chain_through_self))]
    if historical not in [
        chain_through_self[:index] for index in range(len(chain_through_self) + 1)
    ]:
        raise StructuralReviewError("unexpected structural registration order or duplicate")
    successors = tail[len(historical) :]
    if historical != chain_through_self and successors:
        raise StructuralReviewError("structural successor registered before this batch")
    expected_batch = current_batch + 1
    for logical_path in successors:
        match = STRUCTURAL_REGISTRATION_RE.fullmatch(logical_path)
        if match is None or int(match.group(1)) != expected_batch:
            raise StructuralReviewError("structural successor order is not contiguous")
        expected_suffix = "final_110" if expected_batch == 15 else "500"
        if match.group(2) != expected_suffix:
            raise StructuralReviewError("structural successor filename does not match its batch")
        if not (repo_root / logical_path).is_file():
            raise StructuralReviewError("registered structural successor is missing")
        expected_batch += 1
    return historical, successors


def resolve_stock_sc(game_root: Path) -> Path:
    candidates = (
        game_root / previous.STOCK_SC_RELATIVE,
        game_root / "KR_PATCH_BACKUP/file_only_transaction/pk-full-messages-seoulhangang-v1/originals/MSG_PK/SC/msgdata.bin",
    )
    expected = previous.OFFICIAL_PINS["SC"]["sha256"]
    for path in candidates:
        if path.is_file() and sha256(path.read_bytes()) == expected:
            return path
    raise StructuralReviewError("pinned pristine PK SC msgdata is unavailable")


def load_tables(game_root: Path) -> tuple[bytes, dict[str, Any]]:
    sc_path = resolve_stock_sc(game_root)
    paths = {
        "SC": sc_path,
        "JP": game_root / "MSG_PK/JP/msgdata.bin",
        "EN": game_root / "MSG_PK/EN/msgdata.bin",
        "TC": game_root / "MSG_PK/TC/msgdata.bin",
    }
    packed_sc, _raw_sc, sc_table = previous.load_pinned_table(
        sc_path, previous.OFFICIAL_PINS["SC"], "SC"
    )
    tables = {"SC": sc_table}
    for language in ("JP", "EN", "TC"):
        tables[language] = previous.load_pinned_table(
            paths[language], previous.OFFICIAL_PINS[language], language
        )[2]
    return packed_sc, tables


def validate_scope(
    tables: dict[str, Any], targets: set[int]
) -> tuple[list[int], dict[int, str], dict[str, tuple[int, ...]], set[int]]:
    owner = previous.load_owner_catalog()
    predecessor_claims = (owner["ids"] | set(previous.SELECTED_IDS)) & targets
    if (
        len(predecessor_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT
        or hash_json(sorted(predecessor_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256
    ):
        raise StructuralReviewError("predecessor target claim set changed")
    groups = previous.classify_structural_prefix(tables, targets, owner["ids"])
    reason_by_id = {entry_id: reason for reason, ids in groups.items() for entry_id in ids}
    structural_ids = sorted(reason_by_id)
    if (
        len(structural_ids) != EXPECTED_STRUCTURAL_COUNT
        or hash_json(structural_ids) != EXPECTED_STRUCTURAL_IDS_SHA256
        or structural_ids != sorted(targets - predecessor_claims)
    ):
        raise StructuralReviewError("remaining structural catalog changed")
    selected = structural_ids[:EXPECTED_REVIEW_COUNT]
    if (
        len(selected) != EXPECTED_REVIEW_COUNT
        or (selected[0], selected[-1]) != (EXPECTED_FIRST_ID, EXPECTED_LAST_ID)
        or hash_json(selected) != EXPECTED_REVIEW_IDS_SHA256
    ):
        raise StructuralReviewError("first structural review page changed")
    selected_groups = {
        reason: tuple(entry_id for entry_id in selected if reason_by_id[entry_id] == reason)
        for reason in sorted(groups)
    }
    for reason, pin in REASON_PINS.items():
        ids = selected_groups[reason]
        if len(ids) != pin["count"] or hash_json(list(ids)) != pin["ids_sha256"]:
            raise StructuralReviewError(f"review reason partition changed: {reason}")
    post_gap = structural_ids[EXPECTED_REVIEW_COUNT:]
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
    return selected, reason_by_id, selected_groups, predecessor_claims


def validate_preservation(
    selected: list[int], reason_by_id: dict[int, str], tables: dict[str, Any]
) -> None:
    sc = tables["SC"].texts
    for entry_id in selected:
        source = sc[entry_id]
        preserved = source
        reason = reason_by_id[entry_id]
        if "\x00" in source or sum(previous.script_counts(source).values()):
            raise StructuralReviewError(f"source-free byte preservation failed at ID {entry_id}")
        if reason == "placeholder_dummy_not_a_translatable_display_message":
            valid = source.strip().lower() == "dummy"
        elif reason == "romanized_or_phonetic_lookup_key":
            valid = bool(re.fullmatch(r"[a-z0-9_]+", source.strip()))
        elif reason == "format_or_control_only_token":
            valid = not engine.has_semantic_alphanumeric(source)
        else:
            valid = False
        if not valid:
            raise StructuralReviewError(f"narrative or unsafe structural value mixed at ID {entry_id}")
        if preserved.encode("utf-16le") != source.encode("utf-16le"):
            raise StructuralReviewError(f"byte preservation failed at ID {entry_id}")


def make_models(
    packed_sc: bytes, tables: dict[str, Any], targets: set[int], progress_path: Path, repo_root: Path
) -> dict[str, Any]:
    selected, reason_by_id, selected_groups, predecessor_claims = validate_scope(tables, targets)
    validate_preservation(selected, reason_by_id, tables)
    sc = tables["SC"].texts
    entries = [
        {
            "id": entry_id,
            "source_sc_utf16le_sha256": common.text_hash(sc[entry_id]),
            "ko": sc[entry_id],
            "status": "reviewed",
        }
        for entry_id in selected
    ]
    pin = previous.OFFICIAL_PINS["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": pin["size"],
            "packed_sha256": pin["sha256"],
            "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"],
            "string_count": previous.STRING_COUNT,
        },
        "defaults": {"status": "reviewed"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)
    overlay_blob = encode_json(overlay)
    progress_audit = audit_progress(progress_path, repo_root, overlay_blob, targets, predecessor_claims, set(selected))
    # Registration timing is diagnostic state, not part of the immutable B07
    # artifact. Preserve the original pre-registration evidence while the
    # live catalog has already been validated above.
    progress_audit["self_registration_count"] = 0
    reason_summary = {
        reason: {"count": len(ids), "ids_sha256": REASON_PINS[reason]["ids_sha256"]}
        for reason, ids in selected_groups.items()
    }
    evidence = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "entry_count": len(selected),
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "selection": {
            "first_id": selected[0],
            "last_id": selected[-1],
            "reviewed_count": len(selected),
            "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256,
            "structural_before": EXPECTED_STRUCTURAL_COUNT,
            "structural_after": EXPECTED_POST_REVIEW_GAP_COUNT,
            "narrative_mixed_count": 0,
            "blocked_count": 0,
        },
        "reason_summary": reason_summary,
        "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256,
        "progress_audit": progress_audit,
        "entries": [
            {
                "id": entry_id,
                "reason": reason_by_id[entry_id],
                "sc_utf16le_sha256": common.text_hash(sc[entry_id]),
                "replacement_utf16le_sha256": common.text_hash(sc[entry_id]),
                "exact_byte_preserved": True,
                "runtime_screen_reviewed": False,
            }
            for entry_id in selected
        ],
    }
    review = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-index.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "reviewed_count": len(selected),
        "exact_byte_preserve_count": len(selected),
        "translated_narrative_count": 0,
        "blocked_count": 0,
        "runtime_screen_reviewed_count": 0,
        "reason_summary": reason_summary,
        "entries": [
            {"id": entry_id, "reason": reason_by_id[entry_id], "status": "reviewed"}
            for entry_id in selected
        ],
    }
    first = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    second = engine.upstream.reconstruct_sc_target(packed_sc, tables["SC"], entries)
    if first != second:
        raise StructuralReviewError("target reconstruction is not deterministic")
    return {
        "overlay": overlay,
        "evidence": evidence,
        "review": review,
        "progress_audit": progress_audit,
        "reason_summary": reason_summary,
        "target_reconstruction": first,
    }


def audit_progress(
    progress_path: Path,
    repo_root: Path,
    overlay_blob: bytes,
    targets: set[int],
    predecessor_claims: set[int],
    selected: set[int],
) -> dict[str, Any]:
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    rows = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1 or not isinstance(rows[0].get("overlay_globs"), list):
        raise StructuralReviewError("progress has no unique msgdata row")
    patterns = rows[0]["overlay_globs"]
    tail, _successors = historical_registration_tail(
        patterns,
        list(EXPECTED_PREDECESSOR_PATHS),
        [SELF_OVERLAY_PATH],
        7,
        repo_root,
    )
    if patterns.count(previous.SELF_OVERLAY_LOGICAL_PATH) != 1:
        raise StructuralReviewError("batch06 must be registered exactly once")
    batch06_path = repo_root / previous.SELF_OVERLAY_LOGICAL_PATH
    if sha256(batch06_path.read_bytes()) != EXPECTED_BATCH06_OVERLAY_SHA256:
        raise StructuralReviewError("batch06 registered overlay changed")
    self_count = tail.count(SELF_OVERLAY_PATH)
    if self_count and (repo_root / SELF_OVERLAY_PATH).read_bytes() != overlay_blob:
        raise StructuralReviewError("registered self overlay differs from deterministic output")
    gap = targets - predecessor_claims
    if len(gap) != EXPECTED_STRUCTURAL_COUNT or hash_json(sorted(gap)) != EXPECTED_STRUCTURAL_IDS_SHA256:
        raise StructuralReviewError("pre-review gap changed")
    if selected & predecessor_claims or selected - gap:
        raise StructuralReviewError("structural review overlaps predecessors or leaves target scope")
    post_gap = gap - selected
    if len(post_gap) != EXPECTED_POST_REVIEW_GAP_COUNT or hash_json(sorted(post_gap)) != EXPECTED_POST_REVIEW_GAP_IDS_SHA256:
        raise StructuralReviewError("post-review gap changed")
    return {
        "predecessor_registration_count": len(EXPECTED_PREDECESSOR_PATHS),
        "batch06_registered_exactly_once": True,
        "self_registration_count": self_count,
        "predecessor_target_count": len(predecessor_claims),
        "predecessor_target_ids_sha256": EXPECTED_PREDECESSOR_TARGET_IDS_SHA256,
        "pre_review_gap_count": len(gap),
        "pre_review_gap_ids_sha256": EXPECTED_STRUCTURAL_IDS_SHA256,
        "post_review_gap_count": len(post_gap),
        "post_review_gap_ids_sha256": EXPECTED_POST_REVIEW_GAP_IDS_SHA256,
    }


def make_files(
    game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path
) -> dict[str, bytes]:
    packed_sc, tables = load_tables(game_root)
    targets = previous.load_target_catalog(target_catalog_path)["ids"]
    models = make_models(packed_sc, tables, targets, progress_path, repo_root)
    blobs = {
        f"public/{OVERLAY_NAME}": encode_json(models["overlay"]),
        f"evidence/{EVIDENCE_NAME}": encode_json(models["evidence"]),
        f"review/{REVIEW_NAME}": encode_json(models["review"]),
    }
    for relative, blob in blobs.items():
        text = blob.decode("utf-8")
        if "\x00" in text or sum(previous.script_counts(text).values()):
            raise StructuralReviewError(f"public artifact is not source-free: {relative}")
    artifacts = {
        relative: {"path": relative, "size": len(blob), "sha256": sha256(blob)}
        for relative, blob in blobs.items()
    }
    validation = {
        "schema": "nobu16.kr.msgdata-pk-structural-review-validation.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {
            "reviewed_count": EXPECTED_REVIEW_COUNT,
            "reviewed_ids_sha256": EXPECTED_REVIEW_IDS_SHA256,
            "exact_byte_preserve_count": EXPECTED_REVIEW_COUNT,
            "translated_narrative_count": 0,
            "narrative_mixed_count": 0,
            "blocked_count": 0,
            "duplicate_id_count": 0,
            "predecessor_overlap_count": 0,
            "post_review_structural_remaining": EXPECTED_POST_REVIEW_GAP_COUNT,
        },
        "reason_summary": models["reason_summary"],
        "official_selected_rowset_sha256": OFFICIAL_ROWSET_SHA256,
        "progress_audit": models["progress_audit"],
        "replacement_invariants": {
            "checked": EXPECTED_REVIEW_COUNT,
            "exact_utf16le_byte_preserve_count": EXPECTED_REVIEW_COUNT,
            "printf_preserved": True,
            "esc_preserved": True,
            "pua_preserved": True,
            "line_breaks_preserved": True,
            "failures": 0,
        },
        "source_free_scan": {
            relative: {**previous.script_counts(blob.decode("utf-8")), "embedded_nul_count": blob.count(b"\x00")}
            for relative, blob in blobs.items()
        },
        "target_reconstruction": models["target_reconstruction"],
        "reproducibility": {"in_memory_target_a_b_equal": True, "artifact_json_canonical": True},
        "artifacts": artifacts,
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "global_progress_modified": False,
            "global_readme_modified": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "commit_or_push_performed": False,
        },
    }
    blobs[VALIDATION_NAME] = encode_json(validation)
    if sum(previous.script_counts(blobs[VALIDATION_NAME].decode("utf-8")).values()) or b"\x00" in blobs[VALIDATION_NAME]:
        raise StructuralReviewError("validation artifact is not source-free")
    return blobs


def build_reproducibly(
    game_root: Path, repo_root: Path, target_catalog_path: Path, progress_path: Path, out_root: Path
) -> dict[str, Any]:
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
    return {
        "reviewed_count": EXPECTED_REVIEW_COUNT,
        "preserve_count": EXPECTED_REVIEW_COUNT,
        "blocked_count": 0,
        "remaining_count": EXPECTED_POST_REVIEW_GAP_COUNT,
        "files": first,
    }


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
    result = build_reproducibly(
        args.game_root.resolve(), args.repo_root.resolve(), args.target_catalog.resolve(),
        args.progress.resolve(), args.out_root.resolve(),
    )
    print(f"reviewed={result['reviewed_count']}")
    print(f"preserved={result['preserve_count']}")
    print(f"blocked={result['blocked_count']}")
    print(f"remaining={result['remaining_count']}")
    for relative, blob in result["files"].items():
        print(f"{relative}_sha256={sha256(blob)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
