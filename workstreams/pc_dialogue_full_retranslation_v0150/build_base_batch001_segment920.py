#!/usr/bin/env python3
"""Build Base authoring segment 920 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment919 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S920.private.v1.jsonl"
)
SEGMENT = 920
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1628:0": "본거지야말로 가문의 요체",
    "15:1628:1": "\n이곳에는 새로이",
    "15:1628:2": "대관",
    "15:1628:3": (
        "을(를) 임명해\n"
        "빈 군의 발전을 맡겨 보는 것은 어떻겠습니까?"
    ),
    "15:1629:0": "본거지의 군을",
    "15:1629:1": "대관",
    "15:1629:2": (
        "에게 다스리게 해 보시는 것은 어떻겠소?\n"
        "임명된 자에게도\n"
        "공을 세울 좋은 기회를 제공"
    ),
    "15:1630:0": "대관",
    "15:1630:1": "이 없는 군이 있다고 들",
    "15:1630:2": (
        "\n여력이 있는 자에게 통치를 맡겨\n"
        "우리 본거지의 발전으로 이어가"
    ),
    "15:1631:0": (
        "슬슬 미처 살피지 못하는 성도\n"
        "생길 때가 된 듯하옵니다"
    ),
    "15:1631:1": "\n새로이",
    "15:1631:2": "군단",
    "15:1631:3": "을(를) 편성해 보시는 것은 어떻겠습니까?",
    "15:1632:0": "많은 성을 아우르려면\n",
    "15:1632:1": "군단",
    "15:1632:2": "이(가) 반드시 필요하오니\n신설을",
    "15:1632:3": "검토해 주시옵소서…",
    "15:1633:0": "많은 성이 휘하에 들어온 지금\n",
    "15:1633:1": "군단",
    "15:1633:2": "을(를) 새로 편성하여\n통치에 보탬으로 삼",
    "15:1634:0": (
        "강국과 맞서려면 영내를 풍요롭게 해야 하오\n"
        "금전에 여유가 있다면\n"
        "성하에 시설을 건설해 보는 것은 어떻겠소?"
    ),
}
RECORD_ARITIES = {
    1628: 4,
    1629: 3,
    1630: 3,
    1631: 4,
    1632: 4,
    1633: 3,
    1634: 1,
}
EXPECTED_BASE_JP = {
    1628: (
        "本拠こそ家の要",
        "\nここは新たに",
        "代官",
        "を任じ\n空いた郡の発展を任せてみては？",
    ),
    1629: (
        "本拠の郡を",
        "代官",
        "に治めさせては？\n任じられた者にとっても\n"
        "功を立てる良い機会とな",
    ),
    1630: (
        "代官",
        "がおらぬ郡があると伺",
        "\nここは手すきの者に統治を任せ\n我らが本拠の発展に繋げ",
    ),
    1631: (
        "そろそろ目の届かぬ城も\n出てくる頃合かと",
        "\n新たに",
        "軍団",
        "を編制しては",
    ),
    1632: (
        "多くの城を束ねるには\n",
        "軍団",
        "が必要不可欠\n新設の",
        "検討を…",
    ),
    1633: (
        "多くの城が麾下となった今\n",
        "軍団",
        "を新たに編制し\n統治の助けとし",
    ),
    1634: (
        "強国と戦うには領内を豊かにせねば\n"
        "もし金銭に余裕があるならば\n"
        "城下に施設を建設してみては？",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1628: (
        "",
        "014326020000",
        "1B434D",
        "1B435A",
        "050505",
    ),
    1629: (
        "",
        "1B434D",
        "1B435A",
        "01435A040000050505",
    ),
    1630: (
        "1B434D",
        "1B435A",
        "01436E020000",
        "01431E040000050505",
    ),
    1631: (
        "",
        "0143E2000000",
        "1B434D",
        "1B435A",
        "050505",
    ),
    1632: (
        "",
        "1B434D",
        "1B435A",
        "01438A040000",
        "050505",
    ),
    1633: (
        "",
        "1B434D",
        "1B435A",
        "01431E040000050505",
    ),
    1634: ("", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1628: (
        "",
        "014332020000",
        "1B434D",
        "1B435A",
        "050505",
    ),
    1629: (
        "",
        "1B434D",
        "1B435A",
        "014366040000050505",
    ),
    1630: (
        "1B434D",
        "1B435A",
        "01437A020000",
        "01432A040000050505",
    ),
    1632: (
        "",
        "1B434D",
        "1B435A",
        "014396040000",
        "050505",
    ),
    1633: (
        "",
        "1B434D",
        "1B435A",
        "01432A040000050505",
    ),
}
PK_RECORD_MAP = {
    1628: 1658,
    1629: 1659,
    1630: 1660,
    1631: 1661,
    1632: 1662,
    1633: 1663,
    1634: 1664,
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1632:3"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_RECORD_IDS = {1634}
MORPHOLOGY_COMMAND_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
MORPHOLOGY_JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    226: (
        "생각한다",
        "생각합니다",
        "생각하오",
        "생각하옵니다",
        "생각하옵나이다",
    ),
    550: ("다", "입니다", "이옵니다", "이오"),
    622: ("있었습니다", "었다"),
    1054: ("듯", "합시다"),
    1114: ("하리라", "합시다"),
    1162: ("", "고"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    562: EXPECTED_BASE_MORPHOLOGY_TERMINALS[550],
    634: EXPECTED_BASE_MORPHOLOGY_TERMINALS[622],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def make_auxiliary_overrides(
    shared: dict[
        tuple[str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    pk_en: dict[int, tuple[tuple[str, ...], tuple[str, ...]]],
) -> dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
]:
    return {
        **{
            (side, language, record_id): expected
            for (language, record_id), expected in shared.items()
            for side in ("base", "pk")
        },
        **{
            ("pk", "EN", record_id): expected
            for record_id, expected in pk_en.items()
        },
    }


def morphology_operands(gap_hex: str) -> tuple[int, ...]:
    return tuple(
        struct.unpack("<I", match.group(1))[0]
        for match in MORPHOLOGY_COMMAND_RE.finditer(bytes.fromhex(gap_hex))
    )


def morphology_terminal_literals(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    pending = [root]
    seen: set[int] = set()
    terminals: list[str] = []
    while pending:
        record_id = pending.pop(0)
        if record_id in seen:
            continue
        seen.add(record_id)
        record = records[(0, record_id)]
        for literal in ENGINE.parse_record_literals(record):
            if literal.text not in terminals:
                terminals.append(literal.text)
        pending.extend(
            struct.unpack("<I", match.group(1))[0]
            for match in MORPHOLOGY_JUMP_RE.finditer(record.data)
        )
    if not terminals:
        raise RuntimeError(f"morphology graph has no terminal literal: {root}")
    return tuple(terminals)


def annotate_morphology_evidence(
    prepared: Any,
    rows: list[dict[str, object]],
    *,
    record_arities: dict[int, int],
    pk_record_map: dict[int, int],
    base_gaps: dict[int, tuple[str, ...]],
    pk_gaps: dict[int, tuple[str, ...]],
    expected_base: dict[int, tuple[str, ...]],
    expected_pk: dict[int, tuple[str, ...]],
) -> None:
    base_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    pk_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    observed_base_operands = {
        operand
        for record_id, arity in record_arities.items()
        for gap_hex in base_gaps[record_id][: arity + 1]
        for operand in morphology_operands(gap_hex)
    }
    observed_pk_operands = {
        operand
        for record_id, arity in record_arities.items()
        for gap_hex in pk_gaps[record_id][: arity + 1]
        for operand in morphology_operands(gap_hex)
    }
    if observed_base_operands != set(expected_base):
        raise RuntimeError("Base morphology operand universe drifted")
    if observed_pk_operands != set(expected_pk):
        raise RuntimeError("PK morphology operand universe drifted")
    for records, expected, side in (
        (base_records, expected_base, "Base"),
        (pk_records, expected_pk, "PK"),
    ):
        for operand, terminals in expected.items():
            actual = morphology_terminal_literals(records, operand)
            if set(actual) != set(terminals) or len(actual) != len(terminals):
                raise RuntimeError(
                    f"{side} morphology terminal corpus drifted: {operand}"
                )

    rows_by_coordinate = {str(row["coordinate"]): row for row in rows}
    for record_id, arity in record_arities.items():
        for literal_id in range(arity):
            base_operands = morphology_operands(
                base_gaps[record_id][literal_id + 1]
            )
            pk_operands = morphology_operands(
                pk_gaps[record_id][literal_id + 1]
            )
            if not base_operands and not pk_operands:
                continue
            rows_by_coordinate[f"15:{record_id}:{literal_id}"][
                "runtime_morphology_samples"
            ] = {
                "base": [
                    {
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(expected_base[operand]),
                    }
                    for operand in base_operands
                ],
                "pk": [
                    {
                        "mapped_record_id": pk_record_map[record_id],
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(expected_pk[operand]),
                    }
                    for operand in pk_operands
                ],
            }


SHARED_AUXILIARY = {
    ("SC", 1628): (
        ("根据地正是家中要地，\n请任命新的", "代官", "。"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("TC", 1628): (
        ("根據地乃家中之要，\n不妨任命新", "代官", "。"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("SC", 1629): (
        (
            "视察自己周围的郡也很重要，\n"
            "但是比起下达指令，让他们自己选 ",
            "代官",
            "\n也是种办法。",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("TC", 1629): (
        ("親自治理旗下的郡為方法之一，\n從麾下任命", "代官", "亦為一手。"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("SC", 1630): (
        ("各位都渴望获得功勋，\n如果可以，请考虑任命", "代官", "。"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("TC", 1630): (
        ("眾人皆極欲立功，\n不妨考慮任命", "代官", "吧。"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("SC", 1631): (
        (
            "差不多也该到了\n目不能及的城出现之时了，\n"
            "请重新编制",
            "军团",
            "。",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("TC", 1631): (
        ("目前保有的城已快無法通盤照料，\n不妨編制新", "軍團", "。"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("SC", 1632): (
        ("想要统领众多的城，\n必须有", "军团", "，\n请考虑一下新组建一支……"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("TC", 1632): (
        ("要掌管眾多的城，就必須要有", "軍團", "，\n請大人考量新設……"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("SC", 1633): (
        ("目前已有众多的城位于麾下，\n重新编制", "军团", "，\n将会对统治大有帮助。"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("TC", 1633): (
        ("如今麾下城池眾多，\n編制新", "軍團", "協助統治吧！"),
        ("", "1B434D", "1B435A", "050505"),
    ),
    ("SC", 1634): (
        (
            "欲与强国开战，必先富足领内。\n"
            "若金钱宽裕，\n"
            "便于城下兴建设施如何？",
        ),
        ("", "050505"),
    ),
    ("TC", 1634): (
        (
            "若欲與強國戰鬥，則需豐足領內。\n"
            "若有金錢上的餘裕，\n"
            "則於城下興建設施，如何？",
        ),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1628: (
        (
            "A main base is of vital importance to the clan. Why not appoint a ",
            "substitute",
            " and have them develop the county?",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    1629: (
        (
            "Why not have a ",
            "substitute",
            " rule over the main baseÖs county? ItÖll be a great way for "
            "the person in charge to acquire honor.",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    1630: (
        (
            "It appears you have a county without a ",
            "substitute",
            ". Why not leave it to someone not otherwise occupied? We could "
            "further develop our home base.",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    1631: (
        (
            "I think itÖs time to pay attention to some of the castles weÖve "
            "neglected so far. ItÖs a good opportunity to organize a new ",
            "province",
            ".",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    1632: (
        (
            "When managing numerous castles at once, a ",
            "province",
            " is absolutely invaluable. Consider organizing a new one.",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    1633: (
        (
            "Now that you control many castles, organizing a new ",
            "province",
            " would help with their administration.",
        ),
        ("", "1B434D", "1B435A", "050505"),
    ),
    1634: (
        (
            "To fight powerful countries, we must make our territory prosper. "
            "If youÖve got the money, why not add some facilities to the "
            "castle town?",
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
    "main_base_magistrate_corps_organization_and_castle_town_facility_"
    "construction_with_explicit_base1628_1634_to_pk1658_1664_mapping_"
    "exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_pk_opcode_"
    "divergences_recorded_project_bongeoji_daegwan_gundan_terms_dynamic_"
    "label_tokens_live_inflection_stems_current_ko_morphology_terminal_"
    "corpus_recorded_current_layout_and_skeleton_preserved_static_and_"
    "runtime_split"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 920 direct Base/PK map drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 920 unexpected Base/PK JP literal divergence")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {1628, 1629, 1630, 1632, 1633}:
        raise RuntimeError("segment 920 Base/PK opcode divergence set drifted")
    joined = "\n".join(translations.values())
    for required in (
        "본거지",
        "대관",
        "군단",
        "편성",
        "성하",
        "시설",
        "건설",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 920 required terminology drifted: {required}")
    for forbidden in ("본거·", "대리", "편제", "당가", "주가"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 920 forbidden terminology retained: {forbidden}"
            )
    for coordinate, ending in {
        "15:1629:2": "제공",
        "15:1630:1": "들",
        "15:1630:2": "이어가",
        "15:1633:2": "삼",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 920 live inflection stem drifted: {coordinate}"
            )
    if {
        raw_translations["15:1629:2"] + suffix
        for suffix in EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114]
    } != {
        "에게 다스리게 해 보시는 것은 어떻겠소?\n"
        "임명된 자에게도\n"
        "공을 세울 좋은 기회를 제공하리라",
        "에게 다스리게 해 보시는 것은 어떻겠소?\n"
        "임명된 자에게도\n"
        "공을 세울 좋은 기회를 제공합시다",
    }:
        raise RuntimeError("segment 920 record 1629 composed suffix corpus drifted")
    if {
        raw_translations["15:1630:1"] + suffix
        for suffix in EXPECTED_BASE_MORPHOLOGY_TERMINALS[622]
    } != {
        "이 없는 군이 있다고 들있었습니다",
        "이 없는 군이 있다고 들었다",
    }:
        raise RuntimeError("segment 920 record 1630 composed suffix corpus drifted")
    if (
        raw_translations["15:1632:3"].count("…") != 1
        or translations["15:1632:3"].count("…") != 2
    ):
        raise RuntimeError("segment 920 ellipsis seed/pair drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 920 fixed visible decision count drifted")


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
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    annotate_morphology_evidence(
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
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 920 validated count drifted")
    if sum(
        row["scope_classification"] == "retranslated"
        and row["runtime_review"] == "not_required"
        for row in rows
    ) != 1:
        raise RuntimeError("segment 920 static classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S920",
                "decision_count": len(rows),
                "retranslated": 1,
                "runtime_fragment_pending": len(rows) - 1,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1628,
                    1629,
                    1630,
                    1632,
                    1633,
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
