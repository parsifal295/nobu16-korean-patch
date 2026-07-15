#!/usr/bin/env python3
"""Build the first semantic-review batch from the v1.3 msggame exclusions.

The batch is intentionally source-free.  It publishes only coordinates whose
Switch Korean meaning and complete PK JP/SC record context make the Korean
fragment boundary unambiguous.  The rest of the first 100-coordinate review
window remains explicitly excluded.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
RECOVERY_ROOT = REPO_ROOT / "workstreams" / "switch_msggame_v13_invariant_recovery"
sys.path.insert(0, str(RECOVERY_ROOT))

import build_switch_msggame_v13_invariant_recovery as recovery  # noqa: E402


BATCH_ID = "switch_v13_pk_msggame_semantic_review_b01_53.v1"
RESOURCE = recovery.RESOURCE
OVERLAY_NAME = "msggame_ko_switch_v13_semantic_review_b01_53.v1.json"
EVIDENCE_NAME = "switch_v13_pk_msggame_semantic_review_b01_evidence.v1.json"
REVIEW_NAME = "switch_v13_pk_msggame_semantic_review_b01_review.v1.json"
VALIDATION_NAME = "switch_v13_pk_msggame_semantic_review_b01_validation.v1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()
PREDECESSOR_BOUNDARY_RELATIVE = recovery.SELF_RELATIVE
PREDECESSOR_PATHS_PIN = "71C29923F39216680E10DB7548B13D6FD27C16F4C25C0A1CA5F3A2C8D1BD9DB9"
PREDECESSOR_COORDINATE_COUNT = 9_898
SELF_COORDINATES_PIN = "D734E31CF4348AEB4095E70F33CDF71E75A66F356A1176A205714A1775098FA6"
SELF_OVERLAY_SHA256 = "8F1450EE1E06F26E8A2AC004E1562241F2150CF3FEF0EA10BD8B5786DDA05A3B"
PRIOR_REVIEW = (
    RECOVERY_ROOT
    / "review"
    / "switch_v13_pk_msggame_invariant_recovery_review.v1.json"
)
PRIOR_REVIEW_PIN = "2C2F2603B01C14E5A706B35190ED5A76CFB1E1CF4E2D0BF9DB2ACDA7F81095D4"
WINDOW_PIN = "FA1448A158FA57F9FDCB58BD9451337CCF31EF3D0F2A98645750193B5116ABCE"


# These replacements were authored after reading the complete record context,
# rather than by splitting the Switch literal mechanically.  Newlines and edge
# whitespace deliberately follow the pristine PK/SC literal at each coordinate.
TRANSLATIONS: dict[tuple[int, int, int], str] = {
    (6, 3939, 1): "에 도달했습니다.\n곧바로 교섭에 들어가시겠습니까?",
    (6, 3940, 2): "\n면회를 요청하러 찾아왔습니다.",
    (6, 3941, 0): "측에서 동맹을 요청했습니다.\n수락하시겠습니까?",
    (6, 3944, 0): "측에서 혼인 동맹을 요청했습니다.\n수락하시겠습니까?",
    (6, 3949, 0): "정말 거절하시겠습니까?\n거절하면",
    (6, 3949, 1): "의 신용이 떨어질 뿐 아니라,\n다른 가문의 의심도 사게 됩니다.",
    (6, 3950, 1): "마저 당가가 함락시키더라도,\n여전히",
    (6, 3950, 2): "의 지배하에 놓입니다.\n부디 주의하십시오.",
    (6, 3955, 0): "요즘은 흉흉해 이래저래 돈 들 일이 많아서…\n고작",
    (6, 3959, 0): "그 가문은 인척이라 오랜 동맹 관계입니다.\n필요한",
    (6, 3960, 0): "두 가문의 동맹 관계에 근거하여,\n필요한",
    (6, 3960, 1): "등의 협력을 얻는 것을 목표로,\n친선을 시작하겠습니다.",
    (6, 3961, 0): "그 가문과는 과거 힘을 합친 사이입니다.\n필요한",
    (6, 3961, 1): "등의 협력을 얻는 것을 목표로,\n친선을 시작하겠습니다.",
    (6, 3972, 0): "적의 위신이 당가를 웃돌아 병사들이\n다소 불안해하고 있습니다…\n부디 방심하지 마십시오.",
    (6, 3973, 0): "적의 위신이 당가를 웃돌아 병사들이\n다소 불안해하고 있습니다…\n부디 방심하지 마십시오.",
    (6, 3974, 0): "적의 위신이 당가를 웃돌아 병사들이\n다소 불안해하고 있습니다…\n부디 방심하지 마십시오.",
    (6, 3978, 0): "적의 위신이 당가를 웃돌아 병사들이\n다소 불안해하고 있습니다…\n부디 방심하지 마십시오.",
    (6, 3984, 0): "압도적으로 높은 적의 위신에,\n병사들이 위축되어 있습니다.",
    (6, 3985, 0): "압도적으로 높은 적의 위신에,\n병사들이 위축되어 있습니다.",
    (6, 3986, 0): "압도적으로 높은 적의 위신에,\n병사들이 위축되어 있습니다.",
    (6, 3990, 0): "압도적으로 높은 적의 위신에,\n병사들이 위축되어 있습니다.",
    (6, 4018, 1): "필요합니다.\n명령만 내리시면 즉시 전투를 준비해,\n당가의 힘을 천하에 알리겠습니다.",
    (6, 4020, 1): "에서는,\n병력은 우세하지만 위신에 눌려,\n당가의 병사들이 위축되어 있습니다.",
    (6, 4021, 1): "에서는,\n병력은 호각이나 위신에 압도되어,\n당가의 병사들이 위축되어 있습니다.",
    (6, 4022, 1): "에서는,\n병력도 열세이고 위신에도 압도되어,\n당가의 병사들이 위축되어 있습니다.",
    (6, 4023, 1): "에서는,\n병력은 우세하지만 위신에서 밀려,\n병사들이 본래 힘을 발휘하지 못합니다.",
    (6, 4024, 1): "에서는,\n병력은 호각이나 위신에서 밀려,\n병사들이 본래 힘을 발휘하지 못합니다.",
    (6, 4025, 1): "에서는,\n병력도 열세이고 위신에서도 밀려,\n병사들이 본래 힘을 발휘하지 못합니다.",
    (6, 4026, 1): "에서는,\n당가의 병력이 우세합니다.",
    (6, 4027, 1): "에서는,\n병력이 백중세입니다.",
    (6, 4028, 1): "에서는,\n당가의 병력이 열세입니다.",
    (6, 4031, 0): "운은 하늘에 있고, 갑옷은 가슴에 있으며,\n공은 발에 있다…\n이번에는",
    (6, 4032, 0): "만사 서두르지 마라.\n이번에는",
    (6, 4033, 0): "계책이 많으면 이기고 적으면 진다.\n이번에는",
    (6, 4034, 0): "대비를 갖추고 당당히 진군하여,\n이번에는",
    (6, 4060, 1): "을 본거지로 삼겠습니다.\n이 땅을 당가의 중심으로 번영시키겠습니다.",
    (6, 4158, 0): "우리 군단의 부대가\n현재",
    (6, 4159, 0): "우리 군단의 부대가\n현재",
    (6, 4160, 0): "우리 군단의 부대가\n현재",
    (6, 4161, 0): "우리 군단의 부대가\n현재",
    (6, 4161, 1): "등 여러 방면으로 진군 중입니다.",
    (6, 4162, 0): "우리 군단의 부대가\n현재",
    (6, 4162, 1): "등 여러 방면으로 진군 중입니다.",
    (6, 4163, 0): "우리 군단의 부대가\n현재",
    (6, 4163, 1): "등 여러 방면으로 진군 중입니다.",
    (6, 4170, 1): "공략을 위해",
    (6, 4170, 2): ",\n군비를 갖추고 있습니다.\n준비가 끝나는 대로 출진합니다.",
    (6, 4171, 0): "병력 준비는 완벽합니다.\n영지 확대의 기회가 온다면,\n즉시 출진하겠습니다.",
    (6, 4172, 0): "병력이 부족해 영지 확대를 기대하기 어렵습니다.\n당분간 기존 영지 발전에 힘쓰며,\n주변의 빈틈을 기다리겠습니다.",
    (6, 4174, 0): "전선의 병력이 부족해,\n공략할 수 있는 세력이 없습니다.\n다른 군단의 지원이 있다면…",
    (6, 4176, 0): "상황이 변하여,\n공략 지시를 내린 성을\n공격할 수 없습니다.",
    (6, 4178, 0): "주변에 공략할 수 있는 성이 없어,\n영내 발전에 전념하고 있습니다.\n모든 취락을 이미 장악했습니다.",
}


class BatchError(ValueError):
    """Raised when a pinned review or safety condition changes."""


def exclusion_reason(coordinate: tuple[int, int, int]) -> str:
    if coordinate == (2, 659, 2):
        return "non_language_format_fragment"
    if coordinate in {(6, 3942, 2), (6, 3942, 3)}:
        return "cross_literal_dynamic_boundary_requires_joint_rewrite"
    if coordinate in {(6, 3952, 0), (6, 3958, 0), (6, 4179, 0), (6, 4180, 0), (6, 4194, 1)}:
        return "adjacent_existing_translation_conflict"
    if 4008 <= coordinate[1] <= 4014:
        return "dynamic_target_order_ambiguous"
    if 4134 <= coordinate[1] <= 4152:
        return "switch_record_alignment_absent_and_word_order_crosses_dynamic_boundary"
    return "multi_dynamic_boundary_or_partial_record_context_ambiguous"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BatchError(f"JSON root is not an object: {path}")
    return value


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    if path.parent.name in {"public", "evidence", "review"}:
        relative = Path(path.parent.name) / path.name
    else:
        relative = Path(path.name)
    return {
        "path": relative.as_posix(),
        "size": len(blob),
        "sha256": recovery.sha256(blob),
    }


def collect_existing(
    progress_path: Path, target_catalog_path: Path = recovery.DEFAULT_TARGET_CATALOG
) -> dict[str, Any]:
    history = recovery.collect_overlay_history(
        progress_path,
        target_catalog_path=target_catalog_path,
        predecessor_boundary_relative=PREDECESSOR_BOUNDARY_RELATIVE,
        predecessor_paths_pin=PREDECESSOR_PATHS_PIN,
        predecessor_coordinate_count=PREDECESSOR_COORDINATE_COUNT,
        self_relative=SELF_RELATIVE,
        self_batch_id=BATCH_ID,
        self_coordinate_count=53,
        self_coordinates_pin=SELF_COORDINATES_PIN,
        self_overlay_sha256=SELF_OVERLAY_SHA256,
    )
    paths = history["predecessor_paths"]
    return {
        "coordinates": history["predecessor_coordinates"],
        "paths": paths,
        "self_registration_count": history["self_registration_count"],
        "normalized_input_sha256": recovery.canonical_hash(paths),
        "successor_coordinates": history["successor_coordinates"],
        "successor_paths": history["successor_paths"],
    }


def review_window() -> tuple[list[tuple[int, int, int]], dict[tuple[int, int, int], dict[str, Any]]]:
    if recovery.sha256(PRIOR_REVIEW.read_bytes()) != PRIOR_REVIEW_PIN:
        raise BatchError("prior invariant-recovery review pin changed")
    prior_review = read_json(PRIOR_REVIEW)
    excluded = [
        item
        for item in prior_review.get("entries", [])
        if isinstance(item, dict) and item.get("status") == "excluded"
    ]
    excluded.sort(key=lambda item: (item["block_id"], item["record_id"], item["literal_id"]))
    if len(excluded) != 1_879:
        raise BatchError("prior exclusion pool changed")
    window_items = excluded[:100]
    coordinates = [(item["block_id"], item["record_id"], item["literal_id"]) for item in window_items]
    if recovery.canonical_hash([list(value) for value in coordinates]) != WINDOW_PIN:
        raise BatchError("first 100-coordinate review window changed")
    return coordinates, {coordinate: item for coordinate, item in zip(coordinates, window_items)}


def assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = recovery.script_counts(path.read_text(encoding="utf-8"))
        result[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise BatchError(f"commercial source script leaked into artifact: {path}")
    return result


def build(args: argparse.Namespace) -> dict[str, Any]:
    v13_path = args.switch_v13_zip.resolve()
    v11_path = args.switch_v11_zip.resolve()
    base_jp_path = args.base_jp.resolve()
    pk_jp_path = args.pk_jp.resolve()
    pk_sc_path = args.pk_sc.resolve()
    progress_path = args.progress.resolve()
    target_path = args.target_catalog.resolve()
    input_paths = (v13_path, v11_path, base_jp_path, pk_jp_path, pk_sc_path, progress_path, target_path, PRIOR_REVIEW)
    before = {str(path): recovery.sha256(path.read_bytes()) for path in input_paths}

    v13 = recovery.load_switch(v13_path, recovery.V13_ZIP_PIN)
    v11 = recovery.load_switch(v11_path, recovery.V11_ZIP_PIN)
    if v13["packed"] != v11["packed"] or v13["raw"] != v11["raw"]:
        raise BatchError("Switch v1.3 msggame text differs from pinned v1.1")
    base_jp = recovery.prior.load_standard_source(base_jp_path, "base_jp")
    pk_jp = recovery.prior.load_standard_source(pk_jp_path, "pk_jp")
    pk_sc = recovery.prior.load_standard_source(pk_sc_path, "pk_sc")
    target = recovery.load_target_catalog(target_path)
    existing = collect_existing(progress_path, target_path)
    window, prior_by_coordinate = review_window()

    selected_coordinates = sorted(TRANSLATIONS)
    selected_set = set(selected_coordinates)
    window_set = set(window)
    if len(TRANSLATIONS) != 53:
        raise BatchError(f"translation count changed: {len(TRANSLATIONS)}")
    if not selected_set <= window_set:
        raise BatchError("translation escaped the first 100-coordinate review window")
    if selected_set & existing["coordinates"]:
        raise BatchError("translation overlaps an existing PK msggame overlay")
    if not selected_set <= target["coordinates"]:
        raise BatchError("translation escaped the exact target catalog")

    base_literals = recovery.literal_map(base_jp["archive"])
    switch_literals = recovery.literal_map(v13["archive"])
    pk_jp_literals = recovery.literal_map(pk_jp["archive"])
    pk_sc_literals = recovery.literal_map(pk_sc["archive"])
    switch_values, source_occurrences = recovery.prior.build_switch_value_map(
        base_literals,
        switch_literals,
        recovery.prior.record_map(base_jp["archive"]),
        recovery.prior.record_map(v13["archive"]),
    )

    selected: list[dict[str, Any]] = []
    for coordinate in selected_coordinates:
        source = pk_sc_literals[coordinate].text
        pk_jp_text = pk_jp_literals[coordinate].text
        replacement = TRANSLATIONS[coordinate]
        switch_candidates = switch_values.get(recovery.text_hash(pk_jp_text), set())
        if len(switch_candidates) != 1:
            raise BatchError(f"Switch Korean literal alignment is not unique at {coordinate}")
        prior_item = prior_by_coordinate[coordinate]
        if prior_item.get("pk_jp_utf16le_sha256") != recovery.text_hash(pk_jp_text):
            raise BatchError(f"PK JP hash changed at {coordinate}")
        if prior_item.get("pk_sc_utf16le_sha256") != recovery.text_hash(source):
            raise BatchError(f"PK SC hash changed at {coordinate}")
        if prior_item.get("switch_ko_utf16le_sha256") != recovery.text_hash(next(iter(switch_candidates))):
            raise BatchError(f"Switch Korean hash changed at {coordinate}")
        mismatches = recovery.invariant_mismatches(source, replacement)
        if mismatches:
            raise BatchError(f"invariant mismatch at {coordinate}: {mismatches}")
        if recovery.msggame_translation.bracket_sequence(source) != recovery.msggame_translation.bracket_sequence(replacement):
            raise BatchError(f"bracket sequence changed at {coordinate}")
        if recovery.delimiter_roles(source) != recovery.delimiter_roles(replacement):
            raise BatchError(f"delimiter roles changed at {coordinate}")
        if recovery.script_counts(replacement) != {"cjk_unified_count": 0, "kana_count": 0}:
            raise BatchError(f"forbidden source script remains at {coordinate}")
        if not recovery.prior.has_hangul_syllable(replacement):
            raise BatchError(f"replacement lacks Hangul at {coordinate}")
        selected.append(
            {
                "coordinate": coordinate,
                "replacement": replacement,
                "pk_jp_hash": recovery.text_hash(pk_jp_text),
                "pk_sc_hash": recovery.text_hash(source),
                "switch_ko_hash": recovery.text_hash(next(iter(switch_candidates))),
                "replacement_hash": recovery.text_hash(replacement),
                "source_occurrences": source_occurrences[recovery.text_hash(pk_jp_text)],
                "source_structure": recovery.source_structure(source),
                "replacement_structure": recovery.source_structure(replacement),
            }
        )

    excluded_coordinates = sorted(window_set - selected_set)
    if len(excluded_coordinates) != 47:
        raise BatchError("review-window exclusion count changed")
    selected_hash = recovery.canonical_hash([list(value) for value in selected_coordinates])
    excluded_hash = recovery.canonical_hash([list(value) for value in excluded_coordinates])

    overlay_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "source_sc_utf16le_sha256": item["pk_sc_hash"],
            "ko": item["replacement"],
        }
        for item in selected
    ]
    overlay = {
        "schema": recovery.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "migration_provenance": {
            "kind": "third_party_switch_v13_agent_semantic_record_review",
            "author": "snake7594",
            "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
            "release_tag": "v1.3",
            "asset_sha256": recovery.V13_ZIP_PIN["sha256"],
            "v13_text_identical_to_v11": True,
            "source_text_embedded": False,
        },
        "stock_sc": {
            "packed_size": len(pk_sc["packed"]),
            "packed_sha256": recovery.sha256(pk_sc["packed"]),
            "raw_size": len(pk_sc["raw"]),
            "raw_sha256": recovery.sha256(pk_sc["raw"]),
            "record_count": pk_sc["archive"].record_count,
            "literal_slot_count": len(pk_sc_literals),
        },
        "entries": overlay_entries,
    }

    evidence_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "review_method": "agent_semantic_full_record_context",
            "pk_jp_utf16le_sha256": item["pk_jp_hash"],
            "pk_sc_utf16le_sha256": item["pk_sc_hash"],
            "switch_ko_utf16le_sha256": item["switch_ko_hash"],
            "replacement_utf16le_sha256": item["replacement_hash"],
            "source_occurrence_count": item["source_occurrences"],
            "pk_sc_structure": item["source_structure"],
            "replacement_structure": item["replacement_structure"],
            "complete_record_context_reviewed": True,
            "not_mechanical_literal_split": True,
            "invariants_exact": True,
            "bracket_sequence_equal": True,
            "delimiter_role_sequence_equal": True,
        }
        for item in selected
    ]
    evidence = {
        "schema": "nobu16.kr.switch-msggame-v13-semantic-review-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "source_free": True,
        "provenance": {
            "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
            "v13_zip_sha256": recovery.V13_ZIP_PIN["sha256"],
            "v11_zip_sha256": recovery.V11_ZIP_PIN["sha256"],
            "v13_v11_msggame_byte_identical": True,
            "msggame_packed_sha256": recovery.SWITCH_TEXT_PIN["packed_sha256"],
            "prior_review_path": PRIOR_REVIEW.relative_to(REPO_ROOT).as_posix(),
            "prior_review_sha256": PRIOR_REVIEW_PIN,
        },
        "review_window": {
            "policy": "coordinate_sorted_first_100_prior_exclusions",
            "count": len(window),
            "coordinates_sha256": WINDOW_PIN,
            "first_coordinate": list(window[0]),
            "last_coordinate": list(window[-1]),
            "translated": len(selected),
            "excluded": len(excluded_coordinates),
        },
        "target_catalog": {
            "path": target_path.relative_to(REPO_ROOT).as_posix(),
            "coordinate_count": len(target["coordinates"]),
            "coordinates_sha256": target["hash"],
            "selected_is_subset": True,
        },
        "existing_overlay_exclusion": {
            "coordinate_union": len(existing["coordinates"]),
            "resolved_paths": existing["paths"],
            "normalized_input_sha256": existing["normalized_input_sha256"],
            "self_path": SELF_RELATIVE,
            "self_registration_states_supported": [0, 1],
            "self_excluded_before_selection": True,
        },
        "selected_coordinates_sha256": selected_hash,
        "excluded_coordinates_sha256": excluded_hash,
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "status": "translated",
            "review_method": "agent_semantic_full_record_context",
            "semantic_review_completed": True,
            "human_review_required": True,
            "runtime_reviewed": False,
        }
        for item in selected
    ] + [
        {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
            "status": "excluded",
            "reason": exclusion_reason(coordinate),
            "semantic_review_completed": True,
            "human_review_required": True,
            "runtime_reviewed": False,
        }
        for coordinate in excluded_coordinates
    ]
    review = {
        "schema": "nobu16.kr.switch-msggame-v13-semantic-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "agent_semantic_review_safe_subset_translated_ambiguous_excluded",
        "window_count": len(window),
        "selected_count": len(selected),
        "excluded_count": len(excluded_coordinates),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts = {
        "overlay": write_json(overlay_path, overlay),
        "evidence": write_json(evidence_path, evidence),
        "review": write_json(review_path, review),
    }
    source_free_scan = assert_source_free((overlay_path, evidence_path, review_path))

    rebuilt, binary_manifest = recovery.apply_overlay_blob(pk_sc["packed"], overlay)
    parsed = recovery.parse_packed_msggame(rebuilt)
    rebuilt_literals = recovery.literal_map(parsed.archive)
    if set(rebuilt_literals) != set(pk_sc_literals):
        raise BatchError("offline reconstruction changed literal coordinates")
    for item in selected:
        if rebuilt_literals[item["coordinate"]].text != item["replacement"]:
            raise BatchError(f"offline replacement mismatch at {item['coordinate']}")

    after = {str(path): recovery.sha256(path.read_bytes()) for path in input_paths}
    if before != after:
        raise BatchError("read-only input changed during build")
    validation = {
        "schema": "nobu16.kr.switch-msggame-v13-semantic-review-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "review_window": {"count": 100, "translated": len(selected), "excluded": len(excluded_coordinates)},
        "coordinate_sets": {
            "selected_sha256": selected_hash,
            "excluded_sha256": excluded_hash,
            "selected_excluded_disjoint": True,
            "selected_existing_disjoint": True,
            "selected_target_subset": True,
        },
        "proofs": {
            "complete_pk_record_context_semantically_reviewed": True,
            "switch_korean_meaning_consulted": True,
            "mechanical_literal_split_forbidden": True,
            "all_replacements_preserve_pk_sc_invariants": True,
            "all_replacements_preserve_bracket_sequence": True,
            "all_replacements_preserve_delimiter_role_sequence": True,
            "ambiguous_coordinates_excluded": True,
            "v13_msggame_byte_identical_to_v11": True,
            "self_registration_states_supported": [0, 1],
            "self_registration_does_not_feed_selection": True,
            "later_overlay_registration_does_not_feed_selection": True,
            "later_overlays_source_free_target_only_and_disjoint": True,
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": recovery.sha256(rebuilt),
            "literal_coordinates_preserved": True,
            "installed_game_file_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": recovery.sha256(SCRIPT_PATH.read_bytes())},
        "safety": {
            "installed_game_files_modified": False,
            "executable_modified": False,
            "dll_injection": False,
            "process_memory_access": False,
            "registry_modified": False,
            "root_progress_modified": False,
            "root_readme_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_artifact = write_json(validation_path, validation)
    return {
        "entry_count": len(selected),
        "excluded_count": len(excluded_coordinates),
        "review_window_count": len(window),
        "selected_coordinates_sha256": selected_hash,
        "excluded_coordinates_sha256": excluded_hash,
        "target_packed_sha256": recovery.sha256(rebuilt),
        "artifacts": {**artifacts, "validation": validation_artifact},
        "self_registration_count": existing["self_registration_count"],
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--switch-v13-zip", type=Path, default=recovery.DEFAULT_V13_ZIP)
    value.add_argument("--switch-v11-zip", type=Path, default=recovery.DEFAULT_V11_ZIP)
    value.add_argument("--base-jp", type=Path, default=GAME_ROOT / "MSG" / "JP" / "msggame.bin")
    value.add_argument("--pk-jp", type=Path, default=GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin")
    value.add_argument("--pk-sc", type=Path, default=recovery.DEFAULT_PK_SC)
    value.add_argument("--progress", type=Path, default=recovery.DEFAULT_PROGRESS)
    value.add_argument("--target-catalog", type=Path, default=recovery.DEFAULT_TARGET_CATALOG)
    value.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return value


def main() -> int:
    result = build(parser().parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
