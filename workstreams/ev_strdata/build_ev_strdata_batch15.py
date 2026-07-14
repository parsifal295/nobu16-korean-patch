#!/usr/bin/env python3
"""Build source-free ev_strdata character/speaker-label batch v0.15 artifacts."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402


BATCH_ID = "ev-strdata-character-speaker-labels-2780-2971-v0.15"
OVERLAY_NAME = "ev_strdata_ko_event_labels_2780_2971.v0.15.json"
EVIDENCE_NAME = "alignment_evidence.v0.15.json"
REVIEW_NAME = "review_index.v0.15.json"
VALIDATION_NAME = "validation.v0.15.json"

SCOPE_START = 2780
SCOPE_END = 2971
INSPECTED_START = 2780
INSPECTED_END = 3006
NEXT_DISPLAY_ID = 3007
TRANSLATED_COUNT = 184
INSPECTED_COUNT = 227
DEFERRED_COUNT = 43

TRANSLATED_IDS_SHA256 = "12A475F1AB7DE76E060236B78BB84D70BADD8AE2C22D325047D2B704BC3E1A47"
TRANSLATION_MAP_SHA256 = "5811499B8E15FC535693B3E741E3001B3F44426B1A923D5A39732AC68B3B727E"
SOURCE_SC_HASHES_SHA256 = "B105E2544E7E0980E766DA1D8C62450F3AE33A89EE83C94AAC6F4FB5DCAF503D"
ALL_REFERENCE_HASHES_SHA256 = "C1CC901EF1A0DC3ED5E52D71D7161A531F13AB5689154E54E88D889247B4E28F"
INSPECTED_IDS_SHA256 = "219CDF182F9789CF7BB5494962D533AFA3163B29E2CB76D1AC72D17C38A357B3"
DEFERRED_IDS_SHA256 = "2B95F92D5D9B8AB6E96DEB1A412CB34957B24978FFF2C089254A42C3CE265245"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "84AA6AA8E375B4F881DB1A9225993E14543E54EC8A1D9627E18B5955DC0A8DD2",
    "JP": "3BA1AF9AE985DB60E6B432796C320EB9C14A1FF32E5A1B63C76AA5AFA2BA75D2",
    "TC": "6BBF19C7CCADBA8BD6E642FDB2C9B2FC761DE28EE88F6538D5BCD0ED46D2655C",
}

TRANSLATIONS: dict[int, str] = {
    2780: "쓰다 소규",
    2781: "가이센 조키",
    2782: "다쿠겐 소온",
    2783: "슌소보",
    2784: "프로이스",
    2785: "알메이다",
    2786: "노인",
    2787: "농민",
    2788: "철포 아시가루",
    2789: "승려",
    2790: "공가",
    2791: "승병",
    2792: "고쇼",
    2793: "조장",
    2794: "가신",
    2795: "범용 닌자",
    2796: "아시가루",
    2797: "가로",
    2798: "전령",
    2799: "상인",
    2800: "호족",
    2801: "아이",
    2802: "사자",
    2803: "병사",
    2804: "사비에르",
    2805: "마쓰다이라 다케치요",
    2806: "닌자",
    2807: "흰 고양이",
    2808: "소년",
    2809: "소녀",
    2810: "오이와 유무",
    2811: "시골 처녀",
    2812: "마을 처녀",
    2813: "장로",
    2814: "상인사",
    2815: "흰 원숭이",
    2816: "사자",
    2817: "중신",
    2818: "장자",
    2819: "가상 성대",
    2820: "아케치 미쓰쓰나",
    2821: "아사쿠라 사다카게",
    2822: "아사리 도모요리",
    2823: "아시카가 다카모토",
    2824: "아시나 모리타카",
    2825: "아소 고레노리",
    2826: "아마고 마사히사",
    2827: "아리마 히사아키",
    2828: "이시이 노부타다",
    2829: "이시카와 야스마사",
    2830: "이시카와 기요카네",
    2831: "이마가와 우지치카",
    2832: "우에무라 요리카도",
    2833: "우스키 나가카게",
    2834: "우메즈 도킨",
    2835: "우라가미 무라무네",
    2836: "에마 도키쓰네",
    2837: "오이 다다타카",
    2838: "오쿠보 다다시게",
    2839: "오타 스케요리",
    2840: "오토모 요시나가",
    2841: "오노 사도노카미",
    2842: "오카베 히사쓰나",
    2843: "오쿠다이라 다다마사",
    2844: "오바 요시무네",
    2845: "오부 모씨",
    2846: "가키자키 미쓰히로",
    2847: "가키자키 다카히로",
    2848: "가시야마 아키무네",
    2849: "가타기리 나오사다",
    2850: "가미이즈미 히데타네",
    2851: "간쇼지 짓에",
    2852: "깃카와 구니쓰네",
    2853: "기노시타 이에사다",
    2854: "기노시타 야에몬",
    2855: "교고쿠 다카키요",
    2856: "하라다 다네요시",
    2857: "구마가이 다카나오",
    2858: "구루시마 나가치카",
    2859: "구와야마 가즈시게",
    2860: "고리키 마사나가",
    2861: "고다마 나리자네",
    2862: "고니시 류사",
    2863: "고바타 모씨",
    2864: "사이온지 기미이에",
    2865: "사이온지 긴노부",
    2866: "사카이 마사치카",
    2867: "사쿠마 모리쓰구",
    2868: "사쿠라바 미쓰야스",
    2869: "사타케 요시키요",
    2870: "사나다 요리마사",
    2871: "신조 나오마사",
    2872: "스기 시게스케",
    2873: "스와 요리타카",
    2874: "다테 히사무네",
    2875: "조소카베 가네쓰구",
    2876: "쓰치바시 시게타카",
    2877: "쓰마키 사다노리",
    2878: "덴도 요리미치",
    2879: "도젠지 모씨",
    2880: "도키 마사후사",
    2881: "도다 나이키",
    2882: "나가토로 요시야스",
    2883: "나가노 미치후지",
    2884: "나리타 지카야스",
    2885: "난부 마사야스",
    2886: "니혼마쓰 마사쿠니",
    2887: "하가 우지타카",
    2888: "하타케야마 히사노부",
    2889: "하류 모리아키",
    2890: "히사타케 쇼겐",
    2891: "히네노 다카요시",
    2892: "후쿠시마 마사노부",
    2893: "후쿠바라 모토토시",
    2894: "후루타 시게노리",
    2895: "호소카와 모토아리",
    2896: "호소카와 다다카타",
    2897: "호리 히데시게",
    2898: "혼간지 렌뇨",
    2899: "마에다 도시하루",
    2900: "마카베 히사모토",
    2901: "마키 모씨",
    2902: "마사키 미치쓰나",
    2903: "마시코 가쓰무네",
    2904: "마쓰다이라 노부타다",
    2905: "마쓰나가 모씨",
    2906: "마쓰라 히사노부",
    2907: "마리야쓰 조칸",
    2908: "마리야쓰 노부카쓰",
    2909: "미우라 사다쿠니",
    2910: "미즈노 다다치카",
    2911: "미쓰부치 후지히데",
    2912: "미무라 무네치카",
    2913: "미요시 모토나가",
    2914: "미요시 유키나가",
    2915: "야마우치 모리토요",
    2916: "야마나 무네토요",
    2917: "요시다 노리히로",
    2918: "아소 이에노부",
    2919: "산조 긴요리",
    2920: "누마타 미쓰카네",
    2921: "무로가 미쓰마사",
    2922: "무로가 마사시게",
    2923: "목소리",
    2924: "수수께끼의 무희",
    2925: "이코마 루이",
    2926: "승려",
    2927: "도요 상인",
    2928: "남만인",
    2929: "전령",
    2930: "시마즈 가문 병사",
    2931: "마쓰나가 가문 가신",
    2932: "오다 가문 사자",
    2933: "가모 가문 신참",
    2934: "나가노 가문 병사",
    2935: "다카하시 가문 잡병",
    2936: "미요시군 병사",
    2937: "우에스기 가문 병사",
    2938: "호조군 병사",
    2939: "오토모 가문 병사",
    2940: "오토모군 병사",
    2941: "시마즈군 병사",
    2942: "마쓰나가군 가신",
    2943: "다케다군 병사",
    2944: "모리군 병사",
    2945: "다치바나 가문 가인",
    2946: "아라키군 병사",
    2947: "가모 가문 고참",
    2948: "보초",
    2949: "다카하시대 아시가루",
    2950: "사나다군 가신",
    2951: "나가노군 가신",
    2952: "이코마 이에무네",
    2956: "덴시쓰 고이쿠",
    2957: "나가오 도라치요",
    2958: "셋쓰 하루카도",
    2961: "나가노 가문 가신",
    2962: "다케다 시로",
    2963: "안도 모리나리",
    2966: "사나다 가문 가신",
    2968: "오다군 무장",
    2969: "다케다 가쓰요리",
    2970: "주인",
    2971: "다카하시대 잡병",
}

INTERNAL_ACTOR_REFERENCE_IDS = frozenset(
    {2953, 2954, 2955, 2959, 2960, 2964, 2965, 2967}
)
ACTOR_REFERENCE_IDS = frozenset(INTERNAL_ACTOR_REFERENCE_IDS | set(range(2972, 2998)))
DUMMY_PLACEHOLDER_IDS = frozenset({2998, 2999})
INTERNAL_ROLE_KEY_IDS = frozenset(range(3000, 3007))
DEFERRED_GROUP_IDS = {
    "actor_reference": ACTOR_REFERENCE_IDS,
    "dummy_placeholder": DUMMY_PLACEHOLDER_IDS,
    "internal_role_key": INTERNAL_ROLE_KEY_IDS,
}
DEFERRED_GROUP_PINS = {
    "actor_reference": {
        "count": 34,
        "ids_sha256": "A04A1FD8D53E811766759BA29C048A26CE6ADA5124CFBEBFE1BD70FD9C0518C6",
        "ordered_reference_hashes_sha256": "D03CF5B017076649413812E0444B417C17895641796FF61508CAAC90BFFCCA04",
    },
    "dummy_placeholder": {
        "count": 2,
        "ids_sha256": "EC1FACDE24FAA5091E53277DE5408358F5A4DA7E22E9C999EFF2D0883DAE94C4",
        "ordered_reference_hashes_sha256": "9C482BF2A9F75217B040D786A71153C0EC884A9DCBF7031F0A8CEB2FEB03A853",
    },
    "internal_role_key": {
        "count": 7,
        "ids_sha256": "DCFA8857788FE1D57FC736A63BB35842829CDF3B4E556BBCF07801E9D789F39E",
        "ordered_reference_hashes_sha256": "7BD839CBA467BF6DD6CEA0E6F6DE5AEDE5CE967A0B6449D12299620B9D510327",
    },
}
NAMED_CHARACTER_IDS = frozenset(
    {
        *range(2780, 2786),
        2804,
        2805,
        2810,
        *range(2820, 2923),
        2925,
        2927,
        2952,
        2956,
        2957,
        2958,
        2962,
        2963,
        2969,
    }
)
UNCERTAIN_READING_IDS = frozenset({2783, 2850, 2851, 2861, 2863, 2887, 2888, 2916})
CLASS_COUNTS = {
    "generic_speaker_label": 63,
    "named_character_label": 121,
}
REPEATED_SOURCE_ID_GROUPS = ((2789, 2926), (2798, 2929), (2802, 2816))


def classify(entry_id: int) -> str:
    return (
        "named_character_label"
        if entry_id in NAMED_CHARACTER_IDS
        else "generic_speaker_label"
    )


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def deferred_metadata() -> list[dict[str, Any]]:
    reasons = {
        "actor_reference": "runtime_actor_reference_not_display_text",
        "dummy_placeholder": "dummy_placeholder_not_display_text",
        "internal_role_key": "internal_role_key_not_display_text",
    }
    return [
        {
            "classification": classification,
            "status": "deferred",
            "reason": reasons[classification],
            "ids": sorted(DEFERRED_GROUP_IDS[classification]),
            **DEFERRED_GROUP_PINS[classification],
            "excluded_from_overlay_and_translation_progress": True,
        }
        for classification in (
            "actor_reference",
            "dummy_placeholder",
            "internal_role_key",
        )
    ]


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(INSPECTED_START, INSPECTED_END + 1))
    deferred_ids = sorted(
        entry_id
        for group in DEFERRED_GROUP_IDS.values()
        for entry_id in group
    )
    if len(ids) != TRANSLATED_COUNT or ids[0] != SCOPE_START or ids[-1] != SCOPE_END:
        raise shared.EvStrDataError("v0.15 translated id scope changed")
    if set(ids) & set(deferred_ids):
        raise shared.EvStrDataError("v0.15 translated and deferred ids overlap")
    if sorted(ids + deferred_ids) != inspected_ids:
        raise shared.EvStrDataError("v0.15 inspected partition changed")
    if len(inspected_ids) != INSPECTED_COUNT or len(deferred_ids) != DEFERRED_COUNT:
        raise shared.EvStrDataError("v0.15 inspected/deferred counts changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.15 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.15 inspected id digest changed")
    if shared.hash_json(deferred_ids) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.15 deferred id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.15 Korean translation map changed")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.15 functional classification counts changed")

    source_sc_hashes: list[str] = []
    all_reference_hashes: list[str] = []
    ids_by_source_hash: dict[str, list[int]] = defaultdict(list)
    replacement_by_source_hash: dict[str, str] = {}
    for entry_id in ids:
        references = [
            loaded[language]["table"].texts[entry_id]
            for language in shared.LANGUAGES
        ]
        if any(not text.strip() for text in references):
            raise shared.EvStrDataError(f"id {entry_id}: empty aligned display label")
        source_sc = references[0]
        source_hash = common.text_hash(source_sc)
        source_sc_hashes.append(source_hash)
        all_reference_hashes.extend(common.text_hash(text) for text in references)
        ids_by_source_hash[source_hash].append(entry_id)
        failures = shared.replacement_failures(source_sc, TRANSLATIONS[entry_id])
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
        prior = replacement_by_source_hash.setdefault(source_hash, TRANSLATIONS[entry_id])
        if prior != TRANSLATIONS[entry_id]:
            raise shared.EvStrDataError(
                f"id {entry_id}: repeated SC source has inconsistent Korean translations"
            )
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS or len(ids_by_source_hash) != 181:
        raise shared.EvStrDataError("v0.15 repeated-source groups changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.15 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.15 ordered SC/JP/TC source hashes changed")

    for classification, group in DEFERRED_GROUP_IDS.items():
        ordered_ids = sorted(group)
        pin = DEFERRED_GROUP_PINS[classification]
        reference_hashes = [
            common.text_hash(loaded[language]["table"].texts[entry_id])
            for entry_id in ordered_ids
            for language in shared.LANGUAGES
        ]
        if len(ordered_ids) != pin["count"]:
            raise shared.EvStrDataError(f"v0.15 {classification} count changed")
        if shared.hash_json(ordered_ids) != pin["ids_sha256"]:
            raise shared.EvStrDataError(f"v0.15 {classification} id digest changed")
        if shared.hash_json(reference_hashes) != pin["ordered_reference_hashes_sha256"]:
            raise shared.EvStrDataError(f"v0.15 {classification} source hashes changed")

    actor_pattern = re.compile(r"\[b(?:m)?\d+\]")
    role_pattern = re.compile(r"\d[A-Za-z_]+")
    for entry_id in ACTOR_REFERENCE_IDS:
        for language in shared.LANGUAGES:
            if actor_pattern.fullmatch(loaded[language]["table"].texts[entry_id]) is None:
                raise shared.EvStrDataError(f"id {entry_id}: actor-reference structure changed")
    for entry_id in INTERNAL_ROLE_KEY_IDS:
        for language in shared.LANGUAGES:
            if role_pattern.fullmatch(loaded[language]["table"].texts[entry_id]) is None:
                raise shared.EvStrDataError(f"id {entry_id}: role-key structure changed")

    for language in shared.LANGUAGES:
        if common.text_hash(loaded[language]["table"].texts[NEXT_DISPLAY_ID]) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.15 next display anchor changed for {language}")
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": TRANSLATIONS[entry_id],
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "classification": classify(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": shared.text_structure(
                            loaded[language]["table"].texts[entry_id]
                        ),
                    }
                    for language in shared.LANGUAGES
                },
                "translation_origin": "manual_sc_jp_tc_aligned_review",
            }
        )

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": shared.RESOURCE,
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": shared.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": shared.sha256(sc_raw),
            "string_count": shared.STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **shared.SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": shared.STRING_COUNT,
        }
        for language in shared.LANGUAGES
    }
    boundary_ids = (
        SCOPE_START - 1,
        SCOPE_START,
        2819,
        2820,
        2922,
        2923,
        2952,
        2953,
        2967,
        2968,
        SCOPE_END,
        2972,
        2997,
        2998,
        3000,
        INSPECTED_END,
        NEXT_DISPLAY_ID,
    )
    deferred = deferred_metadata()
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v15",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "inspected_start_id": INSPECTED_START,
            "inspected_end_id": INSPECTED_END,
            "inspected_entry_count": INSPECTED_COUNT,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "named_characters_and_generic_event_speakers",
            "functional_class_counts": CLASS_COUNTS,
        },
        "translation_mapping": {
            "sha256": TRANSLATION_MAP_SHA256,
            "entry_count": TRANSLATED_COUNT,
            "embedded_in_generator": True,
            "commercial_source_text_included": False,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "sc_jp_tc_semantic_review",
            "exact_sc_hash_for_every_overlay_entry",
            "ordered_sc_jp_tc_hash_set_pin",
            "repeated_source_requires_identical_korean_translation",
            "internal_actor_placeholder_and_role_key_classification",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata resource; TC is the third "
            "reference alongside SC and JP. Official strings are represented only by hashes."
        ),
        "source_files": source_files,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(
                        loaded[language]["table"].texts[entry_id]
                    )
                    for language in shared.LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": TRANSLATED_COUNT,
        "entries": evidence_entries,
        "deferred_internal_groups": deferred,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v15",
        "batch_id": BATCH_ID,
        "quality_state": "character_and_speaker_label_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "uncertain_reading_count": len(UNCERTAIN_READING_IDS),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": "manual_sc_jp_tc_aligned_review",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": (
                    ["rare_person_reading"]
                    if entry_id in UNCERTAIN_READING_IDS
                    else []
                ),
            }
            for entry_id in ids
        ],
        "deferred_internal_groups": deferred,
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shared.encode_json(value))

    source_free_scan = {
        path.relative_to(out_root).as_posix(): shared.source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(
        counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for counts in source_free_scan.values()
    ):
        raise shared.EvStrDataError(
            "v0.15 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.15 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v15",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "translated_ids_sha256": TRANSLATED_IDS_SHA256,
            "inspected_start_id": INSPECTED_START,
            "inspected_end_id": INSPECTED_END,
            "inspected_entry_count": INSPECTED_COUNT,
            "inspected_ids_sha256": INSPECTED_IDS_SHA256,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "deferred_ids_sha256": DEFERRED_IDS_SHA256,
            "next_display_id": NEXT_DISPLAY_ID,
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
            "functional_class_counts": CLASS_COUNTS,
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "translated_reference_hash_count": TRANSLATED_COUNT * len(shared.LANGUAGES),
            "translated_ids_nonempty_in_all_references": TRANSLATED_COUNT,
            "ordered_sc_source_hashes_sha256": SOURCE_SC_HASHES_SHA256,
            "ordered_all_reference_hashes_sha256": ALL_REFERENCE_HASHES_SHA256,
            "source_files": source_files,
        },
        "translation": {
            "translation_map_sha256": TRANSLATION_MAP_SHA256,
            "translation_map_entry_count": TRANSLATED_COUNT,
            "exact_sc_hashes_emitted": TRANSLATED_COUNT,
            "uncertain_reading_review_flag_count": len(UNCERTAIN_READING_IDS),
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": 181,
            "translated_repeated_source_group_count": len(REPEATED_SOURCE_ID_GROUPS),
            "repeated_source_id_groups": [list(group) for group in REPEATED_SOURCE_ID_GROUPS],
            "failures": 0,
        },
        "deferred_internal_groups": deferred,
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(shared.LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {
            **binary,
            "installed_target_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": shared.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "existing_v01_through_v014_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.15 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "inspected_count": INSPECTED_COUNT,
        "deferred_count": DEFERRED_COUNT,
        "next_display_id": NEXT_DISPLAY_ID,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [
        game_root / "MSG" / language / "ev_strdata.bin"
        for language in shared.LANGUAGES
    ]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr15-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr15-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.15 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.15 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.15 build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"translated={result['entry_count']}")
    print(f"inspected={result['inspected_count']}")
    print(f"deferred_internal={result['deferred_count']}")
    print(f"next_display_id={result['next_display_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
