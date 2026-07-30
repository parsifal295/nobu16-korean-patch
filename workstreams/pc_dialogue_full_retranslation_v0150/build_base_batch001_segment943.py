#!/usr/bin/env python3
"""Build Base authoring segment 943 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment942 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S943.private.v1.jsonl"
)
SEGMENT = 943
MONEY_REQUIREMENT_TRANSLATION = (
    "무엇을 이루든 먼저 금전이 필수",
    "\n",
    "에서 수입을 늘려 보는 것은\n",
)
DEFENSIVE_EXPANSION_TRANSLATION = (
    "수비를 굳혀 두면 만일의 사태에도 안심",
    "\n",
    "의 증축도 한 방법",
)
TRANSLATIONS_BY_RECORD = {
    1879: (
        "우리 가문의 새 정책으로\n",
        "을(를) 발령해야 한다고",
    ),
    1880: (
        "정책·",
        "을(를) 개선해\n더 큰 혜택을 얻는 것은 어떻겠습니까?",
    ),
    1881: (
        "매달 유지비가 늘어난다고",
        "하지만\n그에 걸맞은 대가는 얻을 수 있을",
    ),
    1882: (
        "의 성하에 세워진\n",
        "의 증축을 권고",
    ),
    1883: (
        "증축을 거듭하면\n",
        "의 성하는 더욱 번성할 수",
    ),
    1884: PREVIOUS.SUPPLY_TRANSLATION,
    1885: MONEY_REQUIREMENT_TRANSLATION,
    1886: MONEY_REQUIREMENT_TRANSLATION,
    1887: PREVIOUS.CROP_TRANSLATION,
    1888: (
        PREVIOUS.TRANSLATIONS_BY_RECORD[1873][0],
        "\n",
        "에서 병력을 늘려 보는 것은\n",
    ),
    1889: (
        "의 증축 준비가 끝나 있",
        "\n포술 훈련을 실시해\n병사를 강화",
    ),
    1890: (
        "의 증축 준비가 끝나 있",
        "\n기마술 훈련을 실시해\n병사를 강화",
    ),
    1891: PREVIOUS.SUPPLY_LIMIT_TRANSLATION,
    1892: DEFENSIVE_EXPANSION_TRANSLATION,
    1893: DEFENSIVE_EXPANSION_TRANSLATION,
    1894: (
        "우리 가문의 금전 수입이 넉넉하다고 말하기는 곤란",
        "\n취락을 장악하거나 성하 시설을 세워\n"
        "수익을 개선해야 한다고",
    ),
    1895: (
        "다행히 우리 가문의 금전 수입은 넉넉합니다…\n"
        "정책 발령과 성하 시설 건설 등에 유용하게 써서\n"
        "다른 가문보다 앞서 나가는 것이 상책입니다",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1885:1": "\n",
    "15:1886:1": "\n",
    "15:1888:1": "\n",
    "15:1892:1": "\n",
    "15:1893:1": "\n",
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1879: ("当家の新たな政策として\n", "を発令すべきかと"),
    1880: ("政策・", "を改善し\nさらなる恩恵を得ては？"),
    1881: ("毎月の維持費はかさ", "が\nそれに見合う対価は得られ"),
    1882: ("の城下に建つ\n", "の増築を勧め"),
    1883: ("増築を積み重ねることで\n", "の城下はさらに賑わ"),
    1884: ("で兵糧を確保すれば\n戦が長引いても\n兵力を保て",),
    1885: (
        "なにを成すにもまずは金銭が必要",
        "\n",
        "で収入を増やしては\n",
    ),
    1886: (
        "なにを成すにもまずは金銭が必要",
        "\n",
        "で収入を増やしては\n",
    ),
    1887: ("で石高を増強すれば\n戦が長引いても\n兵力を保て",),
    1888: (
        "攻めるも守るも兵力次第",
        "\n",
        "で兵力を増強しては\n",
    ),
    1889: (
        "増築の準備は整ってい",
        "\n砲術の訓練を行い\n兵を強化し",
    ),
    1890: (
        "増築の準備は整ってい",
        "\n馬術の訓練を行い\n兵を強化し",
    ),
    1891: ("で兵糧上限を増やしておけば\n連戦にも備えられ",),
    1892: ("守りを固めておけばいざというときも安心", "\n", "の増築はいかが"),
    1893: ("守りを固めておけばいざというときも安心", "\n", "の増築はいかが"),
    1894: (
        "当家の金銭収入は潤沢とは言いかね",
        "\n集落の掌握や城下施設などにより\n"
        "収益を改善していくべきかと",
    ),
    1895: (
        "幸い、当家の金銭収入は潤沢…\n"
        "政策の発令や、城下町建設など\n"
        "有効に使い、他家を出し抜くが上策かと",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1879: ("", "1B4349023C1B435A", "0143E2000000050505"),
    1880: ("", "1B4349023C1B435A", "050505"),
    1881: ("", "0143A0030000", "01431E040000050505"),
    1882: ("026432", "1B4349023C1B435A", "01433C040000050505"),
    1883: ("", "026432", "0143CA000000050505"),
    1884: ("023C", "01431E040000050505"),
    1885: (
        "",
        "01432C020000",
        "023C",
        "0143B0020000014356020000050505",
    ),
    1886: (
        "",
        "01432C020000",
        "023C",
        "0143B0020000014356020000050505",
    ),
    1887: ("023C", "01431E040000050505"),
    1888: (
        "",
        "01432C020000",
        "023C",
        "0143B0020000014356020000050505",
    ),
    1889: ("023C", "01433C040000", "01431E040000050505"),
    1890: ("023C", "01433C040000", "01431E040000050505"),
    1891: ("023C", "01431E040000050505"),
    1892: ("", "01432C020000", "023C", "014324010000050505"),
    1893: ("", "01432C020000", "023C", "014324010000050505"),
    1894: ("", "01433C040000", "0143E2000000050505"),
    1895: ("", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1879: ("", "1B4349023C1B435A", "0143E2000000050505"),
    1880: ("", "1B4349023C1B435A", "050505"),
    1881: ("", "0143AC030000", "01432A040000050505"),
    1882: ("026432", "1B4349023C1B435A", "014348040000050505"),
    1883: ("", "026432", "0143CA000000050505"),
    1884: ("023C", "01432A040000050505"),
    1885: (
        "",
        "014338020000",
        "023C",
        "0143BC020000014362020000050505",
    ),
    1886: (
        "",
        "014338020000",
        "023C",
        "0143BC020000014362020000050505",
    ),
    1887: ("023C", "01432A040000050505"),
    1888: (
        "",
        "014338020000",
        "023C",
        "0143BC020000014362020000050505",
    ),
    1889: ("023C", "014348040000", "01432A040000050505"),
    1890: ("023C", "014348040000", "01432A040000050505"),
    1891: ("023C", "01432A040000050505"),
    1892: ("", "014338020000", "023C", "014324010000050505"),
    1893: ("", "014338020000", "023C", "014324010000050505"),
    1894: ("", "014348040000", "0143E2000000050505"),
    1895: ("", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:1895:0"}
STATIC_RECORD_IDS = {1895}
EXPECTED_AUXILIARY_DIGESTS = {
    "base_SC": "85266FB10A4D594CC3AEC89C4F63A5EE094BFF14DCA68EFDDDA0A10299FD4B29",
    "base_TC": "81BDEB6E1C9FA168A2ABC3DF73CE0249AC816CFA18930EB298DBE62B03508D3A",
    "pk_SC": "85266FB10A4D594CC3AEC89C4F63A5EE094BFF14DCA68EFDDDA0A10299FD4B29",
    "pk_TC": "81BDEB6E1C9FA168A2ABC3DF73CE0249AC816CFA18930EB298DBE62B03508D3A",
    "pk_EN": "6B27906B9BFCEEF405D30C0AFD76DAFE8DA9F00F704748406133F747CC0C315F",
}
BASIS = (
    "review_queue_base_msggame_B113_B_pristine_base_pc_jp_authoritative_"
    "policy_issue_improvement_facility_expansion_money_income_supplies_"
    "yield_troops_gunnery_horsemanship_and_defense_evaluation_with_"
    "explicit_base1879_1895_to_pk1909_1925_mapping_exact_base_pk_jp_sc_"
    "tc_and_pk_en_context_guarded_by_combined_record_sha256_dynamic_"
    "policy_castle_facility_tokens_1b4349_023c_1b435a_026432_current_"
    "korean_morphology_terminal_corpora_and_base_pk_opcode_divergences_"
    "recorded_1885_1886_1888_1892_1893_hidden_lf_excluded_cross_segment_"
    "exact_1869_1884_1872_1887_1876_1891_reuse_and_local_1885_1886_"
    "1892_1893_reuse_kotobank_kokudaka_hojutsu_bajutsu_historical_basis_"
    "project_uri_gamun_policy_seongha_facility_chwirak_terms_current_line_"
    "counts_ellipsis_pair_and_runtime_skeleton_preserved"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    202: ("있겠지요", "오"),
    226: ("생각합니다", "생각한다", "생각하오", "생각하옵니다", "생각하옵나이다"),
    292: ("일까요", "일까", "입니까"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    928: ("봅니다", "음", "보옵니다"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    202: EXPECTED_BASE_MORPHOLOGY_TERMINALS[202],
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    292: EXPECTED_BASE_MORPHOLOGY_TERMINALS[292],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    940: EXPECTED_BASE_MORPHOLOGY_TERMINALS[928],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if TRANSLATIONS_BY_RECORD[1884] is not PREVIOUS.SUPPLY_TRANSLATION:
        raise RuntimeError("segment 943 Base1869/1884 supply reuse split")
    if TRANSLATIONS_BY_RECORD[1887] is not PREVIOUS.CROP_TRANSLATION:
        raise RuntimeError("segment 943 Base1872/1887 crop reuse split")
    if TRANSLATIONS_BY_RECORD[1891] is not PREVIOUS.SUPPLY_LIMIT_TRANSLATION:
        raise RuntimeError("segment 943 Base1876/1891 supply-limit reuse split")
    if TRANSLATIONS_BY_RECORD[1885] is not MONEY_REQUIREMENT_TRANSLATION:
        raise RuntimeError("segment 943 Base1885 money tuple split")
    if TRANSLATIONS_BY_RECORD[1886] is not MONEY_REQUIREMENT_TRANSLATION:
        raise RuntimeError("segment 943 Base1886 money tuple split")
    if TRANSLATIONS_BY_RECORD[1892] is not DEFENSIVE_EXPANSION_TRANSLATION:
        raise RuntimeError("segment 943 Base1892 defense tuple split")
    if TRANSLATIONS_BY_RECORD[1893] is not DEFENSIVE_EXPANSION_TRANSLATION:
        raise RuntimeError("segment 943 Base1893 defense tuple split")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 943 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {
        1881,
        1882,
        1884,
        1885,
        1886,
        1887,
        1888,
        1889,
        1890,
        1891,
        1892,
        1893,
        1894,
    }:
        raise RuntimeError("segment 943 Base-to-PK gap divergence drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        "15:1885:1": "\n",
        "15:1886:1": "\n",
        "15:1888:1": "\n",
        "15:1892:1": "\n",
        "15:1893:1": "\n",
    }:
        raise RuntimeError("segment 943 hidden LF exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "정책",
        "성하 시설",
        "취락",
        "석고",
        "병량",
        "포술",
        "기마술",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 943 required terminology drifted: {required}"
            )
    for forbidden in ("당가", "호족", "승마 훈련", "성하 마을"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 943 forbidden terminology retained: {forbidden}"
            )
    for record_id in (1889, 1890):
        if not TRANSLATIONS_BY_RECORD[record_id][0].endswith("준비가 끝나 있"):
            raise RuntimeError(
                f"segment 943 completed-preparation state drifted: {record_id}"
            )
    if re.search(r"(?<!기)마술", joined):
        raise RuntimeError("segment 943 standalone 마술 terminology retained")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 943 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 30:
        raise RuntimeError("segment 943 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    auxiliary_overrides = PREVIOUS.PREVIOUS.make_guarded_auxiliary_overrides(
        tuple(RECORD_ARITIES),
        PK_RECORD_MAP,
        EXPECTED_AUXILIARY_DIGESTS,
    )
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
        auxiliary_overrides=auxiliary_overrides,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    PREVIOUS.PREVIOUS.SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
        skip_records=STATIC_RECORD_IDS,
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
    if len(rows) != 30 or len(validated) != len(translations):
        raise RuntimeError("segment 943 validated count drifted")
    static_rows = [
        row
        for row in rows
        if row["scope_classification"] == "retranslated"
        and row["runtime_review"] == "not_required"
    ]
    if len(static_rows) != 1:
        raise RuntimeError("segment 943 static classification count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S943",
                "source_literal_count": 35,
                "decision_count": len(rows),
                "hidden_lf_excluded": len(EXCLUDED_NONVISIBLE_COORDINATES),
                "retranslated": len(static_rows),
                "runtime_fragment_pending": len(rows) - len(static_rows),
                "static_record_ids": sorted(STATIC_RECORD_IDS),
                "cross_segment_reuse_groups": [
                    [1869, 1884],
                    [1872, 1887],
                    [1876, 1891],
                ],
                "local_reuse_groups": [
                    [1885, 1886],
                    [1892, 1893],
                ],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": sorted(
                    record_id
                    for record_id in RECORD_ARITIES
                    if EXPECTED_BASE_GAPS[record_id]
                    != EXPECTED_PK_JP_GAPS[record_id]
                ),
                "historical_term_basis": {
                    "石高": "Kotobank land productivity and tax basis",
                    "砲術": "Kotobank firearm operation skill",
                    "馬術": "Kotobank military horsemanship skill",
                },
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
