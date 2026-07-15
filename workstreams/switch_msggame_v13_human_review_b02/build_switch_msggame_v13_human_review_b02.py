#!/usr/bin/env python3
"""Build semantic-review batch B02 from exclusions 101 through 200."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
B01_ROOT = REPO_ROOT / "workstreams" / "switch_msggame_v13_human_review_b01"
sys.path.insert(0, str(B01_ROOT))

import build_switch_msggame_v13_human_review_b01 as base  # noqa: E402


recovery = base.recovery
BATCH_ID = "switch_v13_pk_msggame_semantic_review_b02_68.v1"
RESOURCE = recovery.RESOURCE
OVERLAY_NAME = "msggame_ko_switch_v13_semantic_review_b02_68.v1.json"
EVIDENCE_NAME = "switch_v13_pk_msggame_semantic_review_b02_evidence.v1.json"
REVIEW_NAME = "switch_v13_pk_msggame_semantic_review_b02_review.v1.json"
VALIDATION_NAME = "switch_v13_pk_msggame_semantic_review_b02_validation.v1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()
B01_RELATIVE = (
    B01_ROOT / "public" / base.OVERLAY_NAME
).relative_to(REPO_ROOT).as_posix()
PREDECESSOR_PATHS_PIN = "1F0AE417EBEA096BF635AEB083C0704978E7FF663A691DA052A7CF5E8A8B71EA"
PREDECESSOR_COORDINATE_COUNT = 9_951
SELF_COORDINATES_PIN = "13C30CC6D6118211BC318B3CFDAF2A268B26A97698921E369FE13C9D7CCC5A2D"
SELF_OVERLAY_SHA256 = "1656637F64B7EA30C284AA9DE229A636A93CD14E90EF92F25A1FB6F838F47359"
PRIOR_REVIEW = base.PRIOR_REVIEW
PRIOR_REVIEW_PIN = base.PRIOR_REVIEW_PIN
WINDOW_PIN = "C6C33F0F4249670A8A7229C5107264A04FA106DCF9AF3BA2FE10314B657C9CAD"


TRANSLATIONS: dict[tuple[int, int, int], str] = {
    (6, 4196, 2): "출진 전까지 영내를 발전시키겠습니다.",
    (6, 4199, 0): "주명을 받들어 가중의 의견을 모았습니다.\n실행할 만한 제안이 있는 듯하니,\n확인 후 결정해 주십시오.",
    (6, 4200, 0): "주명을 가중에 알렸더니,\n방침에 맞는 제안이 나온 듯합니다.\n승인 여부를 확인해 주십시오.",
    (6, 4202, 0): "주명을 받들어 가중의 의견을 모았으나,\n실행할 만한 제안이 없는 듯합니다.\n힘이 미치지 못해 면목이 없습니다…",
    (6, 4205, 0): "명을 받들겠습니다.\n반드시 주명에 걸맞은 성과를\n당가에 가져오겠습니다.",
    (6, 4206, 0): "예, 명을 받들어,\n당가를 위해 주명 완수에 전력을 다하겠습니다.",
    (6, 4207, 1): "겠습니다.\n공을 세운 자에게는 큰 포상을 내리니,\n모두 힘써 주십시오.",
    (6, 4208, 0): "적성 조략의 뜻을 각 성주에게 전하자,\n다음 성에 관한 구체안이 나왔습니다.\n어느 성주의 책략을 실행할지 지시해 주십시오.",
    (6, 4209, 0): "영내 여러 책략의 뜻을 각 성주에게 전하자,\n다음 성에 관한 구체안이 나왔습니다.\n어느 성을 강화할지 지시해 주십시오.",
    (6, 4211, 0): "대상 성에 내린 명령을 취소하시겠습니까?",
    (6, 4249, 0): "조정과 교섭 중인 무장을 해임하시겠습니까?",
    (6, 4251, 0): "조정과의 교섭을 중단했습니다.",
    (6, 4257, 2): "의 영주로 임명합니다.\n성 능력: 통",
    (6, 4323, 0): "바람처럼 전장을 내달리자!\n이제",
    (6, 4384, 1): "발령 준비에 착수하겠습니다.",
    (6, 4387, 0): "명을 받들겠습니다.\n즉시",
    (6, 4388, 1): "의 발령을 이루겠습니다.",
    (6, 4389, 0): "의 발령은 훌륭한 방안입니다.\n즉시 준비에 착수합시다.",
    (6, 4395, 0): "알겠습니다.\n다른 가문보다 앞서기 위해,\n서둘러",
    (6, 4395, 1): "의 개량에 착수하겠습니다.",
    (6, 4402, 0): "동맹을 맺은 당가를 경계하여,\n상대",
    (6, 4403, 0): "동맹을 맺은 당가를 경계하여,\n관련",
    (6, 4404, 0): "동맹을 맺은 당가를 경계하여,\n상대",
    (6, 4405, 0): "동맹을 맺은 당가를 경계하여,\n관련",
    (6, 4409, 1): "님께 더 많은 영지를 내리면,\n그 영지가 더욱 번영할 것입니다.",
    (6, 4411, 3): "개의 맡길 수 있는 군이 있습니다.\n이를",
    (6, 4412, 0): "승진한 성주에게 영지를 더 내리면,\n그 땅도 더욱 번영할 것입니다.\n군다이가 다스리는 영지를 맡겨 보시겠습니까?",
    (6, 4418, 0): "명을 받들겠습니다. 필요하다면,\n“지행”에서 다시 명령해 주십시오.",
    (6, 4419, 1): "이 당가에서 독립했습니다.\n이후",
    (6, 4420, 1): "에서 독립했습니다.\n이후",
    (6, 4424, 0): "판단을 내리기 어렵습니다.\n방침을 지시해 주신다면,\n정책 “",
    (6, 4424, 1): "”을 재검토하겠습니다…",
    (6, 4425, 0): "의 성하에는,\n그 방침에 능한 장수가 없습니다.\n인원 배치를 다시 검토해 주십시오.",
    (6, 4427, 0): "현재 인원이 부족하여,\n진행하기 어려울 듯합니다.",
    (6, 4428, 0): "좋은 제안이라고 생각합니다.\n현재",
    (6, 4430, 1): "를 보여 줄 때입니다.\n성과를 기대해 주십시오.",
    (6, 4431, 1): "있으니,\n문제없이 완수할 수 있습니다.",
    (6, 4433, 0): "우리 성에는 건설에 능한 자가 있어,\n정책 「",
    (6, 4433, 1): "」 발령 뒤,\n다음",
    (6, 4436, 0): "성하의 석고를 늘리면,\n다음",
    (6, 4436, 1): "도 세울 수 있습니다.",
    (6, 4438, 0): "제게 맡겨 주십시오.\n훌륭한 성하를 만들겠습니다.",
    (6, 4439, 1): "\n모두 전력을 다하겠습니다.",
    (6, 4440, 0): "방침을 받들었습니다.\n이제 실현하기만 하면 됩니다.",
    (6, 4442, 0): "명을 받들겠습니다.\n임무와 전투가 끝나는 대로,\n착수하겠습니다.",
    (6, 4443, 0): "명을 받들겠습니다.\n전투에서 돌아오는 대로,\n착수하겠습니다.",
    (6, 4444, 0): "명을 받들겠습니다.\n임무가 끝나는 대로,\n착수하겠습니다.",
    (6, 4445, 1): "님이\n다스리는",
    (6, 4450, 1): "주십시오.\n적의 어떤 조략도\n막아 보이겠습니다.",
    (6, 4451, 0): "방비를 강화해야 할 땅이니,\n아무래도",
    (6, 4453, 0): "전선이라니, 솜씨를 보일 기회로군요.\n저를",
    (6, 4453, 1): "배속한다면,\n부대 방비 강화에 공헌하겠습니다.",
    (6, 4454, 0): "과연, 제 창 솜씨를 눈여겨보셨군요.\n하지만… 인선은 다시 검토해 주십시오.",
    (6, 4455, 0): "설마,",
    (6, 4455, 1): "라니, 바라던 바입니다!\n부디 제게 맡겨,\n무공을 세우게 해 주십시오!",
    (6, 4458, 1): "을 맡겨 주십시오.\n포위전으로 성을 공격한다면,\n",
    (6, 4461, 1): "을 배속해 주십시오.",
    (6, 4464, 0): "부디 배속을 명해 주십시오.\n그 성에는,",
    (6, 4465, 1): "에는\n아마,",
    (6, 4466, 0): "나와 같은 특성을 지닌 동료가\n성 안에 있는 듯합니다.\n제 강점을 발휘할 수 있겠습니다.",
    (6, 4467, 0): "제 특성은 전선에서 빛을 발합니다…\n그렇지만 가능하다면,\n부디,",
    (6, 4472, 1): "에게 맡겨 주십시오!\n",
    (6, 4473, 0): "적지에 접한 땅이라면,\n제 조략 솜씨를 보일 기회가 있을지도 모릅니다.",
    (6, 4474, 0): "취락 장악 진척이 더디군요.\n확실히,",
    (6, 4474, 1): "은 장악에 능하지만,\n다른 인선을 찾아 주시기를 바랍니다…",
    (6, 4478, 0): "성민의 사기를 높이는 일은,\n분명 제 장기입니다만…\n다만,",
    (6, 4479, 1): "에게 맡겨 주십시오.\n성민의 사기를 높여,\n전력을 크게 끌어올리겠습니다.",
    (6, 4481, 1): "\n와는 분명 마음이 잘 맞습니다만…",
}


class BatchError(ValueError):
    """Raised when a pinned input or structural contract changes."""


def exclusion_reason(coordinate: tuple[int, int, int]) -> str:
    record_id = coordinate[1]
    if record_id in {4241, 4242, 4243, 4244, 4245, 4246, 4252, 4364, 4386, 4390, 4407, 4408, 4415, 4417, 4426, 4429, 4434, 4437, 4452, 4459, 4471, 4475, 4476}:
        return "dynamic_boundary_or_adjacent_fragment_ambiguous"
    if record_id in {4257, 4326, 4386, 4387, 4396, 4433, 4437, 4453, 4455, 4459}:
        return "korean_word_order_crosses_untranslated_dynamic_boundary"
    if record_id == 4475:
        return "adjacent_existing_translation_conflict"
    return "partial_record_context_not_safe_for_isolated_coordinate"


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
    relative = Path(path.parent.name) / path.name if path.parent.name in {"public", "evidence", "review"} else Path(path.name)
    return {"path": relative.as_posix(), "size": len(blob), "sha256": recovery.sha256(blob)}


def collect_existing(
    progress_path: Path, target_catalog_path: Path = recovery.DEFAULT_TARGET_CATALOG
) -> dict[str, Any]:
    history = recovery.collect_overlay_history(
        progress_path,
        target_catalog_path=target_catalog_path,
        predecessor_boundary_relative=B01_RELATIVE,
        predecessor_paths_pin=PREDECESSOR_PATHS_PIN,
        predecessor_coordinate_count=PREDECESSOR_COORDINATE_COUNT,
        self_relative=SELF_RELATIVE,
        self_batch_id=BATCH_ID,
        self_coordinate_count=68,
        self_coordinates_pin=SELF_COORDINATES_PIN,
        self_overlay_sha256=SELF_OVERLAY_SHA256,
    )
    resolved = sorted(history["predecessor_paths"])
    return {
        "coordinates": history["predecessor_coordinates"],
        "paths": resolved,
        "self_registration_count": history["self_registration_count"],
        "normalized_input_sha256": recovery.canonical_hash(resolved),
        "successor_coordinates": history["successor_coordinates"],
        "successor_paths": history["successor_paths"],
    }


def review_window() -> tuple[list[tuple[int, int, int]], dict[tuple[int, int, int], dict[str, Any]]]:
    if recovery.sha256(PRIOR_REVIEW.read_bytes()) != PRIOR_REVIEW_PIN:
        raise BatchError("prior invariant-recovery review pin changed")
    prior_review = read_json(PRIOR_REVIEW)
    excluded = [item for item in prior_review.get("entries", []) if isinstance(item, dict) and item.get("status") == "excluded"]
    excluded.sort(key=lambda item: (item["block_id"], item["record_id"], item["literal_id"]))
    if len(excluded) != 1_879:
        raise BatchError("prior exclusion pool changed")
    window_items = excluded[100:200]
    coordinates = [(item["block_id"], item["record_id"], item["literal_id"]) for item in window_items]
    if recovery.canonical_hash([list(value) for value in coordinates]) != WINDOW_PIN:
        raise BatchError("B02 100-coordinate review window changed")
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
    if len(TRANSLATIONS) != 68:
        raise BatchError(f"translation count changed: {len(TRANSLATIONS)}")
    if not selected_set <= window_set:
        raise BatchError("translation escaped the B02 review window")
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
        source_hash = recovery.text_hash(pk_jp_text)
        switch_candidates = switch_values.get(source_hash, set())
        if len(switch_candidates) != 1:
            raise BatchError(f"Switch Korean literal alignment is not unique at {coordinate}")
        switch_ko = next(iter(switch_candidates))
        prior_item = prior_by_coordinate[coordinate]
        if prior_item.get("pk_jp_utf16le_sha256") != source_hash:
            raise BatchError(f"PK JP hash changed at {coordinate}")
        if prior_item.get("pk_sc_utf16le_sha256") != recovery.text_hash(source):
            raise BatchError(f"PK SC hash changed at {coordinate}")
        if prior_item.get("switch_ko_utf16le_sha256") != recovery.text_hash(switch_ko):
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
                "pk_jp_hash": source_hash,
                "pk_sc_hash": recovery.text_hash(source),
                "switch_ko_hash": recovery.text_hash(switch_ko),
                "replacement_hash": recovery.text_hash(replacement),
                "source_occurrences": source_occurrences[source_hash],
                "source_structure": recovery.source_structure(source),
                "replacement_structure": recovery.source_structure(replacement),
            }
        )

    excluded_coordinates = sorted(window_set - selected_set)
    if len(excluded_coordinates) != 32:
        raise BatchError(f"review-window exclusion count changed: {len(excluded_coordinates)}")
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
            "policy": "coordinate_sorted_prior_exclusions_101_through_200",
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
            "b01_forced_into_union": True,
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
    review = {
        "schema": "nobu16.kr.switch-msggame-v13-semantic-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "agent_semantic_review_safe_subset_translated_ambiguous_excluded",
        "window_count": len(window),
        "selected_count": len(selected),
        "excluded_count": len(excluded_coordinates),
        "entries": [
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
        ],
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
            "selected_b01_disjoint": True,
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
