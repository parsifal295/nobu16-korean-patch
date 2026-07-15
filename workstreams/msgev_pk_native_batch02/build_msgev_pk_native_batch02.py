#!/usr/bin/env python3
"""Build the second native PK ``msgev`` translation batch.

The batch takes the first 150 lexical PK/SC target rows that remain after all
registered predecessors and the safety exclusions documented by batch 01.
It reuses nine same-index Switch translations only after adapting them to the
exact PK/SC runtime contract, then translates 141 PK-only event rows from the
pinned official SC/JP/TC/EN alignment.  Public artifacts contain hashes and
Korean replacements, never commercial source strings or a complete resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
BATCH01_ROOT = REPO_ROOT / "workstreams" / "msgev_pk_native_batch01"
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path[:0] = [str(WORKSTREAM_ROOT), str(BATCH01_ROOT), str(TOOLS_ROOT)]

import build_msgev_pk_native_batch01 as batch01  # noqa: E402
from translations import SELECTED_IDS, TRANSLATIONS  # noqa: E402


base = batch01.base
common = batch01.common
strict = batch01.strict
NativeBatchError = batch01.NativeBatchError

BATCH_ID = "msgev-pk-native-batch02-150.v1"
RESOURCE = "MSG_PK/SC/msgev.bin"
OVERLAY_NAME = "msgev_ko_pk_native_batch02_150.v1.json"
EVIDENCE_NAME = "msgev_pk_native_batch02_alignment.v1.json"
REVIEW_NAME = "msgev_pk_native_batch02_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgev_pk_native_batch02/public/{OVERLAY_NAME}"
TARGET_CATALOG_RELATIVE = Path("data/public/translation_target_keys.v0.1.json")
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")

EXPECTED_TARGET_COUNT = 12_906
EXPECTED_TARGET_IDS_SHA256 = base.EXPECTED_TARGET_IDS_SHA256
EXPECTED_PREDECESSOR_PATH_COUNT = 34
EXPECTED_PREDECESSOR_PATHS_SHA256 = (
    "F7878E6FEC9524DE798CC1484BBE5CED1AA6B5BC817AF66DBF0B1099A6BFCA34"
)
EXPECTED_PREDECESSOR_CLAIM_COUNT = 13_028
EXPECTED_PREDECESSOR_CLAIM_IDS_SHA256 = (
    "394202C7C85B347BCF88131F6782971593E64BAD92C7E5B6B6916A5212809B76"
)
EXPECTED_PREDECESSOR_TARGET_COUNT = 11_430
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = (
    "8C2769DA64E1494DA45F0B4C28B2B3290032F7D802256C8ADC61A41069722614"
)
EXPECTED_PREDECESSOR_OUTSIDE_TARGET_COUNT = 1_598
EXPECTED_PREDECESSOR_OUTSIDE_TARGET_IDS_SHA256 = (
    "5C050980004350E17D6B4E5BFC0151075CFDEBF1D41006A7E7FBE5BBC2B0E313"
)
EXPECTED_PRE_BATCH_GAP_COUNT = 1_476
EXPECTED_PRE_BATCH_GAP_IDS_SHA256 = (
    "5354079470DDC716B890A4972947BF3E1103D9FE094CB6605C1D5E2C764DD0A3"
)
EXPECTED_SELECTED_IDS_SHA256 = (
    "DE2892A479E562CC6EEC4A74D78F0333481D9323D3817F6EF0F8FD07691EA3B9"
)
EXPECTED_CANDIDATE_COUNT = 284
EXPECTED_CANDIDATE_IDS_SHA256 = (
    "4BB06E06A4CB4C8EA0100879F201B0DF7DD6B3F2648A94C758C2320F44ADB68A"
)
EXPECTED_EXCLUDED_COUNT = 134
EXPECTED_EXCLUDED_IDS_SHA256 = (
    "287F7E8FBB66E78E6E75CA0C540E720300F086478177836C277277EB6D1D5F74"
)
EXPECTED_NEW_EXCLUDED_IDS_SHA256 = (
    "78B147F8507CA86D373BF56A3283059C9BF5228C443D8F3BB22299CF21D359A8"
)

EXPECTED_OVERLAY_SHA256 = (
    "642E5B0B7503B5CCA6472CE10E4066296C6D8F6DA8DD8BC2B16EDA7BEC554367"
)

SWITCH_SEMANTIC_REUSE_IDS = [
    7_841,
    7_844,
    7_845,
    7_908,
    7_918,
    8_440,
    8_466,
    8_494,
    9_506,
]
PK_NATIVE_IDS = [entry_id for entry_id in SELECTED_IDS if entry_id not in SWITCH_SEMANTIC_REUSE_IDS]

NEW_DYNAMIC_TOKEN_PUNCTUATION_IDS = [8_006, 8_375]
NEW_PUNCTUATION_ONLY_IDS = [
    7_996,
    8_118,
    8_123,
    8_141,
    8_181,
    8_220,
    8_355,
    8_398,
    8_437,
    8_529,
    8_577,
    8_588,
    8_589,
    8_603,
    8_625,
    8_631,
    8_644,
    8_671,
    8_676,
    8_708,
    8_848,
    8_875,
    8_890,
    8_900,
    9_016,
    9_056,
    9_197,
    9_456,
    9_495,
    9_532,
    9_568,
    9_631,
    9_656,
    9_722,
    9_758,
    9_762,
    9_845,
    9_849,
    9_853,
    9_854,
]
NEW_EXCLUDED_IDS = sorted(
    NEW_DYNAMIC_TOKEN_PUNCTUATION_IDS + NEW_PUNCTUATION_ONLY_IDS
)
EXCLUDED_IDS = sorted(set(batch01.EXCLUDED_IDS) | set(NEW_EXCLUDED_IDS))
CANDIDATE_IDS = sorted(set(SELECTED_IDS) | set(EXCLUDED_IDS))

HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


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


def artifact_metadata(relative: str, blob: bytes) -> dict[str, Any]:
    return {"path": relative, "size": len(blob), "sha256": sha256(blob)}


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def _safe_out_root(path: Path, repo_root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise NativeBatchError("output must remain inside the patch workspace") from exc
    return resolved


def _load_overlay(path: Path) -> tuple[dict[str, Any], bytes, list[int]]:
    overlay, blob = common.load_json_strict(path)
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE:
        raise NativeBatchError(f"overlay targets another resource: {path}")
    return overlay, blob, [int(entry["id"]) for entry in entries]


def audit_progress_registration(
    progress_path: Path, repo_root: Path, target_ids: set[int]
) -> dict[str, Any]:
    """Freeze predecessors while tolerating exact self/successor registration.

    The first 34 non-self paths are the pinned predecessor set.  Later paths
    are validated for overlap but deliberately do not change this batch's
    selection or artifacts, preventing the predecessor regression seen in
    older workstream builders after successor registration.
    """

    progress, _blob = common.load_json_strict(progress_path)
    resources = progress.get("resources")
    rows = (
        [row for row in resources if row.get("path") == RESOURCE]
        if isinstance(resources, list)
        else []
    )
    if len(rows) != 1:
        raise NativeBatchError("progress catalog has no unique msgev row")
    patterns = rows[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise NativeBatchError("msgev progress overlay paths are invalid")
    if len(patterns) != len(set(patterns)):
        raise NativeBatchError("msgev progress overlay paths are duplicated")
    if patterns.count(SELF_OVERLAY_PATH) > 1:
        raise NativeBatchError("self overlay is registered more than once")

    nonself = [pattern for pattern in patterns if pattern != SELF_OVERLAY_PATH]
    predecessor_patterns = nonself[:EXPECTED_PREDECESSOR_PATH_COUNT]
    successor_patterns = nonself[EXPECTED_PREDECESSOR_PATH_COUNT:]
    if (
        len(predecessor_patterns) != EXPECTED_PREDECESSOR_PATH_COUNT
        or hash_json(predecessor_patterns) != EXPECTED_PREDECESSOR_PATHS_SHA256
    ):
        raise NativeBatchError("pinned msgev predecessor path set/order changed")

    predecessor_ids: list[int] = []
    all_registered_ids: list[int] = []
    for pattern in patterns:
        paths = sorted(repo_root.glob(pattern))
        if len(paths) != 1:
            raise NativeBatchError(
                f"progress overlay pattern {pattern!r} resolved to {len(paths)} files"
            )
        path = paths[0]
        logical = _repo_relative(path, repo_root)
        if logical != pattern:
            raise NativeBatchError("msgev progress paths must be exact repo-relative paths")
        overlay, overlay_blob, ids = _load_overlay(path)
        if pattern == SELF_OVERLAY_PATH:
            if overlay.get("overlay_id") != BATCH_ID or ids != SELECTED_IDS:
                raise NativeBatchError("self registration overlay identity changed")
            if hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
                raise NativeBatchError("self registration ID hash changed")
            if (
                EXPECTED_OVERLAY_SHA256 != "__PIN_AFTER_GENERATION__"
                and sha256(overlay_blob) != EXPECTED_OVERLAY_SHA256
            ):
                raise NativeBatchError("self registration overlay hash changed")
        elif pattern in predecessor_patterns:
            predecessor_ids.extend(ids)
        all_registered_ids.extend(ids)

    if len(all_registered_ids) != len(set(all_registered_ids)):
        raise NativeBatchError("registered msgev overlays overlap")
    claims = set(predecessor_ids)
    if (
        len(claims) != EXPECTED_PREDECESSOR_CLAIM_COUNT
        or hash_json(sorted(claims)) != EXPECTED_PREDECESSOR_CLAIM_IDS_SHA256
    ):
        raise NativeBatchError("pinned predecessor msgev claim set changed")
    target_claims = claims & target_ids
    outside_claims = claims - target_ids
    if (
        len(target_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT
        or hash_json(sorted(target_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256
    ):
        raise NativeBatchError("pinned predecessor target claims changed")
    if (
        len(outside_claims) != EXPECTED_PREDECESSOR_OUTSIDE_TARGET_COUNT
        or hash_json(sorted(outside_claims))
        != EXPECTED_PREDECESSOR_OUTSIDE_TARGET_IDS_SHA256
    ):
        raise NativeBatchError("pinned predecessor outside-target claims changed")
    gap_ids = sorted(target_ids - claims)
    if (
        len(gap_ids) != EXPECTED_PRE_BATCH_GAP_COUNT
        or hash_json(gap_ids) != EXPECTED_PRE_BATCH_GAP_IDS_SHA256
    ):
        raise NativeBatchError("pre-batch exact target gap changed")
    successor_ids = set(all_registered_ids) - claims - (
        set(SELECTED_IDS) if SELF_OVERLAY_PATH in patterns else set()
    )
    if successor_ids & set(CANDIDATE_IDS):
        raise NativeBatchError("a successor overlay overlaps this batch candidate range")
    if claims & set(SELECTED_IDS):
        raise NativeBatchError("selected IDs overlap a pinned predecessor overlay")

    return {
        "predecessor_overlay_path_count": len(predecessor_patterns),
        "predecessor_overlay_paths_sha256": hash_json(predecessor_patterns),
        "predecessor_claim_count": len(claims),
        "predecessor_claim_ids_sha256": hash_json(sorted(claims)),
        "predecessor_target_intersection_count": len(target_claims),
        "predecessor_target_intersection_ids_sha256": hash_json(sorted(target_claims)),
        "predecessor_outside_target_count": len(outside_claims),
        "predecessor_outside_target_ids_sha256": hash_json(sorted(outside_claims)),
        "pre_batch_gap_count": len(gap_ids),
        "pre_batch_gap_ids_sha256": hash_json(gap_ids),
        "candidate_count": len(CANDIDATE_IDS),
        "candidate_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
        "selected_count": len(SELECTED_IDS),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "excluded_count": len(EXCLUDED_IDS),
        "excluded_ids_sha256": EXPECTED_EXCLUDED_IDS_SHA256,
        "selected_predecessor_overlap_count": 0,
        "selected_target_intersection_count": len(SELECTED_IDS),
        "selected_outside_target_count": 0,
        "target_coverage_after_registration": len(target_claims) + len(SELECTED_IDS),
        "target_gap_after_registration": len(gap_ids) - len(SELECTED_IDS),
        "self_registration_states_allowed": ["absent", "one_exact_path"],
        "self_excluded_from_predecessor_claims": True,
        "successor_registration_tolerant": True,
        "ids": claims,
    }


def _has_letter_or_number(text: str) -> bool:
    return batch01._has_letter_or_number(text)


def _remove_runtime_tokens(text: str) -> str:
    return batch01._remove_runtime_tokens(text)


def exclusion_reason_by_id() -> dict[int, str]:
    reasons = dict(batch01.exclusion_reason_by_id())
    for entry_id in NEW_DYNAMIC_TOKEN_PUNCTUATION_IDS:
        reasons[entry_id] = "dynamic_token_with_nonlexical_punctuation"
    for entry_id in NEW_PUNCTUATION_ONLY_IDS:
        reasons[entry_id] = "nonlexical_punctuation_only"
    if sorted(reasons) != EXCLUDED_IDS:
        raise NativeBatchError("exclusion reasons do not exactly cover exclusions")
    return reasons


def validate_exclusion_shape(
    entry_id: int, reason: str, sources: dict[str, Any]
) -> None:
    if entry_id in batch01.EXCLUDED_IDS:
        batch01.validate_exclusion_shape(entry_id, reason, sources)
        return
    sc = sources["SC"]["table"].texts[entry_id]
    if reason == "dynamic_token_with_nonlexical_punctuation":
        if not base.BRACKET_TOKEN_RE.search(sc) or _has_letter_or_number(
            _remove_runtime_tokens(sc)
        ):
            raise NativeBatchError(f"ID {entry_id} is no longer token plus punctuation")
    elif reason == "nonlexical_punctuation_only":
        if (
            _has_letter_or_number(sc)
            or common.ESC_RE.search(sc)
            or base.BRACKET_TOKEN_RE.search(sc)
        ):
            raise NativeBatchError(f"ID {entry_id} is no longer punctuation-only")
    else:
        raise NativeBatchError(f"unknown new exclusion reason {reason}")


def validate_translation(source_sc: str, translation: str, entry_id: int) -> dict[str, Any]:
    if not common.has_semantic_text(source_sc):
        raise NativeBatchError(f"ID {entry_id} is not a visible PK SC target")
    if not common.has_semantic_text(translation) or HANGUL_RE.search(translation) is None:
        raise NativeBatchError(f"ID {entry_id} lacks meaningful Hangul")
    if strict.upstream.contains_cjk_or_kana(translation):
        raise NativeBatchError(f"ID {entry_id} contains CJK or Kana")
    problems = common.invariant_mismatches(source_sc, translation)
    if problems:
        raise NativeBatchError(f"ID {entry_id} PK SC invariants differ: {problems}")
    source_brackets = base.BRACKET_TOKEN_RE.findall(source_sc)
    target_brackets = base.BRACKET_TOKEN_RE.findall(translation)
    if source_brackets != target_brackets:
        raise NativeBatchError(f"ID {entry_id} custom bracket sequence differs")
    return {
        "pk_sc_invariants_preserved": True,
        "custom_bracket_tokens_preserved": True,
        "custom_bracket_token_count": len(source_brackets),
        "source_script_free": True,
    }


def derive_candidate_partition(
    sources: dict[str, Any], target_ids: set[int], predecessor_ids: set[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if len(SELECTED_IDS) != 150 or hash_json(SELECTED_IDS) != EXPECTED_SELECTED_IDS_SHA256:
        raise NativeBatchError("selected ID set differs from its pin")
    if len(NEW_EXCLUDED_IDS) != 42 or hash_json(NEW_EXCLUDED_IDS) != EXPECTED_NEW_EXCLUDED_IDS_SHA256:
        raise NativeBatchError("new exclusion ID set differs from its pin")
    if len(EXCLUDED_IDS) != EXPECTED_EXCLUDED_COUNT or hash_json(EXCLUDED_IDS) != EXPECTED_EXCLUDED_IDS_SHA256:
        raise NativeBatchError("complete exclusion ID set differs from its pin")
    if len(CANDIDATE_IDS) != EXPECTED_CANDIDATE_COUNT or hash_json(CANDIDATE_IDS) != EXPECTED_CANDIDATE_IDS_SHA256:
        raise NativeBatchError("candidate ID set differs from its pin")
    if sorted(TRANSLATIONS) != SELECTED_IDS:
        raise NativeBatchError("translation table does not exactly cover selected IDs")
    if len(SWITCH_SEMANTIC_REUSE_IDS) != 9 or len(PK_NATIVE_IDS) != 141:
        raise NativeBatchError("translation provenance partition changed")

    gaps = sorted(target_ids - predecessor_ids)
    lexical_ids = [
        entry_id
        for entry_id in gaps
        if entry_id not in batch01.EXCLUDED_IDS
        and _has_letter_or_number(
            _remove_runtime_tokens(sources["SC"]["table"].texts[entry_id])
        )
    ]
    if lexical_ids[:150] != SELECTED_IDS:
        raise NativeBatchError("selection is no longer the first 150 safe lexical gap rows")
    candidate_ids = [entry_id for entry_id in gaps if entry_id <= SELECTED_IDS[-1]]
    if candidate_ids != CANDIDATE_IDS:
        raise NativeBatchError("candidate frontier through the 150th lexical row changed")

    reasons = exclusion_reason_by_id()
    jp_buckets = strict.exact_jp_buckets(
        {
            "pk_jp": sources["JP"],
            "base_jp": sources["base_jp"],
            "switch_ko": sources["switch_ko"],
        }
    )
    entries: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    review_exclusions: list[dict[str, Any]] = []
    for entry_id in CANDIDATE_IDS:
        if entry_id not in target_ids or entry_id in predecessor_ids:
            raise NativeBatchError(f"ID {entry_id} is not an unclaimed exact target")
        hashes = {
            language: common.text_hash(sources[language]["table"].texts[entry_id])
            for language in ("SC", "JP", "EN", "TC")
        }
        if entry_id in reasons:
            reason = reasons[entry_id]
            validate_exclusion_shape(entry_id, reason, sources)
            evidence_rows.append(
                {
                    "id": entry_id,
                    "status": "excluded",
                    "official_pk_utf16le_sha256": hashes,
                    "exclusion_reason": reason,
                    "preserve_stock_value": True,
                    "overlay_claim_created": False,
                    "selected_within_exact_target_key": True,
                }
            )
            review_exclusions.append(
                {
                    "id": entry_id,
                    "status": "excluded",
                    "reason": reason,
                    "runtime_safety_decision": "preserve_stock_value",
                    "progress_claim_created": False,
                }
            )
            continue

        source_sc = sources["SC"]["table"].texts[entry_id]
        translation = TRANSLATIONS[entry_id]
        checks = validate_translation(source_sc, translation, entry_id)
        if entry_id in SWITCH_SEMANTIC_REUSE_IDS:
            if entry_id >= len(sources["base_jp"]["table"].texts):
                raise NativeBatchError(f"ID {entry_id} has no same-index Switch row")
            switch_jp = sources["base_jp"]["table"].texts[entry_id]
            switch_ko = sources["switch_ko"]["table"].texts[entry_id]
            if not common.has_semantic_text(switch_jp) or not common.has_semantic_text(switch_ko):
                raise NativeBatchError(f"ID {entry_id} lost its semantic Switch evidence")
            provenance = {
                "translation_kind": "switch_same_index_semantic_reuse",
                "semantic_basis": "switch_v13_same_index_plus_official_pk_four_language_review",
                "switch_same_index_jp_utf16le_sha256": common.text_hash(switch_jp),
                "switch_same_index_ko_utf16le_sha256": common.text_hash(switch_ko),
                "adapted_to_exact_pk_sc_runtime_contract": True,
            }
        else:
            jp = sources["JP"]["table"].texts[entry_id]
            exact = [
                row
                for row in jp_buckets.get(common.text_hash(jp), [])
                if row["jp"] == jp
            ]
            if exact:
                raise NativeBatchError(f"ID {entry_id} unexpectedly gained an exact Switch JP mapping")
            provenance = {
                "translation_kind": "pk_native_event_translation",
                "semantic_basis": "official_pk_sc_jp_tc_en_context",
                "switch_exact_mapping_available": False,
            }
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": hashes["SC"],
                "ko": translation,
            }
        )
        evidence_rows.append(
            {
                "id": entry_id,
                "status": "translated",
                "official_pk_utf16le_sha256": hashes,
                "ko_utf16le_sha256": common.text_hash(translation),
                "official_multilingual_context_reviewed": True,
                "selected_within_exact_target_key": True,
                "selected_within_stock_visible_target": True,
                "disjoint_from_predecessor_overlays": True,
                **provenance,
                **checks,
            }
        )

    if [entry["id"] for entry in entries] != SELECTED_IDS:
        raise NativeBatchError("derived selected entries changed")
    if [entry["id"] for entry in review_exclusions] != EXCLUDED_IDS:
        raise NativeBatchError("derived exclusions changed")
    return entries, evidence_rows, review_exclusions


def actual_input_snapshot(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
) -> dict[str, str]:
    source_pins = base.SOURCE_PINS
    paths = {
        "switch_archive": archive_path,
        "base_jp": game_root / strict.upstream.SOURCE_PINS["base_jp"]["logical_path"],
        "pk_sc": repo_root / source_pins["SC"]["logical_path"],
        "pk_jp": game_root / source_pins["JP"]["logical_path"],
        "pk_en": game_root / source_pins["EN"]["logical_path"],
        "pk_tc": game_root / source_pins["TC"]["logical_path"],
        "target_catalog": target_path,
        "progress_catalog": progress_path,
        "translation_table": WORKSTREAM_ROOT / "translations.py",
    }
    return {name: sha256(path.read_bytes()) for name, path in paths.items()}


def build_once(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    out_root = _safe_out_root(out_root, repo_root)
    before = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    target = batch01.load_target_catalog(target_path, repo_root)
    progress = audit_progress_registration(progress_path, repo_root, target["ids"])
    sources = base.load_sources(game_root, repo_root, archive_path)
    entries, evidence_rows, review_exclusions = derive_candidate_partition(
        sources, target["ids"], progress["ids"]
    )
    rebuilt_a = base.reconstruct_target(sources, entries)
    rebuilt_b = base.reconstruct_target(sources, entries)
    if rebuilt_a != rebuilt_b:
        raise NativeBatchError("in-memory target reconstruction is not deterministic")

    source_public = {
        language: sources[language]["public_pin"]
        for language in ("SC", "JP", "EN", "TC")
    }
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
            key: source_public["SC"][key]
            for key in ("size", "packed_sha256", "raw_size", "raw_sha256", "string_count")
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)

    target_public = {key: value for key, value in target.items() if key != "ids"}
    progress_public = {key: value for key, value in progress.items() if key != "ids"}
    reason_map = exclusion_reason_by_id()
    class_summary = {
        reason: {
            "count": sum(1 for value in reason_map.values() if value == reason),
            "ids_sha256": hash_json(
                sorted(entry_id for entry_id, value in reason_map.items() if value == reason)
            ),
        }
        for reason in sorted(set(reason_map.values()))
    }
    scope = {
        "candidate_count": len(CANDIDATE_IDS),
        "candidate_ids": CANDIDATE_IDS,
        "candidate_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
        "translated_count": len(entries),
        "translated_ids": SELECTED_IDS,
        "translated_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "switch_semantic_reuse_count": len(SWITCH_SEMANTIC_REUSE_IDS),
        "pk_native_translation_count": len(PK_NATIVE_IDS),
        "excluded_count": len(review_exclusions),
        "excluded_ids": EXCLUDED_IDS,
        "excluded_ids_sha256": EXPECTED_EXCLUDED_IDS_SHA256,
        "new_excluded_count": len(NEW_EXCLUDED_IDS),
        "candidate_partition_complete": True,
    }
    evidence = {
        "schema": "nobu16.kr.msgev-pk-native-batch02-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": scope,
        "official_source_files": source_public,
        "switch_release_checked": strict.SWITCH_RELEASE,
        "target_catalog": target_public,
        "progress_registration_audit": progress_public,
        "exclusion_classes": class_summary,
        "translation_policy": {
            "selection": "first_150_safe_lexical_gap_rows_after_batch01_exclusions",
            "runtime_contract_authority": "pk_sc",
            "semantic_context_languages": ["SC", "JP", "TC", "EN"],
            "switch_same_index_semantic_reuse_adapted_to_pk_sc": True,
            "pk_only_rows_translated_natively": True,
            "excluded_runtime_keys_are_not_translation_progress": True,
            "published_source_material": "hashes_only",
        },
        "entry_count": len(evidence_rows),
        "entries": evidence_rows,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.msgev-pk-native-batch02-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "quality_state": "native_semantic_review_complete_runtime_review_pending",
        "candidate_count": len(CANDIDATE_IDS),
        "translated_count": len(entries),
        "excluded_count": len(review_exclusions),
        "translated": [
            {
                "id": row["id"],
                "status": "translated",
                "translation_kind": row["translation_kind"],
                "semantic_basis": row["semantic_basis"],
                "pk_sc_invariants_preserved": True,
                "custom_bracket_tokens_preserved": True,
                "source_script_free": True,
                "predecessor_overlay_disjoint": True,
                "exact_target": True,
                "runtime_reviewed": False,
            }
            for row in evidence_rows
            if row["status"] == "translated"
        ],
        "excluded": review_exclusions,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }

    values = {
        f"public/{OVERLAY_NAME}": overlay,
        f"evidence/{EVIDENCE_NAME}": evidence,
        f"review/{REVIEW_NAME}": review,
    }
    files = {relative: encode_json(value) for relative, value in values.items()}
    expected_scan = {"han_or_kana_count": 0, "embedded_nul_count": 0}
    scans = {relative: strict.source_free_counts(blob) for relative, blob in files.items()}
    if any(scan != expected_scan for scan in scans.values()):
        raise NativeBatchError("a generated public artifact contains source script")
    artifacts = {
        relative: artifact_metadata(relative, blob) for relative, blob in files.items()
    }
    validation = {
        "schema": "nobu16.kr.msgev-pk-native-batch02-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": scope,
        "target_catalog": target_public,
        "progress_registration_audit": progress_public,
        "exclusion_classes": class_summary,
        "replacement_invariants": {
            "checked": len(entries),
            "failures": 0,
            "pk_sc_contract_preserved_count": len(entries),
            "custom_bracket_contract_preserved_count": len(entries),
            "source_script_free_count": len(entries),
        },
        "target_reconstruction": rebuilt_a,
        "source_free_scan": scans,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
            "translation_table_path": "translations.py",
            "translation_table_sha256": sha256((WORKSTREAM_ROOT / "translations.py").read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "pre_and_post_self_registration_must_be_byte_identical": True,
            "successor_registration_tolerant": True,
            "in_memory_target_a_b_equal": True,
        },
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "base_msg_sc_modified": False,
            "root_progress_modified": False,
            "root_readme_modified": False,
            "font_modified": False,
            "commit_or_push_performed": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_blob = encode_json(validation)
    if strict.source_free_counts(validation_blob) != expected_scan:
        raise NativeBatchError("generated validation contains source script")
    files[VALIDATION_NAME] = validation_blob

    for relative, blob in files.items():
        path = out_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)

    target_after = batch01.load_target_catalog(target_path, repo_root)
    progress_after = audit_progress_registration(progress_path, repo_root, target_after["ids"])
    after = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    if before != after:
        raise NativeBatchError("a read-only input changed during generation")
    if target_after != target or progress_after != progress:
        raise NativeBatchError("target or progress ownership changed during generation")
    return {
        "candidate_count": len(CANDIDATE_IDS),
        "entry_count": len(entries),
        "excluded_count": len(review_exclusions),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "target": rebuilt_a,
        "files": files,
        "artifacts": {
            **artifacts,
            VALIDATION_NAME: artifact_metadata(VALIDATION_NAME, validation_blob),
        },
    }


def build_reproducibly(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    out_root = _safe_out_root(out_root, repo_root)
    before = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    tmp_root = repo_root / "tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="nobu16-msgev-native-b02-a-", dir=tmp_root
    ) as first_dir, tempfile.TemporaryDirectory(
        prefix="nobu16-msgev-native-b02-b-", dir=tmp_root
    ) as second_dir:
        first = build_once(
            game_root, repo_root, archive_path, target_path, progress_path, Path(first_dir)
        )
        second = build_once(
            game_root, repo_root, archive_path, target_path, progress_path, Path(second_dir)
        )
        if first["files"] != second["files"] or first["target"] != second["target"]:
            raise NativeBatchError("isolated builds are not byte-identical")
    final = build_once(
        game_root, repo_root, archive_path, target_path, progress_path, out_root
    )
    if final["files"] != first["files"] or final["target"] != first["target"]:
        raise NativeBatchError("final build differs from isolated builds")
    if actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    ) != before:
        raise NativeBatchError("a read-only input changed across the reproducible build")
    return final


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--archive", type=Path, default=REPO_ROOT / strict.SWITCH_ARCHIVE_RELATIVE
    )
    parser.add_argument(
        "--target-catalog", type=Path, default=REPO_ROOT / TARGET_CATALOG_RELATIVE
    )
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root,
            args.repo_root,
            args.archive,
            args.target_catalog,
            args.progress,
            args.out_root,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"candidates={result['candidate_count']}")
    print(f"translated={result['entry_count']}")
    print(f"excluded={result['excluded_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['packed_sha256']}")
    for relative, artifact in sorted(result["artifacts"].items()):
        print(f"{relative}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
