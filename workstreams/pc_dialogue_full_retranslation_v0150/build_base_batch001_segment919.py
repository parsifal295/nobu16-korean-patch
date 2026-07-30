#!/usr/bin/env python3
"""Build Base authoring segment 919 decisions for the v0.15.0 retranslation."""

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


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S919.private.v1.jsonl"
)
SEGMENT = 919
EMPTY_COUNTY_POLITE = (
    "빈 군이 있다 하더군요\n"
    "다행히 여력이 있으니\n"
    "제게 맡겨 주십시오"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1614:0": "아무도 다스리지 않는 군이 있나\n그거 마침 잘됐군\n",
    "15:1614:1": "에게 맡겨라!",
    "15:1615:0": "빈 군이 있다 하오니\n",
    "15:1615:1": "에게 맡겨 주신다면\n풍요로운 땅으로 가꾸어 보이겠나이다",
    "15:1616:0": "아무도 다스리지 않는 군이 있다니…\n흠,",
    "15:1616:1": "은(는) 여력이 있소이다\n부디 맡겨 주시오",
    "15:1617:0": EMPTY_COUNTY_POLITE,
    "15:1618:0": (
        "몰수되어 주인 없는 땅이 있다 하오니\n"
        "제게 영지로 맡겨 주신다면\n"
        "전장에서 활약해 보이겠소이다"
    ),
    "15:1619:0": (
        "아무도 다스리지 않는 군이 있다 하오니…\n"
        "부디 제게 맡겨 주실 수 없겠사옵니까"
    ),
    "15:1620:0": (
        "빈 군이 있사옵니다\n"
        "부디 지행지로 내려 주시옵소서\n"
        "그 은혜에 반드시 보답하겠나이다"
    ),
    "15:1621:0": (
        "호오, 몰수되어 주인 없는 땅이라\n"
        "지행지로 제게 맡겨 주시오\n"
        "잘 다스려 보이겠소이다"
    ),
    "15:1622:0": "아무도 다스리지 않는 군이 있습니다\n부디,",
    "15:1622:1": "에게 맡겨 주십시오\n훌륭한 땅으로 가꾸어 보이겠습니다!",
    "15:1623:0": "아무도 다스리지 않는 군이 있소\n부디",
    "15:1623:1": "에게 맡겨 주었으면 하오\n결코 후회하게 하지 않겠소",
    "15:1624:0": "아무도 다스리지 않는 군이 있어요\n부디,",
    "15:1624:1": "에게 맡겨 주세요\n훌륭한 땅으로 가꾸어 보이겠어요",
    "15:1625:0": EMPTY_COUNTY_POLITE,
    "15:1626:0": (
        "아무래도 빈 군이 있는 듯합니다…\n"
        "마침 여력이 있는 자가 있습니다"
    ),
    "15:1626:1": "\n영주로 삼아 다스리게 해 보는 것은 어떻겠습니까?",
    "15:1627:0": "영주가 없는 군이",
    "15:1627:1": "\n누군가에게 군을 내려\n발전을 맡기는 것은 어떠하신지",
    "15:1627:2": "인가",
}
RECORD_ARITIES = {
    1614: 2,
    1615: 2,
    1616: 2,
    **{record_id: 1 for record_id in range(1617, 1622)},
    1622: 2,
    1623: 2,
    1624: 2,
    1625: 1,
    1626: 2,
    1627: 3,
}
EXPECTED_BASE_JP = {
    1614: (
        "誰も治めてねえ郡があるのか\nそれは丁度良い\n",
        "に任せろ！",
    ),
    1615: (
        "空いている郡があるとか\n",
        "にお任せくだされば\n豊かな地に育ててみせまするぞ",
    ),
    1616: (
        "誰も治めておらぬ郡があると…\nふむ、",
        "ならば余裕がありますぞ\n是非、お任せくだされ",
    ),
    1617: (
        "空いている郡があるそうですね\n幸い、余裕がありますので\n"
        "お任せください",
    ),
    1618: (
        "闕所地がござるとか\n知行としてお任せくだされば\n"
        "戦にて活躍してみせましょうぞ",
    ),
    1619: (
        "誰も治めておらぬ郡があるとか…\n是非とも、お任せいただけませぬか",
    ),
    1620: (
        "空いている郡がございますね\nどうぞ知行地としてお与えください\n"
        "そのご恩には必ず応えましょう",
    ),
    1621: (
        "ほう、闕所地とな\n知行地としてお任せくだされい\n"
        "良う治めてみせましょうぞ",
    ),
    1622: (
        "誰も治めてない郡があります\n是非、",
        "に任せてください\n素晴らしい地に育ててみせます！",
    ),
    1623: (
        "誰も治めてない郡がある\nどうか",
        "に預けてほしい\n絶対に後悔はさせぬ",
    ),
    1624: (
        "誰も治めてない郡がありますわ\n是非、",
        "にお任せを\n素晴らしい地に育ててみせます",
    ),
    1625: (
        "空いている郡があるそうですね\n幸い、余裕がありますので\n"
        "お任せください",
    ),
    1626: (
        "どうやら空いている郡があるとか…\n幸いにも手すきの者が",
        "\n領主として治めさせてみては？",
    ),
    1627: (
        "領主がおらぬ郡が",
        "\nどなたかに郡を与えて\n発展を任せるのはいかが",
        "か",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1614: ("", "014301000000", "050505"),
    1615: ("", "014301000000", "050505"),
    1616: ("", "014301000000", "050505"),
    **{
        record_id: ("", "050505")
        for record_id in range(1617, 1622)
    },
    1622: ("", "014301000000", "050505"),
    1623: ("", "014301000000", "050505"),
    1624: ("", "014301000000", "050505"),
    1625: ("", "050505"),
    1626: ("", "0143b2000000", "050505"),
    1627: (
        "",
        "0143520000000143ce020000",
        "014356020000",
        "050505",
    ),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    1626: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1627: (
        "",
        "0143520000000143da020000",
        "014362020000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    1614: 1644,
    1615: 1645,
    1616: 1646,
    1617: 1647,
    1618: 1648,
    1619: 1649,
    1620: 1650,
    1621: 1651,
    1622: 1652,
    1623: 1653,
    1624: 1654,
    1625: 1655,
    1626: 1656,
    1627: 1657,
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1616:0",
    "15:1619:0",
    "15:1626:0",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_RECORD_IDS = {*range(1617, 1622), 1625}

SHARED_AUXILIARY = {
    ("SC", 1616): (
        (
            "原来有郡无人治理啊…\n嗯，",
            "应该可以轻松胜任，\n请务必交给我。",
        ),
        ("", "014301000000", "050505"),
    ),
    ("TC", 1616): (
        (
            "既有無人治理之郡……\n嗯，時間上綽綽有餘，\n務必交由",
            "治理。",
        ),
        ("", "014301000000", "050505"),
    ),
    ("SC", 1617): (
        ("据报有郡空置。\n所幸我还有精力，\n请交给我吧。",),
        ("", "050505"),
    ),
    ("TC", 1617): (
        ("似乎有個郡無人看管。\n所幸時間上綽有餘裕，\n還請交給我代管。",),
        ("", "050505"),
    ),
    ("SC", 1618): (
        ("似乎有无主之地。\n请任命我为知行。\n我会在战役中大放光彩的。",),
        ("", "050505"),
    ),
    ("TC", 1618): (
        ("聽說有塊闕所地……\n若能作為知行交給在下，\n戰時必將加以運用。",),
        ("", "050505"),
    ),
    ("SC", 1622): (
        ("有无人治理的郡。\n请务必交给", "。\n我定会将它变成福地的！"),
        ("", "014301000000", "050505"),
    ),
    ("TC", 1622): (
        ("有個郡無人治理。\n請大人務必交給", "，\n保證讓該郡化為寶地！"),
        ("", "014301000000", "050505"),
    ),
    ("SC", 1626): (
        ("看来，有空着的郡……\n所幸有武将可供指派。\n不妨指派为领主治理看看如何？",),
        ("", "050505"),
    ),
    ("TC", 1626): (
        ("看來，有空著的郡……\n所幸有武將可供指派。\n不妨指派為領主治理看看如何？",),
        ("", "050505"),
    ),
    ("SC", 1627): (
        ("看来，是无领主的郡。\n不妨指派麾下进行知行，\n尝试发展该郡如何？",),
        ("", "050505"),
    ),
    ("TC", 1627): (
        ("看來，是無領主的郡。\n不妨指派麾下進行知行，\n嘗試發展該郡如何？",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1616: (
        (
            "ThereÖs a county that doesnÖt have anybody watching over it, "
            "eh? IÖm certainly up to the task. Just leave it to me.",
        ),
        ("", "050505"),
    ),
    1617: (
        (
            "There is apparently still an empty county. Fortunately, I have "
            "plenty of time, so leave it to me.",
        ),
        ("", "050505"),
    ),
    1618: (
        (
            "So youÖve taken some land? Leave the governing to me, and IÖll "
            "show my worth in battle.",
        ),
        ("", "050505"),
    ),
    1622: (
        (
            "There is a county without a ruler. Allow me to handle it, and "
            "IÖll cultivate a fine land.",
        ),
        ("", "050505"),
    ),
    1626: (
        (
            "There seems to be an open county. Luckily, I know some people "
            "who have the time. Shall we appoint one as land holder?",
        ),
        ("", "050505"),
    ),
    1627: (
        (
            "You have a county with no land holder, yes? Why not give it to "
            "someone and task them with improving it?",
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
HISTORICAL_REFERENCE_URLS = (
    "https://asakura-museum.pref.fukui.lg.jp/database_list/"
    "047_historicaldata/detail.php?id=6",
    "https://rekihaku.repo.nii.ac.jp/records/1124",
)
BASIS = (
    "review_queue_base_msggame_B110_C_pristine_base_pc_jp_authoritative_"
    "county_fief_request_speaker_voice_variants_and_landholder_proposal_"
    "with_explicit_base1614_to1627_pk1644_to1657_mapping_exact_base_pk_"
    "sc_tc_and_pk_en_auxiliary_context_kessho_land_historical_meaning_"
    "made_explicit_as_confiscated_ownerless_land_chigyo_as_fief_and_"
    "chigyouchi_as_chigyouchi_base1617_1625_source_and_korean_canonical_"
    "exact_reuse_current1626_flattened_runtime_skeleton_recorded_source_"
    "opcode_stems_token_directions_and_current_layout_preserved_static_"
    "and_runtime_split"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "군",
        "몰수되어 주인 없는 땅",
        "영지",
        "지행지",
        "영주",
        "여력이",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 919 required meaning drifted: {required}")
    for forbidden in ("궐소", "몰수지", "지행으로", "闕", "。", "、"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 919 retained opaque or forbidden term: {forbidden}"
            )
    if EXPECTED_BASE_JP[1617] != EXPECTED_BASE_JP[1625]:
        raise RuntimeError("segment 919 Base1617/1625 source canonical drifted")
    if tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 1617)])
    ) != tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 1625)])
    ):
        raise RuntimeError("segment 919 pristine Base1617/1625 equality drifted")
    if (
        raw_translations["15:1617:0"] != EMPTY_COUNTY_POLITE
        or raw_translations["15:1625:0"] != EMPTY_COUNTY_POLITE
    ):
        raise RuntimeError("segment 919 Base1617/1625 Korean canonical drifted")
    if not raw_translations["15:1616:1"].startswith("은(는)"):
        raise RuntimeError("segment 919 record 1616 person-token relation drifted")
    if raw_translations["15:1624:1"] != (
        "에게 맡겨 주세요\n훌륭한 땅으로 가꾸어 보이겠어요"
    ):
        raise RuntimeError("segment 919 feminine speaker voice drifted")
    if raw_translations["15:1626:0"].endswith(("있", "있으")):
        raise RuntimeError("segment 919 flattened record 1626 was left as a stem")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 919 ellipsis seed/pair drifted: {coordinate}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1614, 1644),
        (1615, 1645),
        (1616, 1646),
        (1617, 1647),
        (1618, 1648),
        (1619, 1649),
        (1620, 1650),
        (1621, 1651),
        (1622, 1652),
        (1623, 1653),
        (1624, 1654),
        (1625, 1655),
        (1626, 1656),
        (1627, 1657),
    }:
        raise RuntimeError("segment 919 explicit Base-to-PK mapping drifted")
    if len(HISTORICAL_REFERENCE_URLS) != 2:
        raise RuntimeError("segment 919 historical reference set drifted")


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
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
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
    if len(rows) != 23 or len(translations) != 23:
        raise RuntimeError("segment 919 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 919 validated count drifted")
    static_count = sum(
        row["scope_classification"] == "retranslated" for row in rows
    )
    if static_count != 6:
        raise RuntimeError("segment 919 static decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S919",
                "decision_count": len(rows),
                "retranslated": static_count,
                "runtime_fragment_pending": len(rows) - static_count,
                "explicit_pk_mapping": True,
                "canonical_base1617_1625_reuse": True,
                "current_flattened_opcode_records": [1626],
                "historical_reference_count": len(HISTORICAL_REFERENCE_URLS),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
