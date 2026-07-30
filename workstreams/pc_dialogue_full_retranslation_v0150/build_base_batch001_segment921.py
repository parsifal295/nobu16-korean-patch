#!/usr/bin/env python3
"""Build Base authoring segment 921 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment920 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S921.private.v1.jsonl"
)
SEGMENT = 921
make_auxiliary_overrides = PREVIOUS.make_auxiliary_overrides
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1635:0": (
        "강적을 물리치려면 국력 증강이 중요하고\n"
        "여유 자금이 있다면\n"
        "성하 시설의 증축을 제안"
    ),
    "15:1636:0": '성하 시설 "',
    "15:1636:1": '"을(를) 건설해 보는 것은',
    "15:1637:0": '정책 "',
    "15:1637:1": (
        '"이야말로\n'
        "우리 가문에 없어서는 안 될 것…\n"
        "인력을 투입해야 할 듯하옵니다"
    ),
    "15:1638:0": '정책 "',
    "15:1638:1": '" 연구를 진척시켜\n우리 가문 발전의 초석으로 삼',
    "15:1639:0": '정책 "',
    "15:1639:1": '"을(를) 발령해 보는 것은',
    "15:1640:0": (
        "각 성의 통치에 지침을 세우면\n"
        "영내를 뜻대로 다스릴 수 있"
    ),
    "15:1640:1": '\n가신단에 "',
    "15:1640:2": '"을(를) 발령해 보는 것은 어떻겠습니까?',
    "15:1641:0": (
        "적재적소야말로 통치의 첫걸음\n"
        "영주의 배치를 바꾸기 위해\n"
        '"'
    ),
    "15:1641:1": '"을(를) 시행해 보시는 것은 어떻겠습니까?',
    "15:1642:0": '적에 대한 대비는 맹장에게 맡기고 싶은 법\n"',
    "15:1642:1": (
        '"을(를) 발령하여\n'
        "성주의 임지를 바꾸어 보시는 것은 어떻겠소?"
    ),
    "15:1643:0": (
        "우리 가문의 조두는 모두 걸물이지만\n"
        "공을 세울 기회를 얻지 못한 듯하니\n"
        '"'
    ),
    "15:1643:1": '"을(를) 발령해 보시는 것은 어떻겠습니까?',
    "15:1644:0": "우리 가문의 영내도 넓어졌",
    "15:1644:1": (
        "\n다른 가문과의 경계까지 살필 수 있도록\n"
        "본거지를 옮길 때인지도 모르"
    ),
}
RECORD_ARITIES = {
    1635: 1,
    1636: 2,
    1637: 2,
    1638: 2,
    1639: 2,
    1640: 3,
    1641: 2,
    1642: 2,
    1643: 2,
    1644: 2,
}
EXPECTED_BASE_JP = {
    1635: (
        "強敵に打ち勝つには国力増強が肝心\n"
        "もし余剰の金銭があるならば\n"
        "城下施設の増築を提案",
    ),
    1636: ("城下施設「", "」を建設しては"),
    1637: (
        "政策「",
        "」こそ\n当家には不可欠なもの…\n人手をかけるべきかと",
    ),
    1638: (
        "政策「",
        "」の研究を進め\n当家発展の礎とし",
    ),
    1639: ("政策「", "」を発令しては"),
    1640: (
        "各城の統治に指針を与えられれば\n領内を思い通りに治められ",
        "\n家中に「",
        "」を発令しては？",
    ),
    1641: (
        "適材適所こそが施政の第一歩\n領主の配置換えをするために\n「",
        "」してはいかがかと",
    ),
    1642: (
        "敵への備えは猛者に担わせたいもの\n「",
        "」を発令することで\n城主の任地替えをしてはいかが",
    ),
    1643: (
        "当家の組頭は傑物揃いなれど\n功を立てる機会に恵まれぬ様子\n「",
        "」を発令しては？",
    ),
    1644: (
        "当家の領国も広うな",
        "\n他家との境に目が届くよう\n本拠を移す頃合いやもし",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1635: ("", "01438E000000050505"),
    1636: (
        "",
        "023C",
        "0143B0020000014356020000050505",
    ),
    1637: ("", "023C", "050505"),
    1638: ("", "023C", "01431E040000050505"),
    1639: (
        "",
        "023C",
        "0143B0020000014356020000050505",
    ),
    1640: (
        "",
        "01431E040000",
        "023C",
        "050505",
    ),
    1641: ("", "023C", "050505"),
    1642: ("", "023C", "050505"),
    1643: ("", "023C", "050505"),
    1644: (
        "",
        "014368020000",
        "01434E040000050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1636: (
        "",
        "023C",
        "0143BC020000014362020000050505",
    ),
    1638: ("", "023C", "01432A040000050505"),
    1639: (
        "",
        "023C",
        "0143BC020000014362020000050505",
    ),
    1640: (
        "",
        "01432A040000",
        "023C",
        "050505",
    ),
    1644: (
        "",
        "014374020000",
        "01435A040000050505",
    ),
}
PK_RECORD_MAP = {
    1635: 1665,
    1636: 1666,
    1637: 1667,
    1638: 1668,
    1639: 1669,
    1640: 1670,
    1641: 1671,
    1642: 1672,
    1643: 1673,
    1644: 1674,
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1637:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    142: ("하다", "하겠습니다", "하겠사옵니다"),
    598: ("이리라", "이겠지요", "이겠지"),
    616: ("었다", "했습니다"),
    688: ("어떻게", "어떠하오"),
    1054: ("듯", "합시다"),
    1102: ("할 수 없", "할 수 없습니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1114: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1102],
}

SHARED_AUXILIARY = {
    ("SC", 1635): (
        (
            "若欲战胜强敌，则需增强国力。\n"
            "若金钱宽裕，\n"
            "建议增筑城下设施。",
        ),
        ("", "050505"),
    ),
    ("TC", 1635): (
        (
            "若欲戰勝強敵，則需增強國力。\n"
            "若有金錢上的餘裕，\n"
            "建議您增築城下設施。",
        ),
        ("", "050505"),
    ),
    ("SC", 1636): (
        ("建设城下设施「", "」的话如何？"),
        ("", "023C", "050505"),
    ),
    ("TC", 1636): (
        ("是否興建城下設施「", "」？"),
        ("", "023C", "050505"),
    ),
    ("SC", 1637): (
        (
            "政策「",
            "」对本家来说，\n正是不可欠缺之事……\n应该着手于此。",
        ),
        ("", "023C", "050505"),
    ),
    ("TC", 1637): (
        (
            "對本家而言，\n政策「",
            "」不可或缺……\n理應增加人手。",
        ),
        ("", "023C", "050505"),
    ),
    ("SC", 1638): (
        ("推进政策「", "」的研究，\n将其作为本家发展的基石吧。"),
        ("", "023C", "050505"),
    ),
    ("TC", 1638): (
        ("全力進行政策「", "」的研究，\n做為本家的根基。"),
        ("", "023C", "050505"),
    ),
    ("SC", 1639): (
        ("颁布政策「", "」，意下如何？"),
        ("", "023C", "050505"),
    ),
    ("TC", 1639): (
        ("下令執行政策「", "」如何？"),
        ("", "023C", "050505"),
    ),
    ("SC", 1640): (
        (
            "颁布政策「",
            "」，\n决定本家的攻略目标吧。\n家中全体都将为攻略而尽力。",
        ),
        ("", "023C", "050505"),
    ),
    ("TC", 1640): (
        (
            "頒布政策「",
            "」，\n決定本家的攻略目標吧。\n家中全體都將為攻略而盡力。",
        ),
        ("", "023C", "050505"),
    ),
    ("SC", 1641): (
        (
            "因本家的扩张，\n为了将远离前线的领主向前线移动，\n"
            "颁布政策「",
            "」如何？",
        ),
        ("", "023C", "050505"),
    ),
    ("TC", 1641): (
        (
            "因本家的擴張，\n為了將遠離前線的領主向前線移動，\n"
            "頒布政策「",
            "」如何？",
        ),
        ("", "023C", "050505"),
    ),
    ("SC", 1642): (
        (
            "应当由骁勇猛将来防卫敌人，\n不如颁布政策「",
            "」，\n将后方的城主移动至前线如何？",
        ),
        ("", "023C", "050505"),
    ),
    ("TC", 1642): (
        (
            "應當由驍勇猛將來防衛敵人，\n不如頒布政策「",
            "」，\n替換城主的任地吧。",
        ),
        ("", "023C", "050505"),
    ),
    ("SC", 1643): (
        (
            "本家多数的人才仍停留在组头，\n所以为了提升他们的功勋，\n"
            "颁布政策「",
            "」如何？",
        ),
        ("", "023C", "050505"),
    ),
    ("TC", 1643): (
        (
            "本家多數的人才仍停留在組頭，\n所以為了提升他們的功勛，\n"
            "頒布政策「",
            "」如何？",
        ),
        ("", "023C", "050505"),
    ),
    ("SC", 1644): (
        (
            "本家的领土也更加辽阔了，\n"
            "为了能监视与他家之间的边境，\n"
            "差不多是时候转移大本营了。",
        ),
        ("", "050505"),
    ),
    ("TC", 1644): (
        (
            "本家的領土也更加遼闊了，\n"
            "為了能監視與他家之間的邊境，\n"
            "差不多是時候轉移大本營了。 ",
        ),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1635: (
        (
            "To defeat a powerful enemy, we must increase our own power. "
            "If you can afford it, IÖd suggest constructing some castle town "
            "facilities.",
        ),
        ("", "050505"),
    ),
    1636: (
        ("How about building a ", " castle town facility?"),
        ("", "023C", "050505"),
    ),
    1637: (
        (
            "The ",
            " policy is absolutely indispensable to the clan. ItÖd be good "
            "to put some people on the job.",
        ),
        ("", "023C", "050505"),
    ),
    1638: (
        (
            "Continuing research on the ",
            " policy will be the key to our clanÖs improvement.",
        ),
        ("", "023C", "050505"),
    ),
    1639: (
        ("How about issuing the ", " policy?"),
        ("", "023C", "050505"),
    ),
    1640: (
        (
            "If we provide a principle to every castle we manage, the "
            "territory will be ruled as you see fit. Would you like to issue ",
            " throughout the clan?",
        ),
        ("", "023C", "050505"),
    ),
    1641: (
        (
            "Having the right person in the right place is vital for a good "
            "government. I suggest using ",
            " to reassign the land holders.",
        ),
        ("", "023C", "050505"),
    ),
    1642: (
        (
            "We need someone fearless to stand against the enemy. Shall we "
            "issue ",
            " to switch the land holders around?",
        ),
        ("", "023C", "050505"),
    ),
    1643: (
        (
            "Our clanÖs chiefs are all very powerful, but they havenÖt been "
            "given a chance to make their mark. How about issuing ",
            "?",
        ),
        ("", "023C", "050505"),
    ),
    1644: (
        (
            "Our clanÖs territory has grown larger. Perhaps itÖs time to move "
            "our main base so we can keep an eye on the border.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B111_A_pristine_base_pc_jp_authoritative_"
    "castle_town_facility_expansion_policy_research_and_issuance_lord_"
    "castle_lord_reassignment_and_main_base_relocation_with_explicit_"
    "base1635_1644_to_pk1665_1674_mapping_exact_base_pk_jp_sc_tc_and_"
    "actual_pk_en_auxiliary_context_pk_opcode_divergences_recorded_"
    "project_policy_household_lord_castle_lord_main_base_terms_dynamic_"
    "policy_tokens_live_inflection_stems_current_ko_morphology_terminal_"
    "corpus_recorded_ascii_quotes_current_layout_and_skeleton_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 921 direct Base/PK map drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 921 unexpected Base/PK JP literal divergence")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {1636, 1638, 1639, 1640, 1644}:
        raise RuntimeError("segment 921 Base/PK opcode divergence set drifted")
    joined = "\n".join(translations.values())
    for required in (
        "성하 시설",
        "증축",
        "건설",
        "정책",
        "우리 가문",
        "가신단",
        "영주",
        "성주",
        "조두",
        "본거지",
        "발령",
        "연구",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 921 required terminology drifted: {required}")
    for forbidden in (
        "당가",
        "가중",
        "본거·",
        "직책",
        "「",
        "」",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 921 forbidden terminology retained: {forbidden}"
            )
    for coordinate, ending in {
        "15:1635:0": "제안",
        "15:1636:1": "것은",
        "15:1638:1": "삼",
        "15:1639:1": "것은",
        "15:1640:0": "있",
        "15:1644:0": "넓어졌",
        "15:1644:1": "모르",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 921 live inflection stem drifted: {coordinate}"
            )
    if {
        raw_translations["15:1635:0"] + suffix
        for suffix in EXPECTED_BASE_MORPHOLOGY_TERMINALS[142]
    } != {
        "강적을 물리치려면 국력 증강이 중요하고\n"
        "여유 자금이 있다면\n"
        "성하 시설의 증축을 제안하다",
        "강적을 물리치려면 국력 증강이 중요하고\n"
        "여유 자금이 있다면\n"
        "성하 시설의 증축을 제안하겠습니다",
        "강적을 물리치려면 국력 증강이 중요하고\n"
        "여유 자금이 있다면\n"
        "성하 시설의 증축을 제안하겠사옵니다",
    }:
        raise RuntimeError("segment 921 record 1635 composed suffix corpus drifted")
    if (
        "영내" not in raw_translations["15:1644:0"]
        or "영지" in raw_translations["15:1644:0"]
    ):
        raise RuntimeError("segment 921 record 1644 領国 meaning drifted")
    if (
        raw_translations["15:1637:1"].count("…") != 1
        or translations["15:1637:1"].count("…") != 2
    ):
        raise RuntimeError("segment 921 ellipsis seed/pair drifted")
    if len(raw_translations) != 20 or len(translations) != 20:
        raise RuntimeError("segment 921 fixed visible decision count drifted")


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
    PREVIOUS.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
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
    if len(rows) != 20 or len(validated) != len(translations):
        raise RuntimeError("segment 921 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 921 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S921",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1636,
                    1638,
                    1639,
                    1640,
                    1644,
                ],
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
