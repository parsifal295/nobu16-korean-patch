#!/usr/bin/env python3
"""Build Base authoring segment 901 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment885 as CANONICAL_B107
import build_base_batch001_segment884 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S901.private.v1.jsonl"
)
SEGMENT = 901
RATIONS_CHANGE_ARROW = ("의 병량이", "→", "에")
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:1452:{literal_id}": translation
        for literal_id, translation in enumerate(RATIONS_CHANGE_ARROW)
    },
    **{
        f"15:1453:{literal_id}": translation
        for literal_id, translation in enumerate(
            CANONICAL_B107.TROOP_CHANGE_ARROW
        )
    },
    "15:1454:0": "에서",
    "15:1454:1": "이(가) 벌인",
    "15:1454:2": "을(를) 저지",
    "15:1455:0": (
        "에 유언비어를 퍼뜨려\n"
        "성안 장수들의 충의를\n"
        "뒤흔들고자"
    ),
    "15:1456:0": "유언비어를",
    "15:1456:1": (
        "에 퍼뜨려\n"
        "성에 봉직하는 적장들을\n"
        "서로 의심하게 만들"
    ),
    "15:1457:0": "두려운 것은 사람의 마음…\n",
    "15:1457:1": (
        "에 유언비어를 퍼뜨려\n"
        "주군을 향한 충성에 흠집을 내고자 하옵니다"
    ),
    "15:1458:0": "을(를) 공략할 한 수로\n성주·",
    "15:1458:1": (
        "와 주군 사이를 갈라\n"
        "이반으로 이끄는 것도 좋은 계책"
    ),
    "15:1459:0": "의 허점은 성주에게 있으니\n",
    "15:1459:1": (
        "이(가) 충의를 바칠 대상은\n"
        "달라질 여지가 있다고 보"
    ),
    "15:1460:0": "공성이란 성을 지키는 장수의 마음을 공략하는 법\n",
    "15:1460:1": "의 성주·",
    "15:1460:2": (
        "의 충의는\n"
        "성의 방비만큼 굳건하지는 않은 듯…"
    ),
}
RECORD_ARITIES = {
    1452: 3,
    1453: 3,
    1454: 3,
    1455: 1,
    1456: 2,
    1457: 2,
    1458: 2,
    1459: 2,
    1460: 3,
}
EXPECTED_BASE_JP = {
    1452: ("の兵糧が", "→", "に"),
    1453: ("の兵力が", "→", "に"),
    1454: ("にて", "からの", "を阻止"),
    1455: (
        "に流言飛語を放ち\n"
        "城内の諸将の忠義を\n"
        "揺るがせたく",
    ),
    1456: (
        "流言を",
        "にしかけ\n城に仕える敵将たちを\n疑心暗鬼に陥れ",
    ),
    1457: (
        "恐ろしきは人の心…\n",
        "に流言を放ち\n主君への忠誠に傷を付けたく",
    ),
    1458: (
        "攻略への一手として\n城主",
        "と主君の仲を裂き\n離反に導くのも良き策",
    ),
    1459: (
        "の隙は城主にあり\n",
        "が忠義を向ける先は\n変ずる余地があると見",
    ),
    1460: (
        "城攻めとは城将の心を攻めるもの\n",
        "の",
        "が忠義\n城の構えほどには堅くないようで…",
    ),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1452: ("026432", "0232", "0233", "050505"),
    1453: ("026432", "0232", "0233", "050505"),
    1454: ("026432", "025032", "023c", "050505"),
    1455: ("026432", "0143e2000000050505"),
    1456: ("", "026432", "01431e040000050505"),
    1457: ("", "026432", "050505"),
    1458: ("026432", "024833", "01431e010000050505"),
    1459: ("026432", "024833", "01433c040000050505"),
    1460: ("", "026432", "024833", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1456: ("", "026432", "01432a040000050505"),
    1459: ("026432", "024833", "014348040000050505"),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1457:0", "15:1460:2"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

SHARED_AUXILIARY = {
    ("SC", 1452): (
        ("的军粮从", "→", "。"),
        ("026432", "0232", "0233", "050505"),
    ),
    ("TC", 1452): (
        ("的軍糧", "→", "。"),
        ("026432", "0232", "0233", "050505"),
    ),
    ("SC", 1453): (
        ("的兵力由", "→", "。"),
        ("026432", "0232", "0233", "050505"),
    ),
    ("TC", 1453): (
        ("的兵力", "→", "。"),
        ("026432", "0232", "0233", "050505"),
    ),
    ("SC", 1454): (
        ("于", "阻止", "的", "。"),
        ("", "026432", "025032", "023c", "050505"),
    ),
    ("TC", 1454): (
        ("於", "阻止", "的", "。"),
        ("", "026432", "025032", "023c", "050505"),
    ),
    ("SC", 1455): (
        ("对", "放出流言飞语，\n使城内诸将的忠义\n产生动摇。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1455): (
        ("對", "放出流言飛語，\n使城內諸將的忠義\n產生動搖。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1456): (
        ("对", "发动流言，\n使效力于城中的敌将们\n疑心暗鬼。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1456): (
        ("對", "發動流言，\n使效力於城中的敵將們\n疑心暗鬼。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1457): (
        ("惟恐人心……\n对", "施放流言，\n伤害对主君的忠诚。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1457): (
        ("惟恐人心……\n對", "施放流言，\n傷害對主君的忠誠。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1458): (
        (
            "作为攻略",
            "的手段，\n破坏城主",
            "与君主之间的关系，\n使其叛变可谓个好策略。",
        ),
        ("", "026432", "024833", "050505"),
    ),
    ("TC", 1458): (
        (
            "作為攻略",
            "的手段，\n破壞城主",
            "與君主之間的關係，\n使其叛變可謂個好策略。",
        ),
        ("", "026432", "024833", "050505"),
    ),
    ("SC", 1459): (
        ("的破绽便是其城主。\n", "效忠的对象\n还是有改变的余地。"),
        ("026432", "024833", "050505"),
    ),
    ("TC", 1459): (
        ("的弱點即城主。\n", "效忠的對象\n仍有變數。"),
        ("026432", "024833", "050505"),
    ),
    ("SC", 1460): (
        ("所谓攻城，攻的是守将的心。\n", "的", "，\n其忠义可不如城墙那般坚固……"),
        ("", "026432", "024833", "050505"),
    ),
    ("TC", 1460): (
        ("所謂攻城，攻的是守將的心。\n", "的", "，\n其忠義可不如城牆那般堅固……"),
        ("", "026432", "024833", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1452: (
        ("Ös supplies went from ", " to ", "."),
        ("026432", "0232", "0233", "050505"),
    ),
    1453: (
        ("Ös soldiers went from ", " to ", "."),
        ("026432", "0232", "0233", "050505"),
    ),
    1454: (
        ("The ", "Ös ", " at ", " was prevented."),
        ("", "025032", "023c", "026432", "050505"),
    ),
    1455: (
        (
            "LetÖs spread rumors around ",
            ". The loyalty of generals in their domain will waver.",
        ),
        ("", "026432", "050505"),
    ),
    1456: (
        (
            "IÖd like to spread rumors around ",
            " to arouse suspicion in the castleÖs officers.",
        ),
        ("", "026432", "050505"),
    ),
    1457: (
        (
            "A humanÖs heart is the most fearsome thing... "
            "IÖll spread rumors around ",
            " to damage trust in the castleÖs lord.",
        ),
        ("", "026432", "050505"),
    ),
    1458: (
        (
            "We could create a rift between the lord, ",
            ", and their master in order to capture ",
            ". If weÖre successful, he might even defect.",
        ),
        ("", "024833", "026432", "050505"),
    ),
    1459: (
        (
            "The key to conquering ",
            " is its lord. ",
            "Ös loyalties could be swayed...",
        ),
        ("", "026432", "024833", "050505"),
    ),
    1460: (
        (
            "An attack on the castle is an attack on the hearts of its officers. ",
            "Ös loyalties are apparently not as stable as the ",
            " castle walls.",
        ),
        ("", "024833", "026432", "050505"),
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
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "rations_and_troop_change_ui_operation_prevention_and_rumor_loyalty_"
    "defection_proposals_with_uniform_plus_15_pk_mapping_base_pk_sc_tc_"
    "exact_pk_en_auxiliary_context_b107_troop_change_ui_canonical_"
    "ryuganhigo_yuugenbiigo_chuugi_rihan_terminology_castle_defending_"
    "general_distinguished_from_castle_lord_master_faction_token_relations_"
    "live_inflection_stems_current_layout_and_opcode_skeleton_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if tuple(
        raw_translations[f"15:1453:{literal_id}"]
        for literal_id in range(3)
    ) != CANONICAL_B107.TROOP_CHANGE_ARROW:
        raise RuntimeError("segment 901 B107 troop-change UI canonical drifted")
    if tuple(
        raw_translations[f"15:1452:{literal_id}"]
        for literal_id in range(3)
    ) != RATIONS_CHANGE_ARROW:
        raise RuntimeError("segment 901 rations-change UI canonical drifted")
    if (
        raw_translations["15:1452:0"].replace("병량", "병력")
        != raw_translations["15:1453:0"]
    ):
        raise RuntimeError("segment 901 rations/troop UI distinction drifted")
    stem_expectations = {
        "15:1455:0": "뒤흔들고자",
        "15:1456:1": "만들",
        "15:1458:1": "좋은 계책",
        "15:1459:1": "보",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 901 live inflection stem drifted: {coordinate}"
            )
    if (
        raw_translations["15:1454:1"] != "이(가) 벌인"
        or raw_translations["15:1454:2"] != "을(를) 저지"
    ):
        raise RuntimeError("segment 901 operation prevention relation drifted")
    if (
        raw_translations["15:1458:0"]
        != "을(를) 공략할 한 수로\n성주·"
        or raw_translations["15:1460:1"] != "의 성주·"
    ):
        raise RuntimeError("segment 901 castle-lord token relation drifted")
    joined = "\n".join(translations.values())
    for required in (
        "유언비어",
        "충의",
        "이반",
        "성주",
        "성을 지키는 장수",
        "주군",
        "봉직",
        "서로 의심",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 901 rumor/defection semantics drifted: {required}"
            )
    if any(term in joined for term in ("루머", "충성의", "배반")):
        raise RuntimeError(
            "segment 901 retained inconsistent rumor/loyalty terminology"
        )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 901 ellipsis seed/pair drifted: {coordinate}"
            )


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
        raise RuntimeError("segment 901 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S901",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "change_and_prevention_ui_records": 3,
                "rumor_and_defection_proposal_records": 6,
                "explicit_pk_mapping": True,
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
