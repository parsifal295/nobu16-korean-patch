#!/usr/bin/env python3
"""Build Base authoring segment 894 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment808 as EARLIER_RONIN_A
import build_base_batch001_segment809 as EARLIER_RONIN_B
import build_base_batch001_segment881 as AUXILIARY
import build_base_batch001_segment893 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S894.private.v1.jsonl"
)
SEGMENT = 894
RONIN_RECRUITMENT_BASE_START = 1398
RONIN_RECRUITMENT_EARLIER_SOURCE_IDS = tuple(range(345, 357))
RONIN_RECRUITMENT_ARITIES = tuple(
    (
        EARLIER_RONIN_A.EXPECTED_ARITIES[source_id]
        if source_id <= 348
        else EARLIER_RONIN_B.RECORD_ARITIES[source_id]
    )
    for source_id in RONIN_RECRUITMENT_EARLIER_SOURCE_IDS
)
RONIN_RECRUITMENT_SOURCE_JP: tuple[tuple[str, ...], ...] = (
    ("、参上したぜ\n", "の力になれるよう尽くそう\n", "の働き、期待していてくれ！"),
    ("は", "と申す\n", "に仕えるは武士の誉れ\nこの上なき喜びにござる"),
    ("、", "と申す\n", "の覇業を助くべく\n身を粉にして働きますぞ"),
    ("と申します\n縁あって", "にお仕えした以上\n必ずやお役に立ってみせましょう"),
    ("お声がけいただき恐悦至極\nこれより、この", "めを\n", "の刃としてお使いくだされい"),
    ("不肖、", "\n我が才を活かせる主を求めておりました\n", "にお仕えでき、光栄に存ずる"),
    ("と申します\nこの度、末席を汚すこととなりました\nいかようにもお使いくだされ",),
    ("は", "と申す\nこの命尽きるまで\n", "のために戦いまするぞ！"),
    ("と申します\n至らぬところも多いと思いますが\n精一杯頑張ります！",),
    ("名を", "と言う\nこれより世話になる\n戦ならば任せてもらいたい！"),
    ("、", "と申します\n少しでも", "のお力になれるよう\n尽くしてまいりますわ"),
    ("これより、この", "\n", "のお力になれるよう尽くします\n", "の働きにご期待くだされ"),
)


def earlier_ronin_translation(source_id: int, literal_id: int) -> str:
    if source_id <= 348:
        return EARLIER_RONIN_A.TRANSLATIONS[
            f"15:{source_id}:{literal_id}"
        ]
    if source_id == 356 and literal_id == 1:
        return "\n"
    return EARLIER_RONIN_B.RAW_TRANSLATIONS[
        f"15:{source_id}:{literal_id}"
    ]


RONIN_RECRUITMENT_CANONICAL: tuple[tuple[str, ...], ...] = tuple(
    tuple(
        earlier_ronin_translation(source_id, literal_id)
        for literal_id in range(arity)
    )
    for source_id, arity in zip(
        RONIN_RECRUITMENT_EARLIER_SOURCE_IDS,
        RONIN_RECRUITMENT_ARITIES,
        strict=True,
    )
)
RONIN_RECRUITMENT_BASE_GAPS: tuple[tuple[str, ...], ...] = tuple(
    (
        EARLIER_RONIN_A.EXPECTED_GAPS[source_id]
        if source_id <= 348
        else EARLIER_RONIN_B.EXPECTED_GAPS[source_id]
    )
    for source_id in RONIN_RECRUITMENT_EARLIER_SOURCE_IDS
)
RONIN_RECRUITMENT_PK_GAPS = RONIN_RECRUITMENT_BASE_GAPS


def ronin_index(record_id: int) -> int:
    index = record_id - RONIN_RECRUITMENT_BASE_START
    if not 0 <= index < len(RONIN_RECRUITMENT_CANONICAL):
        raise RuntimeError(f"record is outside the ronin canonical: {record_id}")
    return index


RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:1393:{literal_id}": translation
        for literal_id, translation in enumerate(
            PREVIOUS.DEVELOPMENT_CANONICAL
        )
    },
    "15:1394:0": "·",
    "15:1394:1": '의 군 특성 "',
    "15:1394:2": '"이(가) 성장',
    "15:1395:0": "이(가)",
    "15:1395:1": "에서 벌인",
    "15:1395:2": "에 성공",
    "15:1396:0": "우리",
    "15:1396:1": "은(는) 일손이 부족하",
    "15:1396:2": (
        "\n"
        "부디 낭인을 등용하여 장차\n"
        "우리 성의 군을 다스리게 하고 싶…"
    ),
    "15:1397:0": (
        "우리 성과 같은 전선에서야말로 제힘을 발휘할\n"
        "싸움에 능한 낭인을 알고 있"
    ),
    "15:1397:1": "\n말을 걸어 보아도",
    "15:1397:2": "인가",
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(1398, 1400)
        for literal_id, translation in enumerate(
            RONIN_RECRUITMENT_CANONICAL[ronin_index(record_id)]
        )
    },
}
RECORD_ARITIES = {
    1393: 5,
    1394: 3,
    1395: 3,
    1396: 3,
    1397: 3,
    1398: 3,
    1399: 3,
}
EXPECTED_BASE_JP = {
    1393: PREVIOUS.DEVELOPMENT_SOURCE_JP,
    1394: ("・", "の郡特性「", "」が成長"),
    1395: ("が", "での", "に成功"),
    1396: (
        "我が",
        "は人手が足",
        "\nぜひとも牢人を登用し、ゆくゆくは\n我が城の郡を治めさせたく…",
    ),
    1397: (
        "我が城のような前線でこそ役立つ\n戦上手な牢人を見知って",
        "\n声をかけても",
        "か",
    ),
    1398: RONIN_RECRUITMENT_SOURCE_JP[ronin_index(1398)],
    1399: RONIN_RECRUITMENT_SOURCE_JP[ronin_index(1399)],
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1393: PREVIOUS.DEVELOPMENT_BASE_GAPS,
    1394: ("", "029632", "02BE32", "050505"),
    1395: ("024633", "029632", "023C", "050505"),
    1396: ("", "02463F", "01432A040000", "050505"),
    1397: (
        "",
        "0143B2000000",
        "01430C040000014356020000",
        "050505",
    ),
    1398: RONIN_RECRUITMENT_BASE_GAPS[ronin_index(1398)],
    1399: RONIN_RECRUITMENT_BASE_GAPS[ronin_index(1399)],
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1393: PREVIOUS.DEVELOPMENT_PK_GAPS,
    1396: ("", "02463F", "014336040000", "050505"),
    1397: (
        "",
        "0143B2000000",
        "014318040000014362020000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1396:2"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1395): (
        ("于", "成功", "了。"),
        ("024633", "029632", "023C", "050505"),
    ),
    ("TC", 1395): (
        ("對", "成功。"),
        ("024633", "029632023C", "050505"),
    ),
    ("SC", 1396): (
        ("我", "人手不足，\n请务必登用浪人，\n让我能逐步将郡治理好……"),
        ("", "02463F", "050505"),
    ),
    ("SC", 1397): (
        ("我认识一个在我城这样的前线\n才有用武之地的浪人。\n去打个招呼如何？",),
        ("", "050505"),
    ),
    ("TC", 1397): (
        ("我認識一位\n擅長在前線之城作戰的浪人。\n是否允許召喚他？",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1395: (
        (" successfully completed the ", " in ", "."),
        ("024633", "023C", "029632", "050505"),
    ),
    1396: (
        (
            "My ",
            " lacks laborers. I would like to employ rªnin to gradually "
            "take over the rule of my castleÖs county.",
        ),
        ("", "02463F", "050505"),
    ),
    1397: (
        (
            "My castle will have a pivotal role on the front lines. I know "
            "a rªnin who is a capable fighter. Shall I have him come?",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = AUXILIARY.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
AUXILIARY_OVERRIDES.update(
    {
        ("base", "TC", 1396): (
            ("我等", "現在人手不足。\n請積極登庸浪人，\n加速發展我等城下的郡……"),
            ("", "02463F", "050505"),
        ),
        ("pk", "TC", 1396): (
            ("我等的", "目前人手不足。\n應該積極登庸浪人，\n以便讓其日後治理我等城下的郡……"),
            ("", "02463F", "050505"),
        ),
    }
)
BASIS = (
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "county_trait_growth_plot_success_ronin_staffing_frontline_recruitment_"
    "and_two_officer_introductions_with_uniform_plus_15_pk_mapping_base_tc_"
    "1396_context_exception_base_tc_authoritative_actual_pk_en_sc_tc_"
    "auxiliary_context_b107_development_and_b080_ronin_canonicals_reused_"
    "牢人_as_historically_contextualized_낭인_dynamic_county_trait_plot_"
    "castle_officer_house_and_speaker_tokens_conjugation_stems_current_"
    "layout_and_opcode_skeleton_preserved_runtime_fragment_pending"
)


def assert_ronin_canonical_sources(
    source_records: dict[tuple[int, int], Any],
) -> None:
    if not (
        len(RONIN_RECRUITMENT_SOURCE_JP)
        == len(RONIN_RECRUITMENT_CANONICAL)
        == len(RONIN_RECRUITMENT_BASE_GAPS)
        == len(RONIN_RECRUITMENT_PK_GAPS)
        == 12
    ):
        raise RuntimeError("segment 894 ronin canonical length drifted")
    for index, earlier_id in enumerate(
        RONIN_RECRUITMENT_EARLIER_SOURCE_IDS
    ):
        target_id = RONIN_RECRUITMENT_BASE_START + index
        expected_source = RONIN_RECRUITMENT_SOURCE_JP[index]
        if COMMON.CORE.source_literals(
            source_records, earlier_id
        ) != expected_source:
            raise RuntimeError(
                f"segment 894 earlier ronin source drifted: {earlier_id}"
            )
        if COMMON.CORE.source_literals(
            source_records, target_id
        ) != expected_source:
            raise RuntimeError(
                f"segment 894 B108 ronin source drifted: {target_id}"
            )
        if RONIN_RECRUITMENT_BASE_GAPS[index] != (
            EARLIER_RONIN_A.EXPECTED_GAPS[earlier_id]
            if earlier_id <= 348
            else EARLIER_RONIN_B.EXPECTED_GAPS[earlier_id]
        ):
            raise RuntimeError(
                f"segment 894 ronin gap canonical drifted: {target_id}"
            )
    if RONIN_RECRUITMENT_CANONICAL[-1][1] != "\n":
        raise RuntimeError("segment 894 ronin hidden LF canonical drifted")
    if (
        "황송하기 그지없" not in RONIN_RECRUITMENT_CANONICAL[4][0]
        or not RONIN_RECRUITMENT_CANONICAL[5][0].startswith("불초")
        or "말석에 들" not in RONIN_RECRUITMENT_CANONICAL[6][0]
    ):
        raise RuntimeError(
            "segment 894 恐悦至極/不肖/末席を汚す meanings drifted"
        )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    assert_ronin_canonical_sources(source_records)
    if tuple(
        raw_translations[f"15:1393:{literal_id}"]
        for literal_id in range(5)
    ) != PREVIOUS.DEVELOPMENT_CANONICAL:
        raise RuntimeError("segment 894 development canonical drifted")
    if (
        raw_translations["15:1394:0"] != "·"
        or raw_translations["15:1394:1"] != '의 군 특성 "'
        or raw_translations["15:1394:2"] != '"이(가) 성장'
    ):
        raise RuntimeError("segment 894 county-trait UI framing drifted")
    if (
        raw_translations["15:1395:0"] != "이(가)"
        or raw_translations["15:1395:1"] != "에서 벌인"
        or raw_translations["15:1395:2"] != "에 성공"
    ):
        raise RuntimeError("segment 894 plot-result token perspective drifted")
    if (
        raw_translations["15:1396:0"] != "우리"
        or not raw_translations["15:1396:1"].endswith("부족하")
        or "낭인을 등용" not in raw_translations["15:1396:2"]
        or "우리 성의 군을 다스리게" not in raw_translations["15:1396:2"]
    ):
        raise RuntimeError("segment 894 ronin staffing proposal drifted")
    if (
        "전선" not in raw_translations["15:1397:0"]
        or "싸움에 능한 낭인" not in raw_translations["15:1397:0"]
        or not raw_translations["15:1397:0"].endswith("알고 있")
        or raw_translations["15:1397:1"] != "\n말을 걸어 보아도"
    ):
        raise RuntimeError("segment 894 frontline ronin proposal drifted")
    for record_id in range(1398, 1400):
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        )
        if actual != RONIN_RECRUITMENT_CANONICAL[ronin_index(record_id)]:
            raise RuntimeError(
                f"segment 894 ronin introduction canonical drifted: {record_id}"
            )
    if (
        not translations["15:1396:2"].endswith("……")
        or translations["15:1396:2"].count("…") != 2
    ):
        raise RuntimeError("segment 894 project ellipsis pairing drifted")
    joined = "\n".join(translations.values())
    for required in ("군 특성", "일손", "낭인", "전선", "무사의 영예"):
        if required not in joined:
            raise RuntimeError(
                f"segment 894 required terminology drifted: {required}"
            )
    if any(term in joined for term in ("牢人", "浪人", "낭자")):
        raise RuntimeError("segment 894 牢人 terminology drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != len(translations):
        raise RuntimeError("segment 894 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S894",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "base_tc_1396_context_authoritative": True,
                "ronin_recruitment_canonical_size": len(
                    RONIN_RECRUITMENT_CANONICAL
                ),
                "ronin_recruitment_canonical_defined": True,
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
