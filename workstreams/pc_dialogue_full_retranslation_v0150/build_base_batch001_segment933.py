#!/usr/bin/env python3
"""Build Base authoring segment 933 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment908 as COMMON
import build_base_batch001_segment932 as CANONICAL_S932


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S933.private.v1.jsonl"
)
SEGMENT = 933
CANONICAL_TRANSLATIONS_BY_RECORD = {
    **{
        record_id: CANONICAL_S932.NEGOTIATION_BREAKDOWN_TRANSLATION
        for record_id in range(1761, 1764)
    },
    1764: (
        "우리 가문이 지금 무엇을 해야 할지…\n고민하고 계시다면,",
        "의 생각을\n이 자리에서 말씀드리고자 하옵니다",
    ),
    1765: (
        "우리 가문이 처한 상황에 대해\n설명이 필요",
        "인가?",
    ),
    1766: (
        "의 설명은 여기까지",
        "만\n상황은 시시각각 변하는 법\n임기응변으로 대처하여",
    ),
    1767: (
        "그럼, 우리 가문을 둘러싼 상황을\n",
        "부터 설명",
    ),
    1768: (
        '우리 가문의 상황이 궁금할 때는\n오른쪽 위의 "헌언"에서 물어봐',
    ),
    1769: (
        "알겠사",
        (
            '. 설명이 필요하실 때는 언제든지\n'
            '"평정"의 "공략 방침"을 열어\n'
            '"진언"에서'
        ),
    ),
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    1761: 2,
    1762: 2,
    1763: 2,
    1764: 2,
    1765: 2,
    1766: 2,
    1767: 2,
    1768: 1,
    1769: 2,
}
NEGOTIATION_BREAKDOWN_JP = CANONICAL_S932.NEGOTIATION_BREAKDOWN_JP
EXPECTED_BASE_JP = {
    1761: NEGOTIATION_BREAKDOWN_JP,
    1762: NEGOTIATION_BREAKDOWN_JP,
    1763: NEGOTIATION_BREAKDOWN_JP,
    1764: (
        "当家は今、なにを為すべきか…\nお悩みならば、",
        "の考えを\nここで述べさせていただきたく",
    ),
    1765: (
        "当家が置かれている状況について\n説明が必要",
        "か？",
    ),
    1766: (
        "からは以上",
        "が\n状況は刻々と変わるもの\n臨機応変に対処して",
    ),
    1767: (
        "では、当家を取り巻く状況について\n",
        "から説明",
    ),
    1768: (
        "当家の状況を知りたいときは\n右上の「献言」から聞いて",
    ),
    1769: (
        "承知し",
        "。聞きたくなったらいつでも\n「評定」の「攻略方針」を開き\n「進言」から",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1761: ("", "023c", "050505"),
    1762: ("", "023c", "050505"),
    1763: ("", "023c", "050505"),
    1764: ("", "014301000000", "050505"),
    1765: ("", "014356020000", "050505"),
    1766: (
        "014301000000",
        "01432c020000",
        "014342010000050505",
    ),
    1767: ("", "014301000000", "0143a2010000050505"),
    1768: ("", "014342010000050505"),
    1769: ("", "014314020000", "014330010000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1765: ("", "014362020000", "050505"),
    1766: (
        "014301000000",
        "014338020000",
        "014342010000050505",
    ),
    1767: ("", "014301000000", "0143a8010000050505"),
    1769: ("", "01431a020000", "014330010000050505"),
}
PK_RECORD_MAP = {
    1761: 1791,
    1762: 1792,
    1763: 1793,
    1764: 1794,
    1765: 1795,
    1766: 1796,
    1767: 1797,
    1768: 1798,
    1769: 1799,
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1764:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1764): (
        (
            "本家现在应该做什么……\n如果为此而烦恼的话，\n就由",
            "来在此说明吧。",
        ),
        ("", "014301000000", "050505"),
    ),
    ("TC", 1764): (
        ("不如就由", "來說明\n本家目前的狀況吧。"),
        ("", "014301000000", "050505"),
    ),
    ("SC", 1765): (
        ("您需要我来介绍一下\n本家的处境吗？",),
        ("", "050505"),
    ),
    ("TC", 1765): (
        ("關於本家所處狀況\n是否需要說明？",),
        ("", "050505"),
    ),
    ("SC", 1766): (
        ("的说明就到此为止了。\n情况瞬息万变……\n还请随机应变。",),
        ("014301000000", "050505"),
    ),
    ("TC", 1766): (
        ("的說明就到此為止。\n情況瞬息萬變，還請隨機應變了。 ",),
        ("014301000000", "050505"),
    ),
    ("SC", 1767): (("您要听哪项说明呢？",), ("", "050505")),
    ("TC", 1767): (("您要聽哪項說明呢？",), ("", "050505")),
    ("SC", 1768): (
        ("想了解本家情况的时候，\n请从右上的「献策」听取。",),
        ("", "050505"),
    ),
    ("TC", 1768): (
        ("想知道本家狀況時，\n可由右上方的「獻策」聽取。",),
        ("", "050505"),
    ),
    ("SC", 1769): (
        (
            "遵命。你若是想听了，\n就随时打开“评定”的“攻略方针。\n"
            "在“进言”里听吧。",
        ),
        ("", "050505"),
    ),
    ("TC", 1769): (
        (
            "了解。若有疑問，\n隨時都可打開「評定」的「攻略方針」，\n"
            "從「進言」詢問。",
        ),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1764: (
        (
            "What should our clan do now? If youÖre unsure, "
            "I can share my thoughts with you.",
        ),
        ("", "050505"),
    ),
    1765: (
        ("Would you like an explanation of our clanÖs current situation?",),
        ("", "050505"),
    ),
    1766: (
        (
            "ThatÖs all I have for now. However, the situation changes "
            "by the hour, so we must be ready to adapt.",
        ),
        ("", "050505"),
    ),
    1767: (
        ("Now, allow me to explain our clanÖs condition.",),
        ("", "050505"),
    ),
    1768: (
        (
            "Whenever you wish to know more about the clanÖs condition, "
            "please check proposal in the upper-right corner.",
        ),
        ("", "050505"),
    ),
    1769: (
        (
            "Understood. If you ever wish for counsel, open the invasion "
            "plan under council.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B112_B_pristine_base_pc_jp_authoritative_"
    "negotiation_breakdown_canonical_continuation_advisor_introduction_"
    "situation_explanation_and_counsel_tutorial_with_explicit_plus30_pk_"
    "mapping_base_pk_sc_tc_and_pk_en_auxiliary_context_s932_exact_tuple_"
    "reuse_glossary_our_clan_heoneon_jineon_distinction_ascii_ui_quotes_"
    "dynamic_advisor_name_014301_and_exhaustive_base_pk_speaker_opcode_"
    "suffix_divergences_1765_1766_1767_1769_current_base_skeleton_"
    "authoritative_contextual_ellipsis_pair_and_line_counts_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1761, 1764):
        if (
            CANONICAL_TRANSLATIONS_BY_RECORD[record_id]
            is not CANONICAL_S932.NEGOTIATION_BREAKDOWN_TRANSLATION
            or EXPECTED_BASE_JP[record_id] is not NEGOTIATION_BREAKDOWN_JP
        ):
            raise RuntimeError(
                f"segment 933 S932 canonical reuse split: {record_id}"
            )
    for record_id, expected_source in EXPECTED_BASE_JP.items():
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != expected_source:
            raise RuntimeError(
                f"segment 933 pristine source drifted: {record_id}"
            )
    if any(
        mapped_id != record_id + 30
        for record_id, mapped_id in PK_RECORD_MAP.items()
    ):
        raise RuntimeError("segment 933 Base-to-PK mapping drifted")
    divergent = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergent != {1765, 1766, 1767, 1769}:
        raise RuntimeError("segment 933 Base/PK opcode divergence set drifted")
    if raw_translations["15:1766:0"] != "의 설명은 여기까지":
        raise RuntimeError("segment 933 1766 name-to-explanation frame drifted")
    if not raw_translations["15:1766:1"].startswith("만\n"):
        raise RuntimeError("segment 933 1766 contrastive suffix drifted")
    if (
        raw_translations["15:1765:0"].splitlines()[-1] != "설명이 필요"
        or raw_translations["15:1765:1"] != "인가?"
    ):
        raise RuntimeError("segment 933 1765 proven copula split drifted")
    if (
        raw_translations["15:1767:1"] != "부터 설명"
        or not raw_translations["15:1768:0"].endswith('물어봐')
        or raw_translations["15:1769:0"] != "알겠사"
        or not raw_translations["15:1769:1"].endswith('"진언"에서')
    ):
        raise RuntimeError("segment 933 advisor opcode stem drifted")
    if (
        raw_translations["15:1764:0"].count("…") != 1
        or translations["15:1764:0"].count("…") != 2
    ):
        raise RuntimeError("segment 933 contextual ellipsis pair drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "헌언",
        "진언",
        "평정",
        "공략 방침",
        "시시각각",
        "임기응변",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 933 required meaning drifted: {required}")
    for forbidden in (
        "당가",
        "「",
        "」",
        "。",
        "이(가)\n상황",
        "로부터는 이상",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 933 retained forbidden phrasing: {forbidden}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 17 or len(translations) != 17:
        raise RuntimeError("segment 933 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 933 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 933 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S933",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "s932_canonical_continuation_records": [1761, 1762, 1763],
                "explicit_plus30_pk_mapping": True,
                "base_pk_opcode_divergence_records": [1765, 1766, 1767, 1769],
                "dynamic_advisor_name_records": [1764, 1766, 1767],
                "glossary_terms": {
                    "当家": "우리 가문",
                    "献言": "헌언",
                    "進言": "진언",
                },
                "contextual_ellipsis_normalized_to_project_pair": 1,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
