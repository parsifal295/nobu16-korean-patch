#!/usr/bin/env python3
"""Build Base authoring segment 913 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment912 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S913.private.v1.jsonl"
)
SEGMENT = 913
make_auxiliary_overrides = PREVIOUS.make_auxiliary_overrides
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1543:0": "우리의 본거지인",
    "15:1543:1": "은(는)\n",
    "15:1543:2": "에 있으며, 이 지방에는\n",
    "15:1543:3": "개의 성이 있",
    "15:1544:0": "대망을 앞두니 피가 끓",
    "15:1544:1": "다…\n우선 통치 상황을",
    "15:1544:2": "확인",
    "15:1545:0": (
        "천하 평정을 이루려면\n"
        "전국 과반수의 성을 다스리고\n"
        "기나이를 제압해야 합니다."
    ),
    "15:1546:0": (
        "우리 가문의 무위라면\n"
        "모든 나라를 복속시킬 수 있을 터\n"
        "남은 세력을"
    ),
    "15:1546:1": "확인",
    "15:1547:0": (
        "다른 세력을 종속시킬 것인가\n"
        "아니면 공격해 멸할 것인가\n"
        "주군의"
    ),
    "15:1547:1": "하명에 달렸사옵니다…",
    "15:1548:0": "옛 본거지인",
    "15:1548:1": "은(는)\n",
    "15:1548:2": "에 있으며, 이 지방에는\n",
    "15:1548:3": "개의 성이 있",
    "15:1549:0": "우리 가문에\n불만을 품은 자가 있는 듯",
    "15:1549:1": "\n은상의",
    "15:1549:2": "검토를",
    "15:1550:0": (
        "충성이 흔들려 출분을 꾀하는 자가 있다는\n"
        "가신단에서 도는 소문을 들었"
    ),
    "15:1550:1": "\n무언가를 내리시는 것이…",
    "15:1551:0": (
        "충의가 부족한 가신이 있는 모양…\n"
        "무언가를 내려\n"
        "우리 가문에 붙들어 두는 것은 어떻겠습니까"
    ),
    "15:1552:0": "의 군에서\n간자가 있다는 보고를 받",
    "15:1552:1": "\n병사를 보내면 방해할 수 있",
    "15:1552:2": "이…",
}
RECORD_ARITIES = {
    1543: 4,
    1544: 3,
    1545: 1,
    1546: 2,
    1547: 2,
    1548: 4,
    1549: 3,
    1550: 2,
    1551: 1,
    1552: 3,
}
EXPECTED_BASE_JP = {
    1543: (
        "我らが本拠の",
        "は\n",
        "にあり、この地方には\n",
        "の城があ",
    ),
    1544: (
        "大望を前に血が滾",
        "ぞ…\nまずは統治状況を",
        "確認",
    ),
    1545: (
        "天下平定を成し遂げるには\n"
        "全国の過半数の城を治め\n"
        "畿内の制圧を行う必要があ",
    ),
    1546: (
        "当家の武威をもってすれば\n"
        "全ての国を従えること能うかと\n"
        "残りの勢力を",
        "確認",
    ),
    1547: (
        "他勢力を従属させるか\n"
        "もしくは攻め滅ぼすか\n"
        "殿の",
        "下知次第にて…",
    ),
    1548: (
        "かつての本拠、",
        "は\n",
        "にあり、この地方には\n",
        "の城があ",
    ),
    1549: (
        "当家に\n不満を抱く者がいるよう",
        "\n恩賞の",
        "検討を",
    ),
    1550: (
        "忠誠が揺らぎ出奔を企む者がいると\n家中で噂を耳にし",
        "\n何かを与えては…",
    ),
    1551: (
        "忠義に欠ける家臣がいる様子…\n"
        "何かを与えることで\n"
        "当家に繋ぎ留めては",
    ),
    1552: (
        "下の郡にて\n間者ありとの報を得",
        "\n兵を出せば妨害でき",
        "が…",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1543: (
        "",
        "026432",
        "023C",
        "0232",
        "014336040000050505",
    ),
    1544: (
        "",
        "01435A040000",
        "01438A040000",
        "014396010000050505",
    ),
    1545: ("", "014336040000050505"),
    1546: (
        "",
        "01438A040000",
        "014396010000050505",
    ),
    1547: ("", "014384040000", "050505"),
    1548: (
        "",
        "026432",
        "023C",
        "0232",
        "014336040000050505",
    ),
    1549: (
        "",
        "01431A020000",
        "01438A040000",
        "050505",
    ),
    1550: ("", "014314020000", "050505"),
    1551: ("", "050505"),
    1552: (
        "026432",
        "014314020000",
        "01433C040000",
        "050505",
    ),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    1545: ("", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    1543: (
        "",
        "026432",
        "023C",
        "0232",
        "014342040000050505",
    ),
    1544: (
        "",
        "014366040000",
        "014396040000",
        "01439C010000050505",
    ),
    1545: ("", "014342040000050505"),
    1546: (
        "",
        "014396040000",
        "01439C010000050505",
    ),
    1547: ("", "014390040000", "050505"),
    1548: (
        "",
        "026432",
        "023C",
        "0232",
        "014342040000050505",
    ),
    1549: (
        "",
        "014326020000",
        "014396040000",
        "050505",
    ),
    1550: ("", "01431A020000", "050505"),
    1551: EXPECTED_BASE_GAPS[1551],
    1552: (
        "026432",
        "01431A020000",
        "014348040000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    1543: 1573,
    1544: 1574,
    1545: 1575,
    1546: 1576,
    1547: 1577,
    1548: 1578,
    1549: 1579,
    1550: 1580,
    1551: 1581,
    1552: 1582,
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1544:1",
    "15:1547:1",
    "15:1550:1",
    "15:1551:0",
    "15:1552:2",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1543): (
        ("我等根据地的", "位于", "。\n在这片地区有", "城。"),
        ("", "026432", "023C", "0232", "050505"),
    ),
    ("TC", 1543): (
        ("我等根據地的", "位在", "，\n於此地有", "城。"),
        ("", "026432", "023C", "0232", "050505"),
    ),
    ("SC", 1544): (
        ("实现大志令人热血沸腾……\n首先确认下统治状况吧。",),
        ("", "050505"),
    ),
    ("TC", 1544): (
        ("實現大志令人熱血沸騰……\n首先將前往確認統治的狀況。",),
        ("", "050505"),
    ),
    ("SC", 1545): (
        (
            "要想达成天下平定，\n"
            "必须要统治全国半数以上的城，\n"
            "对畿内展开压制。",
        ),
        ("", "050505"),
    ),
    ("TC", 1545): (
        ("必須統治全國半數以上的城，\n並壓制畿內方可達成平定天下。",),
        ("", "050505"),
    ),
    ("SC", 1546): (
        (
            "只要有本家的武威，\n"
            "就可以率领所有的国家。\n"
            "请确认残存的势力。",
        ),
        ("", "050505"),
    ),
    ("TC", 1546): (
        (
            "將前往確認剩餘的勢力，\n"
            "衡量本家的實力是否足以\n"
            "收服所有的國家。",
        ),
        ("", "050505"),
    ),
    ("SC", 1547): (
        ("使其他势力从属，\n又或是进行歼灭，\n全听大人的命令…",),
        ("", "050505"),
    ),
    ("TC", 1547): (
        ("令其他勢力從屬，抑或攻滅。\n還請大人下令……",),
        ("", "050505"),
    ),
    ("SC", 1548): (
        ("曾经的根据地", "位于", "。\n这片地区有", "城。"),
        ("", "026432", "023C", "0232", "050505"),
    ),
    ("TC", 1548): (
        ("前根據地的", "位在", "，\n於此地有", "城。"),
        ("", "026432", "023C", "0232", "050505"),
    ),
    ("SC", 1549): (
        ("或许会有人\n对当家不满吧，\n请考虑进行赏赐吧。",),
        ("", "050505"),
    ),
    ("TC", 1549): (
        ("似乎有人對當家抱持不滿，\n望請考量封賞。",),
        ("", "050505"),
    ),
    ("SC", 1550): (
        (
            "听闻家中有人的忠诚心动摇，\n"
            "打算出逃。\n"
            "得给他们点好处……",
        ),
        ("", "050505"),
    ),
    ("TC", 1550): (
        ("據聞家中有人見異思遷，企圖出奔，\n不妨酌情封賞……",),
        ("", "050505"),
    ),
    ("SC", 1551): (
        (
            "似乎有家臣缺乏忠义之心……\n"
            "给他们些好处，\n"
            "把他们留在本家。",
        ),
        ("", "050505"),
    ),
    ("TC", 1551): (
        ("似乎有家臣缺乏忠義之心……\n不妨酌情封賞，\n使其留在當家。",),
        ("", "050505"),
    ),
    ("SC", 1552): (
        ("已获得情报，\n称", "下的郡有间谍。\n若出兵的话，可进行妨害……"),
        ("", "026432", "050505"),
    ),
    ("TC", 1552): (
        ("據報，在", "的郡中\n有間諜出現。\n應派遣士兵制止……"),
        ("", "026432", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1543: (
        (
            "Our main base, ",
            ", is located in ",
            ". There are ",
            " castles in the region.",
        ),
        ("", "026432", "023C", "0232", "050505"),
    ),
    1544: (
        (
            "Your ambitions are making you get ahead of yourself. First, we "
            "should confirm how your reign is proceeding.",
        ),
        ("", "050505"),
    ),
    1545: (
        (
            "If we wish to unify the entire land, we must rule over half of "
            "the nationÖs castles and take the capital.",
        ),
        ("", "050505"),
    ),
    1546: (
        (
            "Our military force should be sufficient to rule over the entire "
            "nation. We should check on the remaining clans.",
        ),
        ("", "050505"),
    ),
    1547: (
        (
            "We can turn other clans into our vassals or destroy them outright. "
            "The choice is yours.",
        ),
        ("", "050505"),
    ),
    1548: (
        (
            "Our former base, ",
            ", is located in ",
            ". There are ",
            " castles in the region.",
        ),
        ("", "026432", "023C", "0232", "050505"),
    ),
    1549: (
        (
            "Discontent is brewing within our clan. We should consider "
            "distributing rewards.",
        ),
        ("", "050505"),
    ),
    1550: (
        (
            "IÖve heard rumors within our clan that some people have lost "
            "their loyalty and are plotting to desert. Perhaps if we gave "
            "them something...",
        ),
        ("", "050505"),
    ),
    1551: (
        (
            "Some of our retainers apparently lack loyalty. If we gave them "
            "something, maybe they would regain their faith in our clan.",
        ),
        ("", "050505"),
    ),
    1552: (
        (
            "IÖve heard there are spies in one of ",
            "Ös counties. We should send soldiers to stop them.",
        ),
        ("", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B110_pristine_base_pc_jp_authoritative_"
    "territory_status_national_unification_requirements_disloyal_retainer_"
    "reward_and_spy_report_with_directly_verified_base_1543_1552_to_pk_"
    "1573_1582_mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_context_"
    "dynamic_castle_region_count_house_and_action_tokens_天下平定_as_천하_평정_"
    "畿内_as_기나이_当家_as_우리_가문_忠義_as_충의_出奔_as_출분_恩賞_as_"
    "은상_間者_as_간자_下知_as_하명_家中_as_가신단_1550_耳にし_past_"
    "opcode_stem_1545_pristine_opcode_and_current_flattened_skeleton_both_"
    "guarded_five_ellipsis_pairs_live_0143_stems_and_current_line_counts_"
    "preserved_runtime_fragment_pending_or_static_retranslated"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if PK_RECORD_MAP != {
        1543: 1573,
        1544: 1574,
        1545: 1575,
        1546: 1576,
        1547: 1577,
        1548: 1578,
        1549: 1579,
        1550: 1580,
        1551: 1581,
        1552: 1582,
    }:
        raise RuntimeError("segment 913 direct Base/PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 913 unexpected Base/PK JP exception")
    if EXPECTED_CURRENT_GAPS[1545] != ("", "050505"):
        raise RuntimeError("segment 913 current 1545 flattened skeleton drifted")
    if not raw_translations["15:1545:0"].endswith("제압해야 합니다."):
        raise RuntimeError(
            "segment 913 flattened 1545 did not restore a complete ending"
        )
    for record_id, prefix in ((1543, "우리의 본거지인"), (1548, "옛 본거지인")):
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(4)
        )
        if (
            actual[0] != prefix
            or actual[1] != "은(는)\n"
            or actual[2] != "에 있으며, 이 지방에는\n"
            or actual[3] != "개의 성이 있"
        ):
            raise RuntimeError(
                f"segment 913 castle-region-count direction drifted: "
                f"{record_id}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "천하 평정",
        "기나이",
        "우리 가문",
        "충의",
        "출분",
        "가신단",
        "은상",
        "간자",
        "하명",
        "병사",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 913 terminology drifted: {required}"
            )
    if any(
        term in joined
        for term in ("당가", "첩자", "포상", "탈주", "가신들 사이", "분부")
    ):
        raise RuntimeError("segment 913 forbidden terminology retained")
    stem_expectations = {
        "15:1543:3": "성이 있",
        "15:1544:0": "피가 끓",
        "15:1548:3": "성이 있",
        "15:1549:0": "있는 듯",
        "15:1550:0": "들었",
        "15:1552:0": "보고를 받",
        "15:1552:1": "수 있",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 913 live inflection stem drifted: {coordinate}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 913 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(raw_translations) != 25:
        raise RuntimeError("segment 913 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = (
        COMMON.build_segment_rows_with_current_gaps(
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
    )
    for row in rows:
        if row["coordinate"] == "15:1551:0":
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 25 or len(translations) != 25:
        raise RuntimeError("segment 913 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 913 validated count drifted")
    static_count = sum(
        row["scope_classification"] == "retranslated"
        and row["runtime_review"] == "not_required"
        for row in rows
    )
    runtime_pending_count = sum(
        row["scope_classification"] == "runtime_fragment_pending"
        and row["runtime_review"] == "pending"
        for row in rows
    )
    if static_count != 1 or runtime_pending_count != 24:
        raise RuntimeError("segment 913 static classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S913",
                "decision_count": len(rows),
                "retranslated": static_count,
                "runtime_fragment_pending": runtime_pending_count,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "current_flattened_opcode_records": [1545],
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
