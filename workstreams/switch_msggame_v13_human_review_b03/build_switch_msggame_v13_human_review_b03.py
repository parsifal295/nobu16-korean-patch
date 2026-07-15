#!/usr/bin/env python3
"""Build the third source-free semantic-review batch for PK msggame."""

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
B02_ROOT = REPO_ROOT / "workstreams" / "switch_msggame_v13_human_review_b02"
sys.path.insert(0, str(B02_ROOT))

import build_switch_msggame_v13_human_review_b02 as previous  # noqa: E402


recovery = previous.recovery
BATCH_ID = "switch_v13_pk_msggame_semantic_review_b03_130.v1"
RESOURCE = recovery.RESOURCE
OVERLAY_NAME = "msggame_ko_switch_v13_semantic_review_b03_130.v1.json"
EVIDENCE_NAME = "switch_v13_pk_msggame_semantic_review_b03_evidence.v1.json"
REVIEW_NAME = "switch_v13_pk_msggame_semantic_review_b03_review.v1.json"
VALIDATION_NAME = "switch_v13_pk_msggame_semantic_review_b03_validation.v1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()
PRIOR_REVIEW = previous.PRIOR_REVIEW
PRIOR_REVIEW_PIN = previous.PRIOR_REVIEW_PIN
B02_RELATIVE = (
    B02_ROOT / "public" / previous.OVERLAY_NAME
).relative_to(REPO_ROOT).as_posix()
WINDOW_PIN = "7D5B3F331AFBECE3FD79E64C70B29DB79D4608D67B6D1F860261A964D96FF96A"
PREDECESSOR_PATHS_PIN = "22E0FCF4E6A99749112F2AB041C85BE6BA1711C4B933BE1A2A2F3A052B67E877"
PREDECESSOR_COORDINATE_COUNT = 10_019
SELF_COORDINATES_PIN = "8621BF3F6BCD119A51226C18CB10BAA10F69BFEADE204D44139BEFD2C2A34BCD"
SELF_OVERLAY_SHA256 = "6279D3C7D7139EED15670309F7DAD3E993359821985DA3194E392439B3C77302"


# The replacements follow the exact SC literal coordinates.  Several records
# order dynamic values differently from JP, so these are contextual rewrites,
# not mechanically trimmed Switch strings.
TRANSLATIONS: dict[tuple[int, int, int], str] = {
    (6, 4482, 2): "성주와 잘 지낼 자신이",
    (6, 4485, 0): "전선이라 가슴이 뛰는군요.\n부디 저를 영주로 임명해 주십시오.",
    (6, 4487, 0): "적령과 가까운 전선이니,\n바로",
    (6, 4488, 1): "\n그곳에서는 솜씨를 마음껏 발휘하기 어렵겠군요……",
    (6, 4492, 0): "당가의 손길이\n거의 닿지 않은 땅이군요……\n힘쓸 보람이 있겠습니다.",
    (6, 4493, 0): "……할 일이 많아 보이는 땅이군요.\n영주의 수완을 시험하기에 제격입니다.",
    (6, 4494, 0): "참으로 안정된 땅이군요.\n안심하고 부임할 수 있겠습니다.",
    (6, 4495, 0): "그곳에 배속된다면,\n할 일을 찾아야겠군요.\n참으로 잘 정비된 땅입니다.",
    (6, 4500, 0): "머, 멀군요……\n아니, 명만 내리시면\n즉시 길 떠날 채비를 하겠습니다.",
    (6, 4501, 0): "특별한 뜻은 없습니다만,\n배속하실 분이",
    (6, 4501, 1): "라면,\n거리가 멀어 부임에 시간이 걸리겠습니다……",
    (6, 4504, 1): "\n관계가 좋지도 나쁘지도 않으니,\n문제없이 일할 수 있을 듯합니다.",
    (6, 4507, 0): "아직 여력이 있으니,\n성주인",
    (6, 4507, 1): "도 겸임할 수 있습니다.",
    (6, 4509, 0): "아직 더 할 수 있습니다.\n해임하지 말아 주십시오.",
    (6, 4510, 0): "설마 해임을 생각하고 계십니까?\n부디 다시 생각해 주십시오……",
    (6, 4517, 0): "도움을 준",
    (6, 4551, 1): "은(는) 큰 불만을 품고 있어,\n언제 출분해도 이상하지 않습니다.\n부디",
    (6, 4553, 1): "등용이 순조롭지 않습니다.\n하지만 이 사람은 명성이 높은 인재이니, 부디",
    (6, 4562, 3): "이(가) 우리에게 항복하겠다고 합니다.\n더 나은 조건을 얻도록 교섭하시겠습니까?",
    (6, 4563, 3): "이(가) 우리에게 항복하겠다고 합니다.\n더 나은 조건을 얻도록 교섭하시겠습니까?",
    (6, 4564, 1): "빼내기가 순조롭게 진행되어,\n성째로 배반할 뜻도 있는 듯합니다.\n자세한 사정은",
    (6, 4566, 2): "\n빼내기에 응해 성째로 배반할 뜻도 있다 합니다.\n자세한 사정은",
    (6, 4567, 2): "\n빼내기에 응해 성째로 배반할 뜻도 있다 합니다.\n자세한 사정은",
    (6, 4577, 0): "그렇습니까, 어쩔 수 없군요.\n붙잡는 일은 포기하겠습니다.",
    (6, 4579, 0): "알겠습니다, 참으로 아쉽군요.\n하지만",
    (6, 4582, 0): "그렇다면 성째로 배반시키는 것은 포기하고,\n대신",
    (6, 4590, 0): "!\n설마",
    (6, 4591, 0): "직접 찾아오실 줄이야……\n그만큼 중요한 일이라는 뜻이군요.",
    (6, 4594, 1): "께서 직접 오시다니,\n그토록",
    (6, 4599, 1): "입니까?\n소인은",
    (6, 4624, 2): "입니다.\n원하는 것이 있다면 말씀하십시오.",
    (6, 4636, 1): "은(는) 보기 드문 인재입니다.\n사람의 마음은 작은 일에도 바뀌는 법이지요.\n가령 바람을 이루어 드린다면……?",
    (6, 4675, 0): "더는 싸우고 싶지 않지만,\n상대가",
    (6, 4707, 0): "그렇군요, 어쩔 수 없습니다.\n끝내 뜻을 함께하지 못하는군요……",
    (6, 4709, 0): "그렇군요……참으로 아쉽습니다.\n어디서부터 어긋난 것일까요……",
    (6, 4712, 0): "그렇군요……참으로 아쉽습니다.\n다음에 만날 때는,\n전장에서 적으로 만나지 않기를 바랍니다.",
    (6, 4716, 0): "그렇군요……\n받아들이지 않으니 아쉽지만,\n어쩔 수 없습니다.",
    (6, 4756, 1): "의 마음은 잘 받았습니다.\n언제든 다시 찾아오십시오.",
    (6, 4761, 0): "만약",
    (6, 4762, 0): "등용을 포기할 대상은",
    (6, 4763, 0): "등용을 포기할 대상은",
    (6, 4766, 0): "제안을 거절할 상대는",
    (6, 4767, 0): "빼내기를 포기할 대상은",
    (6, 4768, 0): "정전 교섭을 중지할 상대는",
    (6, 4769, 0): "양여를 중지할 상대는",
    (6, 4783, 1): "이 있는 성의 영지를\n관리할 인물은",
    (6, 4809, 2): "로 임명한다는 약속,\n잊지 마십시오.",
    (6, 4840, 0): "알겠습니다.\n즉시 준비하겠습니다.",
    (6, 4841, 0): "알겠습니다.\n즉시 준비하겠습니다.",
    (6, 4842, 0): "알겠습니다.\n즉시 준비하겠습니다.",
    (6, 4846, 0): "알겠습니다.\n즉시 준비하겠습니다.",
    (6, 4855, 0): "알겠습니다.\n이 성은 목숨을 걸고 지키겠습니다.",
    (6, 4856, 0): "알겠습니다.\n이 성은 목숨을 걸고 지키겠습니다.",
    (6, 4857, 0): "알겠습니다.\n이 성은 목숨을 걸고 지키겠습니다.",
    (6, 4861, 0): "알겠습니다.\n이 성은 목숨을 걸고 지키겠습니다.",
    (6, 4907, 1): ".\n지금은 교섭할 일이 없지만,\n이번 친선이 의미를 갖는 때가 올 것입니다.",
    (6, 4915, 1): ",\n약속대로",
    (7, 221, 0): "적장을 포박했습니다.\n붙잡힌 무장의 처우를 결정해 주십시오.",
    (7, 264, 0): "……이렇게 된 이상 어쩔 수 없군요.\n이제부터 귀가를 섬기겠습니다.",
    (7, 265, 1): "도량에 감사드립니다.\n이제부터 충성을 다하겠습니다.",
    (7, 266, 0): "권유에 감사드립니다.\n포로가 되었던 오명은 공으로 씻고,\n충성을 다하겠습니다.",
    (7, 267, 1): "을 위해 일하라니,\n어쩔 수 없군요.\n기꺼이 힘을 다하겠습니다.",
    (7, 268, 1): "의 휘하에서 일하는 데,\n아무런 이의가 없습니다.",
    (7, 269, 0): "귀가의 부름, 감사히 받겠습니다.\n특히",
    (7, 272, 0): "……옛 주군을 잊기는 어렵지만,\n이 또한 난세의 이치겠지요.\n앞으로 잘 부탁드립니다.",
    (7, 273, 0): "당가가 천하를 다스릴 길은 끊겼습니다……\n이제부터",
    (7, 276, 0): "……목숨을 구해 주신 은혜를 갚고자,\n이제",
    (7, 276, 1): "을 섬기겠습니다.\n이 또한 인연이겠지요……",
    (7, 277, 0): "은(는) 저를 놓아준 은인이십니다.\n다시 불러 주신 이상,\n따르는 수밖에 없습니다.",
    (7, 278, 0): "사로잡힌 저를 풀어 주신 은혜,\n결코 잊지 않겠습니다.\n분골쇄신하여",
    (7, 284, 1): "명이 사로잡혀,\n이제",
    (7, 325, 2): "을 섬길 수는 없다!",
    (7, 326, 0): "웃기지도 않는 농담이군.\n내 마음속 증오의 불길은\n그리 쉽게 꺼지지 않는다.",
    (7, 327, 0): "거절한다.\n네가 저지른 악행부터 돌아보아라.",
    (7, 332, 0): "에게도 긍지가 있습니다.\n조금 전까지 적이었던 자를 주군으로 섬길 수는 없습니다.",
    (7, 333, 1): "은(는) 나의 대망을 꺾은 원수입니다.\n쉽게 항복할 수는 없습니다.",
    (7, 334, 0): "……온정은 감사하오나,\n이번에는 거절하겠습니다.\n아직 그럴 마음은 들지 않습니다……",
    (7, 335, 0): "권유에는 감사드립니다.\n하지만 당장 결단할 수는 없습니다……",
    (7, 336, 0): "송구합니다.\n주가를 잃은 지 얼마 되지 않아,\n아직 마음을 추스르지 못했습니다.",
    (7, 570, 0): "이제 여기까지다……\n결별할 상대는",
    (7, 578, 0): "아무래도 함께할 수 있는 것은 여기까지인 듯하군.\n싸울 수 없는 상대는",
    (7, 579, 0): "이제 여기까지다……\n싸울 수 없는 상대는",
    (7, 587, 0): "교전 상대는",
    (7, 588, 0): "이번 교전 상대는",
    (7, 800, 0): "（내 영지를 지키지 못하다니……\n　당가의 힘도 알 만하군……）",
    (7, 803, 0): "은(는) 본거지에서 멀리 떨어져 있습니다.\n휘하 군단에 통치를 맡기는 것이 좋습니다.",
    (7, 805, 0): "새 본거지를 결정해 주십시오.\n",
    (7, 806, 0): "새 본거지를 결정해 주십시오.\n",
    (7, 807, 0): "본거 이전에 따라,\n지휘 범위 밖이 된",
    (7, 807, 1): "\n다이묘 군단 소속이 됩니다.",
    (7, 808, 0): "본거 이전에 따라,\n",
    (7, 816, 1): "\n원군 요청을 받았으므로,\n",
    (7, 828, 0): "이(가) 이토록 쇠퇴할 줄이야……\n이대로 섬겨도 미래는 없습니다.\n충성을 다하는 것도 여기까지입니다.",
    (7, 831, 0): "싸우게 될 상대가",
    (7, 835, 0): "방금 원군을 보낸 곳은",
    (7, 864, 0): "저자가 건방지게 구는군.\n직접 나설 사람은",
    (7, 876, 1): "까지 나서다니……!\n이제",
    (7, 876, 2): "의 무용을 시험할 때입니다.",
    (7, 878, 0): "놈이 나타났는가?\n정예 미카와 병사를 이끈다고 한다.\n모두 방심하지 마라.",
    (7, 882, 0): "마침내 야심을 드러냈는가.\n천하의 안녕을 위해,\n더는",
    (7, 882, 1): "두고 볼 수 없다!",
    (7, 885, 0): "가증스러운",
    (7, 889, 0): "가증스러운",
    (7, 890, 0): "이런 곳까지 오다니!\n목숨을 두려워하지 않는 사나운 무사들을 어찌 막는단 말인가……",
    (7, 951, 1): "!?\n……이렇게 된다면\n거리 둘 상대는",
    (7, 955, 0): "힘없는 의는 무와 다름없다.\n패배한 상대는",
    (7, 955, 1): ",\n거리를 둘 상대는",
    (7, 956, 0): "패배한 상대는",
    (7, 956, 1): ", 불운이든 실력이든,\n",
    (7, 957, 2): "까지 염두에 두어야겠군.",
    (7, 961, 1): "따위에게……\n",
    (7, 962, 1): "에게 패하다니……\n",
    (7, 963, 0): "에게 패하다니……유약하구나,",
    (7, 963, 1): "……\n그토록 유약하다니,\n",
    (7, 967, 1): "에게 패했습니까……\n",
    (7, 973, 1): "에게 이겼구나!\n내가 얕본 세력은",
    (7, 974, 1): "도 당대의 패자인가……\n",
    (7, 976, 0): "을 물리친 세력은",
    (7, 976, 1): "!\n하지만 의 없는 힘은 무와 같다.\n과연",
    (7, 977, 0): "승리한 상대는",
    (7, 978, 1): "을 얕볼 수는 없겠군!\n",
    (7, 984, 0): "쓰러뜨린 상대는",
    (7, 988, 1): "도 제법이군요!\n",
    (7, 996, 1): "이(가)\n공격한 곳은",
    (7, 1002, 1): "은(는) 약하다!\n",
    (7, 1006, 1): "!?\n……설마",
    (7, 1014, 0): "이긴 상대는",
    (7, 1019, 0): "승리한 상대는",
    (7, 1019, 1): "!\n살아남기 위해서는\n따를 상대가",
}


class BatchError(ValueError):
    """Raised when a pinned input or semantic contract changes."""


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
    return {"path": relative.as_posix(), "size": len(blob), "sha256": recovery.sha256(blob)}


def review_window() -> tuple[list[tuple[int, int, int]], dict[tuple[int, int, int], dict[str, Any]]]:
    if recovery.sha256(PRIOR_REVIEW.read_bytes()) != PRIOR_REVIEW_PIN:
        raise BatchError("prior invariant-recovery review pin changed")
    prior_review = read_json(PRIOR_REVIEW)
    excluded = sorted(
        (item for item in prior_review.get("entries", []) if isinstance(item, dict) and item.get("status") == "excluded"),
        key=lambda item: (item["block_id"], item["record_id"], item["literal_id"]),
    )
    if len(excluded) != 1_879:
        raise BatchError("prior exclusion pool changed")
    window_items = excluded[200:350]
    coordinates = [(item["block_id"], item["record_id"], item["literal_id"]) for item in window_items]
    if recovery.canonical_hash([list(value) for value in coordinates]) != WINDOW_PIN:
        raise BatchError("B03 150-coordinate review window changed")
    return coordinates, {coordinate: item for coordinate, item in zip(coordinates, window_items)}


def assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = recovery.script_counts(path.read_text(encoding="utf-8"))
        result[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise BatchError(f"commercial source script leaked into artifact: {path}")
    return result


def exclusion_reason(coordinate: tuple[int, int, int]) -> str:
    if coordinate[0] == 7 and 154 <= coordinate[1] <= 209:
        return "sc_dynamic_value_order_requires_joint_sibling_rewrite"
    if coordinate in {(7, 267, 0), (7, 268, 0), (7, 274, 0), (7, 329, 0), (7, 580, 0)}:
        return "cross_literal_korean_word_order_not_safe_in_isolation"
    return "partial_record_context_not_safe_for_isolated_coordinate"


def _overlay_coordinates(path: Path) -> set[tuple[int, int, int]]:
    overlay = read_json(path)
    if overlay.get("resource") != RESOURCE or not isinstance(overlay.get("entries"), list):
        raise BatchError(f"invalid existing msggame overlay: {path}")
    result: set[tuple[int, int, int]] = set()
    for entry in overlay["entries"]:
        coordinate = (entry.get("block_id"), entry.get("record_id"), entry.get("literal_id"))
        if not all(type(value) is int for value in coordinate):
            raise BatchError(f"invalid existing coordinate: {path}")
        result.add(coordinate)
    return result


def collect_existing(
    progress_path: Path, target_catalog_path: Path = recovery.DEFAULT_TARGET_CATALOG
) -> dict[str, Any]:
    """Pin the exact B02 predecessor prefix while tolerating later batches."""
    history = recovery.collect_overlay_history(
        progress_path,
        target_catalog_path=target_catalog_path,
        predecessor_boundary_relative=B02_RELATIVE,
        predecessor_paths_pin=PREDECESSOR_PATHS_PIN,
        predecessor_coordinate_count=PREDECESSOR_COORDINATE_COUNT,
        self_relative=SELF_RELATIVE,
        self_batch_id=BATCH_ID,
        self_coordinate_count=130,
        self_coordinates_pin=SELF_COORDINATES_PIN,
        self_overlay_sha256=SELF_OVERLAY_SHA256,
    )
    return {
        "predecessor_coordinates": history["predecessor_coordinates"],
        "all_coordinates": history["all_coordinates"],
        "predecessor_inputs": history["predecessor_inputs"],
        "predecessor_normalized_sha256": history["predecessor_normalized_sha256"],
        "self_registration_count": history["self_registration_count"],
        "successor_coordinates": history["successor_coordinates"],
        "successor_paths": history["successor_paths"],
    }


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
    if len(TRANSLATIONS) != 130:
        raise BatchError(f"translation count changed: {len(TRANSLATIONS)}")
    if not selected_set <= window_set:
        raise BatchError("translation escaped the B03 review window")
    if selected_set & existing["all_coordinates"]:
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
    if len(excluded_coordinates) != 20:
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
            "policy": "coordinate_sorted_prior_exclusions_201_through_350",
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
            "pinned_predecessor_coordinate_union": len(existing["predecessor_coordinates"]),
            "pinned_predecessor_inputs": existing["predecessor_inputs"],
            "normalized_input_sha256": existing["predecessor_normalized_sha256"],
            "predecessor_prefix_sha256": PREDECESSOR_PATHS_PIN,
            "self_path": SELF_RELATIVE,
            "self_registration_states_supported": [0, 1],
            "successor_overlays_tolerated": True,
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
        "review_window": {"count": 150, "translated": len(selected), "excluded": len(excluded_coordinates)},
        "coordinate_sets": {
            "selected_sha256": selected_hash,
            "excluded_sha256": excluded_hash,
            "selected_excluded_disjoint": True,
            "selected_existing_disjoint": True,
            "selected_predecessor_disjoint": True,
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
            "later_overlay_registration_does_not_change_predecessor_pin": True,
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
