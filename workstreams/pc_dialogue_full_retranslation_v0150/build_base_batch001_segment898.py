#!/usr/bin/env python3
"""Build Base authoring segment 898 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment810 as CAPTURE_S810
import build_base_batch001_segment897 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S898.private.v1.jsonl"
)
SEGMENT = 898
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1428:0": (
        "이(가) 불우한 처지라 하여\n"
        "권해 보았더니 등용에 응할 듯하옵니다\n"
        "사관을 허락해 주시"
    ),
    "15:1428:1": "인가?",
    "15:1429:0": CAPTURE_S810.RAW_TRANSLATIONS["15:373:0"],
    "15:1429:1": CAPTURE_S810.RAW_TRANSLATIONS["15:373:1"],
    "15:1430:0": (
        "이웃 나라의 출병을 방해하려면\n"
        "적 영지에 대한 방화가 적합하옵니다\n"
        "노릴 곳은"
    ),
    "15:1430:1": "근처가 어떻겠습니까",
    "15:1431:0": "지금이라면",
    "15:1431:1": "에 불을 질러\n방비에 구멍을 낼 수 있",
    "15:1431:2": "\n부디,",
    "15:1431:3": "허락을…",
    "15:1432:0": "견고한 성을 함락하려면 뒤쪽의 허점부터…\n",
    "15:1432:1": (
        "에 소수의 병력으로 불을 질러\n"
        "방비를 약화시켜 보는 것은 어떻겠습니까"
    ),
    "15:1433:0": "방화야말로",
    "15:1433:1": (
        "공략의 지름길\n"
        "성에 복속된 마을마다 불을 질러\n"
        "병사를 내보내지 못하게 만들"
    ),
    "15:1434:0": "의 대군은 위협",
    "15:1434:1": (
        "자\n"
        "저 성의 움직임을 봉쇄하고자\n"
        "방화로 병량을 빼앗아 보는 것은 어떻겠소?"
    ),
    "15:1435:0": "근처는 경비가 허술한 모양\n출병용 병량을 불태워\n",
    "15:1435:1": "의 전력을 줄이",
    "15:1436:0": "인근의",
    "15:1436:1": (
        "은(는) 정예가 즐비하오니\n"
        "그 창끝이 우리를 향하지 않도록\n"
        "은밀히 출병을 방해해 두고자 하옵니다"
    ),
    "15:1437:0": (
        "을(를) 공략할 때 성가신 것은 증원\n"
        "적 영지 곳곳에 불을 질러\n"
        "후원군을 보내지 못하게 하"
    ),
    "15:1438:0": "공작은 우리 군단의 특기\n",
    "15:1438:1": "의 출병을 방해하고자\n적 영지 곳곳에 불을 질러 보이",
}
RECORD_ARITIES = {
    1428: 2,
    1429: 2,
    1430: 2,
    1431: 4,
    1432: 2,
    1433: 2,
    1434: 2,
    1435: 2,
    1436: 2,
    1437: 1,
    1438: 2,
}
EXPECTED_BASE_JP = {
    1428: (
        "が不遇をかこっていると聞き\n"
        "誘ってみたところ、登用に応じそうな様子\n"
        "仕官の許可をいただけ",
        "か？",
    ),
    1429: ("が", "を登用"),
    1430: (
        "隣国による出兵を妨害するならば\n"
        "敵領への焼討が適しております\n"
        "狙い目は",
        "辺りでしょうか",
    ),
    1431: (
        "今ならば",
        "に火をかけ\nその防備に風穴を開けられ",
        "\nどうか、",
        "許可を…",
    ),
    1432: (
        "堅城を落とすには搦手から…\n",
        "に小勢で火を放ち\n防備を削いでみては",
    ),
    1433: (
        "焼討こそが",
        "攻略への近道\n城に服属する村々に火を放ち\n兵など出せぬようにしてや",
    ),
    1434: (
        "の大軍は脅威",
        "な\nかの城の身動きを封じるため\n焼討にて軍糧を奪ってはいかが？",
    ),
    1435: (
        "近辺は警備が手薄な様子\n出兵のための兵糧を焼き払い\n",
        "の手駒を減ら",
    ),
    1436: (
        "近隣の",
        "は精鋭揃い\n我らにその矛先が向かぬよう\n密かに出兵の妨害をしておこうかと",
    ),
    1437: (
        "攻めにて厄介なのは増援\n"
        "ここは敵領広くに焼討を仕掛け\n"
        "後詰が叶わぬように",
    ),
    1438: (
        "工作は我が軍団の得意とするところ\n",
        "の出兵を妨害するため\n敵領各地を焼討してみせ",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    1434: (
        "の大軍は脅威",
        "\nかの城の身動きを封じるため\n焼討にて軍糧を奪ってはいかが？",
    ),
}
EXPECTED_BASE_GAPS = {
    1428: ("014322000000", "0143E0020000", "050505"),
    1429: ("024633", "024733", "050505"),
    1430: ("", "026432", "050505"),
    1431: ("", "026432", "01433C040000", "01438A040000", "050505"),
    1432: ("", "026432", "050505"),
    1433: ("", "026432", "014336040000050505"),
    1434: ("026432", "01432C020000", "050505"),
    1435: ("026432", "025032", "01437E040000050505"),
    1436: ("", "026432", "050505"),
    1437: ("026432", "014394000000050505"),
    1438: ("", "025032", "01433C040000050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1428: ("014322000000", "0143EC020000", "050505"),
    1431: ("", "026432", "014348040000", "014396040000", "050505"),
    1433: ("", "026432", "014342040000050505"),
    1434: ("026432", "0143380200000143DA020000", "050505"),
    1435: ("026432", "025032", "01438A040000050505"),
    1438: ("", "025032", "014348040000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 15 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:1431:3", "15:1432:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1428): (
        (
            "听闻",
            "有些不得志，\n尝试过邀请后，貌似有回应登用的打算。\n可否答允让其仕官呢？",
        ),
        ("", "014322000000", "050505"),
    ),
    ("TC", 1428): (
        ("耳聞", "抱怨機遇不佳故嘗試勸誘，\n對方似乎有意效忠。\n是否令其仕官？"),
        ("", "014322000000", "050505"),
    ),
    ("SC", 1429): (
        ("登用了", "。"),
        ("024633", "024733", "050505"),
    ),
    ("TC", 1429): (
        ("登庸", "。"),
        ("024633", "024733", "050505"),
    ),
    ("SC", 1430): (
        ("若邻国出兵妨害的话，\n适合向敌方领地实施火攻。\n目标就定为", "附近吧。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1430): (
        ("若鄰國出兵妨害的話，\n適合向敵方領地實施火攻。\n目標就定為", "附近吧。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1431): (
        ("现在对", "发动火攻，\n就能于其防备上开风穴。\n请予以允诺……"),
        ("", "026432", "050505"),
    ),
    ("TC", 1431): (
        ("現在對", "發動火攻，\n就能於其防備上開風穴。\n請予以允諾……"),
        ("", "026432", "050505"),
    ),
    ("SC", 1432): (
        ("若欲攻下坚城，则应里应外合……\n用一小队人马向", "放火，\n削减其防备如何？"),
        ("", "026432", "050505"),
    ),
    ("TC", 1432): (
        ("若欲攻下堅城，則應趁其虛而入……\n以小勢力對", "放火，\n削減防備如何？"),
        ("", "026432", "050505"),
    ),
    ("SC", 1433): (
        ("火攻才是攻下", "的捷径。\n对城的附属村庄放火，\n无需出兵。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1433): (
        ("火攻才是攻下", "的捷徑。\n對城的附屬村莊放火，\n無需出兵。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1434): (
        ("的大军是个威胁。\n为了让他们动弹不得，\n用火攻夺走军粮如何？",),
        ("026432", "050505"),
    ),
    ("TC", 1434): (
        ("的大軍是個威脅。\n不妨以火攻奪走軍糧，\n壓制該城如何？",),
        ("026432", "050505"),
    ),
    ("SC", 1435): (
        ("周边貌似戒备松懈。\n通过放火烧田、夺取军粮，\n削减", "的实力吧。"),
        ("026432", "025032", "050505"),
    ),
    ("TC", 1435): (
        ("周邊的警備鬆懈。\n那就放火燒田，奪取軍糧，\n削減", "的力量吧。"),
        ("026432", "025032", "050505"),
    ),
    ("SC", 1436): (
        ("近邻的", "具有精锐力量。\n为了不让其矛头指向我等，\n秘密出兵进行干扰吧。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1436): (
        ("近鄰的", "具有精銳力量。\n為了不讓其矛頭指向我等，\n秘密出兵進行干擾吧。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1437): (
        ("攻打", "的难处在于增援。\n对敌领地实施大范围火攻，\n让其无法实现后援。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1437): (
        ("攻打", "的難處在於增援。\n對敵領地實施大範圍火攻，\n讓其無法實現後援。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1438): (
        ("让我军团的智者对", "的城\n一并进行火攻吧。\n应该能够大幅削弱敌战力。"),
        ("", "025032", "050505"),
    ),
    ("TC", 1438): (
        ("讓我方軍團的智者施計，\n一併燒毀", "的多個城吧。\n這樣應可大幅削弱敵人的戰力。"),
        ("", "025032", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1428: (
        (
            "I invited him because he was down on his luck. He seems open to "
            "the idea of serving us. Of course, IÖd need your permission first.",
        ),
        ("", "050505"),
    ),
    1429: (
        (" has employed ", "."),
        ("024633", "024733", "050505"),
    ),
    1430: (
        (
            "If we want to obstruct the flow of soldiers from neighboring "
            "territories, we should raze the land. IÖd say the best place to "
            "start would be ",
            ".",
        ),
        ("", "026432", "050505"),
    ),
    1431: (
        ("Let me start a fire at ", " to breach their defenses. Please, all I need is your go ahead."),
        ("", "026432", "050505"),
    ),
    1432: (
        (
            "A strong castle is best approached from its weakest point... "
            "LetÖs send a small force to start a fire at ",
            ". ThatÖll chip away at their defenses.",
        ),
        ("", "026432", "050505"),
    ),
    1433: (
        (
            "The quickest way to capture ",
            " is by setting it all ablaze. Set fire to the nearby villages, "
            "and theyÖll be too busy to send out troops.",
        ),
        ("", "026432", "050505"),
    ),
    1434: (
        (
            "Ös great army is a threat. We could set fire to their territory "
            "to deprive them of provisions, which should stop their movements.",
        ),
        ("026432", "050505"),
    ),
    1435: (
        (
            "The area around ",
            " is poorly guarded. LetÖs burn their supplies to reduce the "
            "number of pawns for the ",
            " to play with.",
        ),
        ("", "026432", "025032", "050505"),
    ),
    1436: (
        (
            "Ös soldiers are much too strong for us. WeÖll never survive their "
            "attack, so letÖs obstruct their forces in secret.",
        ),
        ("026432", "050505"),
    ),
    1437: (
        (
            "The most vexing part of attacking ",
            " will be the reinforcements. If we raze their territory, they "
            "wonÖt be able to send reserves.",
        ),
        ("", "026432", "050505"),
    ),
    1438: (
        (
            "My provinceÖs specialty is destabilization. To obstruct the ",
            "Ös soldiers, weÖll burn their territory to the ground.",
        ),
        ("", "025032", "050505"),
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "recruitment_permission_and_results_arson_proposals_with_explicit_plus_15_"
    "base_to_pk_mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_context_"
    "dynamic_officer_castle_house_region_tokens_yakiuchi_command_as_banghwa_"
    "and_actions_as_setting_fire_karamete_rear_weak_point_gunryo_hyoryo_both_"
    "byeongnyang_godzume_reinforcement_consistent_current_layout_opcode_"
    "stems_1428_opaque_0143_and_1434_current_proven_boundaries_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for literal_id in range(2):
        if raw_translations[f"15:1429:{literal_id}"] != (
            CAPTURE_S810.RAW_TRANSLATIONS[f"15:373:{literal_id}"]
        ):
            raise RuntimeError("segment 898 recruitment result canonical drifted")
    if (
        EXPECTED_BASE_GAPS[1428][0] != "014322000000"
        or EXPECTED_BASE_GAPS[1428][1] != "0143E0020000"
        or EXPECTED_PK_JP_GAPS[1428][1] != "0143EC020000"
        or not raw_translations["15:1428:0"].startswith("이(가)")
        or raw_translations["15:1428:0"] != (
            "이(가) 불우한 처지라 하여\n"
            "권해 보았더니 등용에 응할 듯하옵니다\n"
            "사관을 허락해 주시"
        )
        or raw_translations["15:1428:1"] != "인가?"
    ):
        raise RuntimeError(
            "segment 898 1428 opaque 0143 boundary split drifted"
        )
    stem_guards = {
        "15:1431:1": "있",
        "15:1433:1": "만들",
        "15:1435:1": "줄이",
        "15:1437:0": "하",
        "15:1438:1": "보이",
    }
    for coordinate, ending in stem_guards.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 898 dynamic conjugation stem drifted: {coordinate}"
            )
    if (
        not raw_translations["15:1434:0"].endswith("위협")
        or not raw_translations["15:1434:1"].startswith("자\n")
        or EXPECTED_BASE_JP[1434][1] == EXPECTED_PK_JP[1434][1]
        or not EXPECTED_BASE_JP[1434][1].startswith("な\n")
        or not EXPECTED_PK_JP[1434][1].startswith("\n")
        or EXPECTED_PK_JP_GAPS[1434][1]
        != "0143380200000143DA020000"
    ):
        raise RuntimeError(
            "segment 898 1434 Base-only な split copula assembly drifted"
        )
    if (
        "방화가 적합" not in raw_translations["15:1430:0"]
        or raw_translations["15:1433:0"] != "방화야말로"
        or "방화로 병량" not in raw_translations["15:1434:1"]
        or "불을 질러" not in raw_translations["15:1437:0"]
        or "불을 질러" not in raw_translations["15:1438:1"]
    ):
        raise RuntimeError(
            "segment 898 焼討 command/prose distinction drifted"
        )
    if (
        "뒤쪽의 허점" not in raw_translations["15:1432:0"]
        or "뒷문" in raw_translations["15:1432:0"]
    ):
        raise RuntimeError("segment 898 搦手 rear weak-point sense drifted")
    if not raw_translations["15:1436:1"].startswith(
        "은(는) 정예가 즐비하오니\n"
    ):
        raise RuntimeError("segment 898 1436 causal speaker register drifted")
    joined = "\n".join(translations.values())
    for required in (
        "사관",
        "등용",
        "방화",
        "불을 질러",
        "불태워",
        "뒤쪽의 허점",
        "병량",
        "후원군",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 898 meaning or terminology drifted: {required}")
    for forbidden in (
        "출사",
        "화공",
        "군량",
        "후속군",
        "뒷문",
        "뒷길",
        "샛길",
    ):
        if forbidden in joined:
            raise RuntimeError(f"segment 898 forbidden terminology retained: {forbidden}")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_record_map=PK_RECORD_MAP,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 898 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S898",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "recruitment_result_canonical_reused": True,
                "arson_proposal_records": 9,
                "historical_terminology_guarded": True,
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
