#!/usr/bin/env python3
"""Build Base authoring segment 935 decisions for the v0.15.0 retranslation."""

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

import build_base_batch001_segment908 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S935.private.v1.jsonl"
)
SEGMENT = 935
MONEY_TRANSLATION = ("우리 가문의\n금전 사정", "만…")
ASSET_TRANSLATION = ("우리 가문의\n자산 현황", "만…")
TRANSLATIONS_BY_RECORD = {
    1787: ("우리를 도와주는\n든든한 국인중에 관해 설명",),
    1788: MONEY_TRANSLATION,
    1789: MONEY_TRANSLATION,
    1790: ASSET_TRANSLATION,
    1791: ASSET_TRANSLATION,
    1792: ("외교 중개자를 두어\n앞으로의 전황을 유리하게 이끄는 것은\n",),
    1793: ("공략 목표를 정하고\n각 성에서 군비를 갖추는 것은\n",),
    1794: ("군의에서 출진을 명하시는 것은",),
    1795: ("성하 시설을 건설하는 것은",),
    1796: ("정책을 발령하는 것은",),
    1797: ("성하 시설을 증축하는 것은",),
    1798: ("현재로서는,", "보고할 사항은"),
    1799: (
        "와(과)의 우호야말로\n"
        "우리 가문의 명운을 좌우하는 중대사\n"
        "중개자를 두어 신용을 제고",
    ),
    1800: (
        "현재 관계는 결코 좋다고 할 수",
        "만\n시간을 들이면 반드시\n관계가 회복될 날이 올 것",
    ),
    1801: (
        "현재 관계는 좋지도 나쁘지도",
        "\n관계를 개선하기에 좋은 기회라고",
    ),
    1802: (
        "현재 관계는 이미 좋은 상태",
        "\n성과를 거둘 날도 머지않은 것",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1787: ("我らに助力してくれる\n頼もしい国衆について説明",),
    1788: ("当家の\n金銭について", "が…"),
    1789: ("当家の\n金銭について", "が…"),
    1790: ("当家の\n資産について", "が…"),
    1791: ("当家の\n資産について", "が…"),
    1792: ("外交の取次を置き\n今後の戦局を優位に運ぶのは\n",),
    1793: ("攻略目標を定め\n各城にて軍備を進めては\n",),
    1794: ("軍議で出陣のご命令を出しては",),
    1795: ("城下施設を建設しては",),
    1796: ("政策を発令しては",),
    1797: ("城下施設を増築しては",),
    1798: ("目下のところ、", "報告は"),
    1799: ("との友誼こそ\n当家の命運を左右する一大事\n取次を置き、信用を高め",),
    1800: (
        "現状、関係は決して良く",
        "が\n時間をかければ必ずや\n雪解けの日は訪れること",
    ),
    1801: ("現状の関係は良くも悪くも", "\n改善を進めるには良き機かと"),
    1802: ("現状、関係は既に良好", "\n成果を得る日はそう遠くない"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1787: ("0143624A0200", "0143CC010000050505"),
    1788: ("0143624A0200", "014326020000", "050505"),
    1789: ("0143624A0200", "014326020000", "050505"),
    1790: ("0143624A0200", "014326020000", "050505"),
    1791: ("0143624A0200", "014326020000", "050505"),
    1792: ("0143624A0200", "0143B0020000014356020000050505"),
    1793: ("0143624A0200", "0143B0020000014356020000050505"),
    1794: ("0143624A0200", "0143B0020000014356020000050505"),
    1795: ("0143624A0200", "0143B0020000014356020000050505"),
    1796: ("0143624A0200", "0143B0020000014356020000050505"),
    1797: ("0143624A0200", "0143B0020000014356020000050505"),
    1798: ("", "01438A040000", "0143DA020000050505"),
    1799: ("025032", "01431E040000050505"),
    1800: ("", "0143DA020000", "014356020000050505"),
    1801: ("", "0143DA020000", "0143E2000000050505"),
    1802: ("", "01431A020000", "014356020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1787: ("0143624A0200", "0143D2010000050505"),
    1788: ("0143624A0200", "014332020000", "050505"),
    1789: ("0143624A0200", "014332020000", "050505"),
    1790: ("0143624A0200", "014332020000", "050505"),
    1791: ("0143624A0200", "014332020000", "050505"),
    1792: ("0143624A0200", "0143BC020000014362020000050505"),
    1793: ("0143624A0200", "0143BC020000014362020000050505"),
    1794: ("0143624A0200", "0143BC020000014362020000050505"),
    1795: ("0143624A0200", "0143BC020000014362020000050505"),
    1796: ("0143624A0200", "0143BC020000014362020000050505"),
    1797: ("0143624A0200", "0143BC020000014362020000050505"),
    1798: ("", "014396040000", "0143E6020000050505"),
    1799: ("025032", "01432A040000050505"),
    1800: ("", "0143E6020000", "014362020000050505"),
    1801: ("", "0143E6020000", "0143E2000000050505"),
    1802: ("", "014326020000", "014362020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1788:1",
    "15:1789:1",
    "15:1790:1",
    "15:1791:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}


def make_auxiliary_overrides(
    shared: dict[tuple[str, int], tuple[tuple[str, ...], tuple[str, ...]]],
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


SHARED_AUXILIARY = {
    ("SC", 1787): (("我来介绍一下会帮助我们的\n可靠国众。",), ("0143624A0200", "050505")),
    ("SC", 1788): (("关于本家的\n金钱……",), ("0143624A0200", "050505")),
    ("SC", 1789): (("关于本家的\n金钱……",), ("0143624A0200", "050505")),
    ("SC", 1790): (("关于本家的\n资产……",), ("0143624A0200", "050505")),
    ("SC", 1791): (("关于本家的\n资产……",), ("0143624A0200", "050505")),
    ("SC", 1792): (("设置外交代理，\n使今后的战局居于上风，\n如何？",), ("0143624A0200", "050505")),
    ("SC", 1793): (("制定攻略目标，\n于各城进行军备\n如何？",), ("0143624A0200", "050505")),
    ("SC", 1794): (("召开军事评议并下达命令，如何？",), ("0143624A0200", "050505")),
    ("SC", 1795): (("建设城下设施，如何？",), ("0143624A0200", "050505")),
    ("SC", 1796): (("颁布政策，如何？",), ("0143624A0200", "050505")),
    ("SC", 1797): (("增建城下设施，如何？",), ("0143624A0200", "050505")),
    ("SC", 1798): (("当下无任何报告。",), ("", "050505")),
    ("SC", 1799): (
        ("与", "的友谊才是\n左右本家命运的头等大事。\n设置代理，以提高信誉吧。"),
        ("", "025032", "050505"),
    ),
    ("SC", 1800): (
        ("目前的情况，双方关系交恶，\n不过经过时间的洗礼，\n化干戈为玉帛之日终会到来的吧。",),
        ("", "050505"),
    ),
    ("SC", 1801): (("虽然目前双方关系不好不坏，\n但确实是进行改善的良机。",), ("", "050505")),
    ("SC", 1802): (("目前双方关系良好。\n取得成果之日想必不远了。",), ("", "050505")),
    ("TC", 1787): (("協助我方的可靠國眾相關說明。",), ("0143624A0200", "050505")),
    ("TC", 1788): (("關於本家的資金……",), ("0143624A0200", "050505")),
    ("TC", 1789): (("關於本家的資金……",), ("0143624A0200", "050505")),
    ("TC", 1790): (("關於本家的資產……",), ("0143624A0200", "050505")),
    ("TC", 1791): (("關於本家的資產……",), ("0143624A0200", "050505")),
    ("TC", 1792): (("設置外交聯繫者，\n使今後的戰局居於上風，\n如何？",), ("0143624A0200", "050505")),
    ("TC", 1793): (("制定攻略目標，\n於各城進行軍備\n如何？",), ("0143624A0200", "050505")),
    ("TC", 1794): (("召開軍事評議並下達命令，如何？",), ("0143624A0200", "050505")),
    ("TC", 1795): (("建設城下設施，如何？",), ("0143624A0200", "050505")),
    ("TC", 1796): (("頒布政策，如何？",), ("0143624A0200", "050505")),
    ("TC", 1797): (("增建城下設施，如何？",), ("0143624A0200", "050505")),
    ("TC", 1798): (("當下無任何報告。",), ("", "050505")),
    ("TC", 1799): (
        ("與", "的友誼\n乃影響命本家命運的大事。\n不如設置聯繫者來提升信賴吧。"),
        ("", "025032", "050505"),
    ),
    ("TC", 1800): (("目前的關係雖不甚理想。\n若能假以時日，\n他日必能前嫌盡釋。",), ("", "050505")),
    ("TC", 1801): (("目前的關係不好不壞。\n應是進行改善的好時機。",), ("", "050505")),
    ("TC", 1802): (("目前關係良好。\n不久後應可獲得回報。",), ("", "050505")),
}
PK_EN_AUXILIARY = {
    1798: (("There is nothing to report at the moment.",), ("", "050505")),
    1799: (
        ("Our friendship with the ", " is crucial to our clanÖs destiny. We should send an emissary to build trust."),
        ("", "025032", "050505"),
    ),
    1800: (
        ("Our relations are not good at present, but IÖm sure that things will smooth over in time.",),
        ("", "050505"),
    ),
    1801: (
        ("Our current connection is neither good nor bad. This could be the perfect opportunity to improve it.",),
        ("", "050505"),
    ),
    1802: (
        ("Our connection is already quite good. It wonÖt be long before we see results.",),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B112_C_pristine_base_pc_jp_authoritative_"
    "kokujin_money_assets_diplomatic_intermediary_war_situation_war_"
    "council_castle_town_facility_policy_reports_friendship_trust_and_"
    "relationship_assessment_with_explicit_base1787_1802_to_pk1817_1832_"
    "mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_"
    "project_kukinjung_junggaeja_uri_gamun_seongha_facility_gongnyak_"
    "mokpyo_jeonhwang_gunui_terms_025032_force_token_current_korean_"
    "morphology_terminal_corpora_and_cross_resource_opcode_divergences_"
    "recorded_exact_money_and_asset_tuple_reuse_project_ellipsis_pair_"
    "current_line_counts_and_protected_skeleton_preserved_runtime_pending"
)

MORPHOLOGY_COMMAND_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
MORPHOLOGY_JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    226: ("생각합니다", "생각한다", "생각하오", "생각하옵니다", "생각하옵나이다"),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    550: ("입니다", "다", "이오", "이옵니다"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    1054: ("합시다", "듯"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    562: EXPECTED_BASE_MORPHOLOGY_TERMINALS[550],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    742: EXPECTED_BASE_MORPHOLOGY_TERMINALS[730],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
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
        if record_id in seen or (0, record_id) not in records:
            continue
        seen.add(record_id)
        record = records[(0, record_id)]
        for literal in ENGINE.parse_record_literals(record):
            if literal.text not in terminals:
                terminals.append(literal.text)
        pending.extend(
            target
            for match in MORPHOLOGY_JUMP_RE.finditer(record.data)
            if (target := struct.unpack("<I", match.group(1))[0])
            and (0, target) in records
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
    skip_records: set[int] | None = None,
) -> None:
    skipped = skip_records or set()
    base_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    pk_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    observed_base = {
        operand
        for record_id, arity in record_arities.items()
        if record_id not in skipped
        for gap_hex in base_gaps[record_id][: arity + 1]
        for operand in morphology_operands(gap_hex)
        if operand in expected_base
    }
    observed_pk = {
        operand
        for record_id, arity in record_arities.items()
        if record_id not in skipped
        for gap_hex in pk_gaps[record_id][: arity + 1]
        for operand in morphology_operands(gap_hex)
        if operand in expected_pk
    }
    if observed_base != set(expected_base) or observed_pk != set(expected_pk):
        raise RuntimeError("morphology operand universe drifted")
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
        if record_id in skipped:
            continue
        for literal_id in range(arity):
            base_operands = tuple(
                operand
                for operand in morphology_operands(
                    base_gaps[record_id][literal_id + 1]
                )
                if operand in expected_base
            )
            pk_operands = tuple(
                operand
                for operand in morphology_operands(
                    pk_gaps[record_id][literal_id + 1]
                )
                if operand in expected_pk
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


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if TRANSLATIONS_BY_RECORD[1788] is not MONEY_TRANSLATION:
        raise RuntimeError("segment 935 money canonical tuple split: 1788")
    if TRANSLATIONS_BY_RECORD[1789] is not MONEY_TRANSLATION:
        raise RuntimeError("segment 935 money canonical tuple split: 1789")
    if TRANSLATIONS_BY_RECORD[1790] is not ASSET_TRANSLATION:
        raise RuntimeError("segment 935 asset canonical tuple split: 1790")
    if TRANSLATIONS_BY_RECORD[1791] is not ASSET_TRANSLATION:
        raise RuntimeError("segment 935 asset canonical tuple split: 1791")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 935 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != set(RECORD_ARITIES):
        raise RuntimeError("segment 935 Base-to-PK gap divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "국인중",
        "우리 가문",
        "중개자",
        "전황",
        "공략 목표",
        "군의",
        "성하 시설",
        "우호",
        "신용",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 935 required terminology drifted: {required}")
    for forbidden in ("호족", "당가", "주선", "전국", "중개역"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 935 forbidden terminology retained: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 935 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(raw_translations) != 24 or len(translations) != 24:
        raise RuntimeError("segment 935 visible decision count drifted")


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
    annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
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
    if len(rows) != 24 or len(validated) != len(translations):
        raise RuntimeError("segment 935 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 935 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S935",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "canonical_money_record_ids": [1788, 1789],
                "canonical_asset_record_ids": [1790, 1791],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": sorted(RECORD_ARITIES),
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
