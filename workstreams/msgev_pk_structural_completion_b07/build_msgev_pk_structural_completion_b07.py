#!/usr/bin/env python3
"""Complete the remaining PK msgev target catalog with reviewed structural rows.

The overlay preserves 219 structural values byte-for-byte and translates 22
dynamic narrative rows while retaining every runtime token and text invariant.
No official Chinese or Japanese source text is published.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
BATCH06_ROOT = REPO_ROOT / "workstreams" / "msgev_pk_native_batch06"
sys.path.insert(0, str(BATCH06_ROOT))

import build_msgev_pk_native_batch06 as previous  # noqa: E402


_SPEC = importlib.util.spec_from_file_location(
    "_nobu16_msgev_pk_structural_completion_b07_translations",
    WORKSTREAM_ROOT / "translations.py",
)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load structural completion translations")
_TRANSLATIONS_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_TRANSLATIONS_MODULE)
DYNAMIC_TRANSLATIONS = _TRANSLATIONS_MODULE.DYNAMIC_TRANSLATIONS

base = previous.base
common = previous.common
strict = previous.strict
StructuralCompletionError = previous.NativeBatchError

BATCH_ID = "msgev-pk-structural-completion-b07-241.v1"
RESOURCE = "MSG_PK/SC/msgev.bin"
OVERLAY_NAME = "msgev_ko_pk_structural_completion_b07_241.v1.json"
EVIDENCE_NAME = "msgev_pk_structural_completion_b07_evidence.v1.json"
REVIEW_NAME = "msgev_pk_structural_completion_b07_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = (
    f"workstreams/msgev_pk_structural_completion_b07/public/{OVERLAY_NAME}"
)
TARGET_CATALOG_RELATIVE = previous.TARGET_CATALOG_RELATIVE
PROGRESS_RELATIVE = previous.PROGRESS_RELATIVE

EXPECTED_IDS = previous.EXCLUDED_IDS
EXPECTED_COUNT = 241
EXPECTED_IDS_SHA256 = (
    "A58E26CCD1D7DD8F7505B0134FD3354E7001B6C91B27A1D7011EBAD29AA4D2B0"
)
DYNAMIC_IDS = sorted(DYNAMIC_TRANSLATIONS)
EXPECTED_DYNAMIC_COUNT = 22
EXPECTED_DYNAMIC_IDS_SHA256 = (
    "741250CAA54217231C57B21AC84F880092EA5E8503DF79439BFF12CDA90D97AA"
)
PRESERVE_IDS = sorted(set(EXPECTED_IDS) - set(DYNAMIC_IDS))
EXPECTED_PRESERVE_COUNT = 219
EXPECTED_PRESERVE_IDS_SHA256 = (
    "F93520945377A6B84E23974E8A1184815C1C74BDFBD61CEF7F14E0E8A5A26464"
)
EXPECTED_OVERLAY_SHA256 = (
    "4FB377A64306BCE929E22A4271E3AB95FEBF1A937B433C3807C4A9816440550F"
)

DYNAMIC_REASONS = frozenset(
    (
        "dynamic_substitution_token_manual_runtime_risk",
        "runtime_custom_bracket_substitution",
    )
)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def artifact(relative: str, blob: bytes) -> dict[str, Any]:
    return {"path": relative, "size": len(blob), "sha256": sha256(blob)}


def safe_output(path: Path, repo_root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise StructuralCompletionError("output must remain inside the patch workspace") from exc
    return resolved


def validate_partition(sources: dict[str, Any]) -> dict[int, str]:
    if len(EXPECTED_IDS) != EXPECTED_COUNT or hash_json(EXPECTED_IDS) != EXPECTED_IDS_SHA256:
        raise StructuralCompletionError("structural completion ID pin changed")
    if len(DYNAMIC_IDS) != EXPECTED_DYNAMIC_COUNT or hash_json(DYNAMIC_IDS) != EXPECTED_DYNAMIC_IDS_SHA256:
        raise StructuralCompletionError("dynamic narrative ID pin changed")
    if len(PRESERVE_IDS) != EXPECTED_PRESERVE_COUNT or hash_json(PRESERVE_IDS) != EXPECTED_PRESERVE_IDS_SHA256:
        raise StructuralCompletionError("byte-preserve ID pin changed")
    if set(DYNAMIC_IDS) & set(PRESERVE_IDS) or sorted(DYNAMIC_IDS + PRESERVE_IDS) != EXPECTED_IDS:
        raise StructuralCompletionError("structural partition is not exact")

    reasons = previous.exclusion_reason_by_id()
    if sorted(reasons) != EXPECTED_IDS:
        raise StructuralCompletionError("batch06 structural reason catalog changed")
    sc = sources["SC"]["table"].texts
    for entry_id in EXPECTED_IDS:
        previous.validate_exclusion_shape(entry_id, reasons[entry_id], sources)
        if "\x00" in sc[entry_id]:
            raise StructuralCompletionError(f"ID {entry_id} contains an embedded NUL")
        if entry_id in DYNAMIC_IDS:
            if reasons[entry_id] not in DYNAMIC_REASONS:
                raise StructuralCompletionError(f"ID {entry_id} is not an approved dynamic narrative")
            replacement = DYNAMIC_TRANSLATIONS[entry_id]
            if strict.upstream.contains_cjk_or_kana(replacement):
                raise StructuralCompletionError(f"ID {entry_id} replacement contains source script")
            if common.invariant_mismatches(sc[entry_id], replacement):
                raise StructuralCompletionError(f"ID {entry_id} runtime invariants changed")
            if base.BRACKET_TOKEN_RE.findall(sc[entry_id]) != base.BRACKET_TOKEN_RE.findall(replacement):
                raise StructuralCompletionError(f"ID {entry_id} dynamic token sequence changed")
        else:
            if reasons[entry_id] in DYNAMIC_REASONS:
                raise StructuralCompletionError(f"ID {entry_id} dynamic narrative lacks review")
            if strict.upstream.contains_cjk_or_kana(sc[entry_id]):
                raise StructuralCompletionError(f"ID {entry_id} byte-preserve value contains source script")
    return reasons


def make_entries(sources: dict[str, Any]) -> list[dict[str, Any]]:
    reasons = validate_partition(sources)
    sc = sources["SC"]["table"].texts
    entries = []
    for entry_id in EXPECTED_IDS:
        replacement = (
            DYNAMIC_TRANSLATIONS[entry_id]
            if entry_id in DYNAMIC_TRANSLATIONS
            else sc[entry_id]
        )
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(sc[entry_id]),
                "ko": replacement,
                "status": "reviewed",
            }
        )
        if entry_id in PRESERVE_IDS and replacement != sc[entry_id]:
            raise StructuralCompletionError(f"ID {entry_id} is not byte-preserved")
        if entry_id in DYNAMIC_IDS and replacement == sc[entry_id]:
            raise StructuralCompletionError(f"ID {entry_id} dynamic narrative was not translated")
        if reasons[entry_id] in DYNAMIC_REASONS and entry_id not in DYNAMIC_IDS:
            raise StructuralCompletionError(f"ID {entry_id} dynamic narrative remains unresolved")
    return entries


def make_overlay(sources: dict[str, Any]) -> dict[str, Any]:
    pin = base.SOURCE_PINS["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": EXPECTED_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": pin["size"],
            "packed_sha256": pin["packed_sha256"],
            "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"],
            "string_count": sources["SC"]["table"].string_count,
        },
        "defaults": {"status": "reviewed"},
        "entries": make_entries(sources),
    }
    common.validate_overlay_shape(overlay)
    return overlay


def audit_progress(
    progress_path: Path,
    repo_root: Path,
    target_ids: set[int],
    overlay_blob: bytes,
) -> dict[str, Any]:
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    rows = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1 or not isinstance(rows[0].get("overlay_globs"), list):
        raise StructuralCompletionError("progress has no unique msgev row")
    patterns = rows[0]["overlay_globs"]
    if len(patterns) != len(set(patterns)):
        raise StructuralCompletionError("progress contains duplicate msgev paths")
    self_count = patterns.count(SELF_OVERLAY_PATH)
    if self_count > 1:
        raise StructuralCompletionError("self overlay is registered more than once")
    if patterns.count(previous.SELF_OVERLAY_PATH) != 1:
        raise StructuralCompletionError("batch06 must be registered exactly once")
    if self_count:
        path = repo_root / SELF_OVERLAY_PATH
        if path.read_bytes() != overlay_blob:
            raise StructuralCompletionError("registered self overlay differs from deterministic output")

    filtered = json.loads(json.dumps(progress))
    filtered_row = next(row for row in filtered["resources"] if row["path"] == RESOURCE)
    filtered_row["overlay_globs"] = [
        item for item in filtered_row["overlay_globs"] if item != SELF_OVERLAY_PATH
    ]
    with tempfile.TemporaryDirectory(prefix="nobu16-msgev-b07-progress-", dir=repo_root / "tmp") as directory:
        filtered_path = Path(directory) / "progress.json"
        filtered_path.write_bytes(previous.encode_json(filtered))
        prior = previous.audit_progress_registration(filtered_path, repo_root, target_ids)

    claims = set(prior["ids"]) | set(previous.SELECTED_IDS)
    if claims & set(EXPECTED_IDS):
        raise StructuralCompletionError("structural completion overlaps predecessor claims")
    gap = sorted(target_ids - claims)
    if gap != EXPECTED_IDS:
        raise StructuralCompletionError("remaining exact target gap is not the structural catalog")
    return {
        "batch06_registered_exactly_once": True,
        "self_registration_count": self_count,
        "predecessor_target_count": len(claims & target_ids),
        "predecessor_target_ids_sha256": hash_json(sorted(claims & target_ids)),
        "pre_completion_gap_count": len(gap),
        "pre_completion_gap_ids_sha256": hash_json(gap),
        "post_completion_target_count": len((claims | set(EXPECTED_IDS)) & target_ids),
        "post_completion_gap_count": len(target_ids - claims - set(EXPECTED_IDS)),
    }


def build_once(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
) -> dict[str, Any]:
    sources = base.load_sources(game_root, repo_root, archive_path)
    target = previous.batch01.load_target_catalog(target_path, repo_root)
    overlay = make_overlay(sources)
    overlay_blob = encode_json(overlay)
    if EXPECTED_OVERLAY_SHA256 != "__PIN_AFTER_GENERATION__" and sha256(overlay_blob) != EXPECTED_OVERLAY_SHA256:
        raise StructuralCompletionError("overlay hash differs from its pin")
    progress = audit_progress(progress_path, repo_root, target["ids"], overlay_blob)
    reasons = validate_partition(sources)
    entries = overlay["entries"]
    rebuilt_a = base.reconstruct_target(sources, entries)
    rebuilt_b = base.reconstruct_target(sources, entries)
    if rebuilt_a != rebuilt_b:
        raise StructuralCompletionError("in-memory reconstruction is not deterministic")

    reason_summary = {
        reason: {
            "count": sum(1 for value in reasons.values() if value == reason),
            "ids_sha256": hash_json(sorted(i for i, value in reasons.items() if value == reason)),
        }
        for reason in sorted(set(reasons.values()))
    }
    evidence_entries = [
        {
            "id": entry_id,
            "status": "reviewed",
            "source_sc_utf16le_sha256": common.text_hash(sources["SC"]["table"].texts[entry_id]),
            "ko_utf16le_sha256": common.text_hash(entries[index]["ko"]),
            "structural_reason": reasons[entry_id],
            "method": "dynamic_narrative_korean_with_exact_runtime_tokens" if entry_id in DYNAMIC_IDS else "exact_structural_byte_preservation",
            "runtime_contract_preserved": True,
            "source_text_embedded": False,
        }
        for index, entry_id in enumerate(EXPECTED_IDS)
    ]
    evidence = {
        "schema": "nobu16.kr.msgev-pk-structural-completion-b07-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "reviewed_count": EXPECTED_COUNT,
            "reviewed_ids_sha256": EXPECTED_IDS_SHA256,
            "exact_byte_preserve_count": EXPECTED_PRESERVE_COUNT,
            "exact_byte_preserve_ids_sha256": EXPECTED_PRESERVE_IDS_SHA256,
            "dynamic_narrative_translation_count": EXPECTED_DYNAMIC_COUNT,
            "dynamic_narrative_ids_sha256": EXPECTED_DYNAMIC_IDS_SHA256,
            "blocked_count": 0,
            "classification_complete": True,
        },
        "reason_summary": reason_summary,
        "progress_audit": progress,
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.msgev-pk-structural-completion-b07-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "quality_state": "structural_review_complete_runtime_screen_review_pending",
        "reviewed_count": EXPECTED_COUNT,
        "exact_byte_preserve_count": EXPECTED_PRESERVE_COUNT,
        "dynamic_narrative_translation_count": EXPECTED_DYNAMIC_COUNT,
        "blocked_count": 0,
        "runtime_screen_reviewed_count": 0,
        "source_script_free": True,
        "complete_target_included": False,
    }
    blobs = {
        f"public/{OVERLAY_NAME}": overlay_blob,
        f"evidence/{EVIDENCE_NAME}": encode_json(evidence),
        f"review/{REVIEW_NAME}": encode_json(review),
    }
    expected_scan = {"han_or_kana_count": 0, "embedded_nul_count": 0}
    scans = {name: strict.source_free_counts(blob) for name, blob in blobs.items()}
    if any(value != expected_scan for value in scans.values()):
        raise StructuralCompletionError("a public artifact contains source script or NUL")
    validation = {
        "schema": "nobu16.kr.msgev-pk-structural-completion-b07-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": evidence["scope"],
        "progress_audit": progress,
        "reason_summary": reason_summary,
        "replacement_invariants": {
            "checked": EXPECTED_COUNT,
            "failures": 0,
            "exact_byte_preserve_count": EXPECTED_PRESERVE_COUNT,
            "dynamic_token_preserve_count": EXPECTED_DYNAMIC_COUNT,
        },
        "target_reconstruction": rebuilt_a,
        "source_free_scan": scans,
        "artifacts": {name: artifact(name, blob) for name, blob in blobs.items()},
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
            "translation_table_sha256": sha256((WORKSTREAM_ROOT / "translations.py").read_bytes()),
        },
        "safety": {
            "installed_game_files_modified": False,
            "memory_patch_used": False,
            "dll_injection_used": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    blobs[VALIDATION_NAME] = encode_json(validation)
    return {
        "files": blobs,
        "target": rebuilt_a,
        "reviewed_count": EXPECTED_COUNT,
        "preserve_count": EXPECTED_PRESERVE_COUNT,
        "dynamic_count": EXPECTED_DYNAMIC_COUNT,
        "blocked_count": 0,
    }


def build_reproducibly(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    out_root = safe_output(out_root, repo_root)
    first = build_once(game_root, repo_root, archive_path, target_path, progress_path)
    second = build_once(game_root, repo_root, archive_path, target_path, progress_path)
    if first != second:
        raise StructuralCompletionError("isolated builds are not byte-identical")
    for relative, blob in first["files"].items():
        common.atomic_write(out_root / relative, blob)
    return first


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--switch-archive",
        type=Path,
        default=REPO_ROOT / strict.SWITCH_ARCHIVE_RELATIVE,
    )
    parser.add_argument("--target-catalog", type=Path, default=REPO_ROOT / TARGET_CATALOG_RELATIVE)
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root.resolve(),
            args.repo_root.resolve(),
            args.switch_archive.resolve(),
            args.target_catalog.resolve(),
            args.progress.resolve(),
            args.out_root.resolve(),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"reviewed={result['reviewed_count']}")
    print(f"exact_byte_preserve={result['preserve_count']}")
    print(f"dynamic_translated={result['dynamic_count']}")
    print(f"blocked={result['blocked_count']}")
    print(f"target_wrapper_sha256={result['target']['packed_sha256']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={sha256(blob)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
