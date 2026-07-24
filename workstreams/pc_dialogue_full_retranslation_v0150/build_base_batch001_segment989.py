#!/usr/bin/env python3
"""Build Base authoring segment 989 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment982 as PREVIOUS
import build_base_batch001_segment988 as CANONICAL_S988


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S989.private.v1.jsonl"
)
SEGMENT = 989
VALUE_TOKEN = "023C"
TARGET_FORCE_TOKEN = "025132"
CASTLE_TOKEN = "026432"
RESOURCE_TRADE_TRANSLATION: tuple[str | None, ...] = (
    "다행히 우리 가문은",
    "의 수입만큼은\n다른 가문보다 풍족한 상태",
    None,
    "은(는) 합전에서 유용할 뿐 아니라\n외교에서는 협상 카드로 활용할\n수도 있",
)
RESOURCE_POLICY_TRANSLATION = CANONICAL_S988.TRANSLATIONS_BY_RECORD[2365]
TRANSLATIONS_BY_RECORD: dict[int, tuple[str | None, ...]] = {
    2366: RESOURCE_TRADE_TRANSLATION,
    2367: RESOURCE_TRADE_TRANSLATION,
    2368: RESOURCE_POLICY_TRANSLATION,
    2369: RESOURCE_POLICY_TRANSLATION,
    2370: RESOURCE_TRADE_TRANSLATION,
    2371: RESOURCE_TRADE_TRANSLATION,
    2372: (
        "현재 목표인",
        "의",
        "을(를) 공략할\n시기에 관한 견해",
        "…",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if translation is not None
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
RESOURCE_TRADE_JP = (
    "幸い、当家は",
    "の収入に関しては\n他家に比べ豊か",
    "\n",
    "は合戦で役立つだけでなく\n外交で取引材料に使う\nこともでき",
)
RESOURCE_POLICY_JP = (
    "幸い、当家は",
    "の収入に関しては\n他家に比べ豊か",
    "\n外交や政策強化に利用するなど\n役立て",
)
EXPECTED_BASE_JP = {
    2366: RESOURCE_TRADE_JP,
    2367: RESOURCE_TRADE_JP,
    2368: RESOURCE_POLICY_JP,
    2369: RESOURCE_POLICY_JP,
    2370: RESOURCE_TRADE_JP,
    2371: RESOURCE_TRADE_JP,
    2372: ("今の目標、", "の", "を攻略すべき\n時期について", "が…"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
RESOURCE_TRADE_BASE_GAPS = (
    "",
    VALUE_TOKEN,
    "01431A020000",
    VALUE_TOKEN,
    "01433C040000050505",
)
RESOURCE_POLICY_BASE_GAPS = (
    "",
    VALUE_TOKEN,
    "01431A020000",
    "01431E040000050505",
)
RESOURCE_TRADE_PK_GAPS = (
    "",
    VALUE_TOKEN,
    "014326020000",
    VALUE_TOKEN,
    "014348040000050505",
)
RESOURCE_POLICY_PK_GAPS = (
    "",
    VALUE_TOKEN,
    "014326020000",
    "01432A040000050505",
)
EXPECTED_BASE_GAPS = {
    2366: RESOURCE_TRADE_BASE_GAPS,
    2367: RESOURCE_TRADE_BASE_GAPS,
    2368: RESOURCE_POLICY_BASE_GAPS,
    2369: RESOURCE_POLICY_BASE_GAPS,
    2370: RESOURCE_TRADE_BASE_GAPS,
    2371: RESOURCE_TRADE_BASE_GAPS,
    2372: ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "014326020000", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2366: RESOURCE_TRADE_PK_GAPS,
    2367: RESOURCE_TRADE_PK_GAPS,
    2368: RESOURCE_POLICY_PK_GAPS,
    2369: RESOURCE_POLICY_PK_GAPS,
    2370: RESOURCE_TRADE_PK_GAPS,
    2371: RESOURCE_TRADE_PK_GAPS,
    2372: ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "014332020000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2372:3"}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2366:2": "\n",
    "15:2367:2": "\n",
    "15:2370:2": "\n",
    "15:2371:2": "\n",
}
RESOURCE_TRADE_SC = (
    ("所幸本家的", "收入\n较别家更为充沛。\n", "不只可以用于合战，\n也可用作外交时的\n交易材料。"),
    ("", VALUE_TOKEN, VALUE_TOKEN, "050505"),
)
RESOURCE_TRADE_TC = (
    ("所幸本家在", "的收入方面比他家豐碩，\n", "不光是會戰能派上用場，\n在外交上亦可作為交易籌碼。"),
    ("", VALUE_TOKEN, VALUE_TOKEN, "050505"),
)
RESOURCE_POLICY_SC = (
    ("所幸本家的", "收入\n较别家更为充沛。\n用到外交和\n强化政策上吧。"),
    ("", VALUE_TOKEN, "050505"),
)
RESOURCE_POLICY_TC = (
    ("所幸本家在", "的收入方面比他家豐碩，\n不妨在外交及政策強化上物盡其用。"),
    ("", VALUE_TOKEN, "050505"),
)
SHARED_AUXILIARY = {
    **{
        (language, record_id): context
        for record_id in (2366, 2367, 2370, 2371)
        for language, context in (
            ("SC", RESOURCE_TRADE_SC),
            ("TC", RESOURCE_TRADE_TC),
        )
    },
    **{
        (language, record_id): context
        for record_id in (2368, 2369)
        for language, context in (
            ("SC", RESOURCE_POLICY_SC),
            ("TC", RESOURCE_POLICY_TC),
        )
    },
    ("SC", 2372): (
        ("关于现在的目标，应该攻略", "的", "\n的时期……"),
        ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2372): (
        ("現今目標應當攻略", "的", "，\n不過就時機上……"),
        ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505"),
    ),
}
RESOURCE_TRADE_EN = (
    (
        "Happily, we have a higher ",
        " income than other clans. This will not only prove useful in battle, "
        "but it can also be used as leverage for diplomacy.",
    ),
    ("", VALUE_TOKEN, "050505"),
)
RESOURCE_POLICY_EN = (
    (
        "Happily, we have a higher ",
        " income than other clans. We ought to invest in diplomacy and "
        "strengthening our policies. It would prove a great help.",
    ),
    ("", VALUE_TOKEN, "050505"),
)
PK_EN_AUXILIARY = {
    **{
        record_id: RESOURCE_TRADE_EN
        for record_id in (2366, 2367, 2370, 2371)
    },
    **{
        record_id: RESOURCE_POLICY_EN
        for record_id in (2368, 2369)
    },
    2372: (
        (
            "For this target, we should capture the ",
            "Ös ",
            ". ItÖs just a question of timing...",
        ),
        ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
HISTORICAL_EVIDENCE_URLS = {
    "合戦": "https://kotobank.jp/word/%E5%90%88%E6%88%A6-464384",
    "兵糧": "https://kotobank.jp/word/%E5%85%B5%E7%B3%A7-613629",
    "拮抗": "https://kotobank.jp/word/%E6%8B%AE%E6%8A%97-474707",
    "将兵": "https://kotobank.jp/word/%E5%B0%86%E5%85%B5-533207",
    "事を構える": "https://kotobank.jp/word/%E4%BA%8B%E3%82%92%E6%A7%8B%E3%81%88%E3%82%8B-502884",
    "めぼしい": "https://kotobank.jp/word/%E3%82%81%E3%81%BC%E3%81%97%E3%81%84-396520",
}
BASIS = (
    "review_queue_base_msggame_B118_C_pristine_base_pc_jp_authoritative_"
    "resource_income_battle_diplomatic_leverage_policy_investment_and_"
    "capture_timing_with_explicit_base2366_2372_to_pk2397_2403_plus31_"
    "mapping_exact_base_pk_jp_sc_tc_literals_actual_pk_en_context_dynamic_"
    "value_target_force_castle_token_direction_exact_reuse2366_2367_2370_"
    "2371_and2368_2369_hidden_lf_slots_current_layout_project_ellipsis_"
    "morphology_terminal_corpora_当家_as_uri_gamun_合戦_as_hapjeon_"
    "authoritative_dictionary_evidence_and_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    550: ("입니다", "다", "이오", "이옵니다"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    562: EXPECTED_BASE_MORPHOLOGY_TERMINALS[550],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 989 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 989 Base-to-PK JP literal drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    } != set(RECORD_ARITIES):
        raise RuntimeError("segment 989 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 989 pristine/current gap drifted")
    if (
        any(
            TRANSLATIONS_BY_RECORD[record_id] is not RESOURCE_TRADE_TRANSLATION
            for record_id in (2366, 2367, 2370, 2371)
        )
        or any(
            TRANSLATIONS_BY_RECORD[record_id] is not RESOURCE_POLICY_TRANSLATION
            for record_id in (2368, 2369)
        )
        or RESOURCE_POLICY_TRANSLATION
        is not CANONICAL_S988.TRANSLATIONS_BY_RECORD[2365]
    ):
        raise RuntimeError("segment 989 exact translation group reuse drifted")
    if set(EXCLUDED_NONVISIBLE_COORDINATES) != {
        "15:2366:2",
        "15:2367:2",
        "15:2370:2",
        "15:2371:2",
    }:
        raise RuntimeError("segment 989 hidden LF coordinate drifted")
    if (
        EXPECTED_BASE_GAPS[2372][1:3]
        != (TARGET_FORCE_TOKEN, CASTLE_TOKEN)
        or raw_translations["15:2372:0"] != "현재 목표인"
        or raw_translations["15:2372:1"] != "의"
        or not raw_translations["15:2372:2"].startswith("을(를) 공략")
    ):
        raise RuntimeError("segment 989 target-force/castle token direction drifted")
    if (
        raw_translations["15:2372:3"].count("…") != 1
        or translations["15:2372:3"].count("…") != 2
    ):
        raise RuntimeError("segment 989 project ellipsis pair drifted")
    joined = "\n".join(translations.values())
    for required in ("우리 가문", "합전", "협상 카드", "정책 강화", "공략"):
        if required not in joined:
            raise RuntimeError(f"segment 989 required terminology drifted: {required}")
    for forbidden in ("당가", "전투에서 유용", "거래 재료", "따위", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 989 forbidden wording retained: {forbidden}")
    if set(HISTORICAL_EVIDENCE_URLS) != {
        "合戦",
        "兵糧",
        "拮抗",
        "将兵",
        "事を構える",
        "めぼしい",
    }:
        raise RuntimeError("segment 989 historical evidence registry drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 989 visible decision count drifted")


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
    SUPPORT.annotate_morphology_evidence(
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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 989 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 989 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B118_S989",
                "source_literal_count": 26,
                "decision_count": len(rows),
                "hidden_non_display_count": 4,
                "runtime_fragment_pending": len(rows),
                "exact_translation_groups": [
                    [2366, 2367, 2370, 2371],
                    [2368, 2369],
                ],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": list(RECORD_ARITIES),
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
