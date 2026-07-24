#!/usr/bin/env python3
"""Build Base authoring segment 991 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment990 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S991.private.v1.jsonl"
)
SEGMENT = 991
VALUE_TOKEN = "023C"
TARGET_FORCE_TOKEN = "025132"
PROTRACTED_UNEASE = PREVIOUS.PROTRACTED_UNEASE
PROTRACTED_RISK_LEAD = PREVIOUS.PROTRACTED_RISK_LEAD
TRANSLATIONS_BY_RECORD = {
    2382: (
        PROTRACTED_UNEASE,
        "\n도와줄 우군이 더 있다면\n한결 든든한 상태",
        "…",
    ),
    2383: (
        PROTRACTED_RISK_LEAD,
        "\n병력과 병량 비축이 모두\n충분하다고 말하기 곤란",
    ),
    2384: (
        PROTRACTED_RISK_LEAD,
        "\n병량 비축과 우군의 전력이\n충분하다고 말하기 곤란",
    ),
    2385: (
        PROTRACTED_RISK_LEAD,
        "\n우리 가문의 병력과 우군의 전력이\n충분하다고 말하기 곤란",
    ),
    2386: (
        PROTRACTED_RISK_LEAD,
        "\n병량 비축과 우리 가문의 병력, 우군의 전력이\n충분하다고 말하기 곤란",
    ),
    2388: (
        "지금 우리는 여러 대세력과 인접해 있",
        "\n특히",
        "의",
        "와(과) 분쟁을 일으키는 것은\n피하는 편이 안전",
    ),
    2389: (
        "의",
        "의 동향은\n주시할 필요가 ",
    ),
    2390: ("이미 저쪽은 우리 가문을 노리는 듯…\n서둘러 대응책을 마련해야 할 것",),
    2391: ("다행히 지금은 우리 가문에 관심이 없는 듯…\n섣불리 자극하지 않는 편이 좋겠습니다",),
    2392: (
        "눈에 띄는 무장은 없다지만\n세력이 강대한 상태",
        "…",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2382: (
        "今の当家では戦を続けるにはやや不安",
        "\n手助けしてくれる味方が\nもっといれば心強いの",
        "が…",
    ),
    2383: (
        "今の当家では戦を続けるには不安",
        "\n兵の数と兵糧の備蓄ともに\n十分とは言いかね",
    ),
    2384: (
        "今の当家では戦を続けるには不安",
        "\n兵糧の備蓄と味方の戦力が\n十分とは言いかね",
    ),
    2385: (
        "今の当家では戦を続けるには不安",
        "\n当家の兵力と味方の戦力が\n十分とは言いかね",
    ),
    2386: (
        "今の当家では戦を続けるには不安",
        "\n兵糧の備蓄と当家の兵力、味方の戦力が\n十分とは言いかね",
    ),
    2388: (
        "今、我らは複数の大勢力と隣接して",
        "\n特に",
        "の",
        "と事を構えるのは\n避けたほうが無難",
    ),
    2389: (
        "の",
        "の動きには\n目を配っておく必要が",
    ),
    2390: ("すでにあちらは当家を狙っている様子…\n早々に何か手を打つべき",),
    2391: ("幸い、今は当家に関心がない様子…\n下手に刺激されぬが吉かと",),
    2392: (
        "めぼしい武将がいないとはいえ\n強大な勢力",
        "からな…",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2382: ("", "01434A020000", "01431A020000", "050505"),
    2383: ("", "01434A020000", "01433C040000050505"),
    2384: ("", "01434A020000", "01433C040000050505"),
    2385: ("", "01434A020000", "01433C040000050505"),
    2386: ("", "01434A020000", "01433C040000050505"),
    2388: ("", "0143B2000000", VALUE_TOKEN, TARGET_FORCE_TOKEN, "014356020000050505"),
    2389: (VALUE_TOKEN, TARGET_FORCE_TOKEN, "014358000000050505"),
    2390: ("", "014356020000050505"),
    2391: ("", "050505"),
    2392: ("", "014326020000", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2382: ("", "014356020000", "014326020000", "050505"),
    2383: ("", "014356020000", "014348040000050505"),
    2384: ("", "014356020000", "014348040000050505"),
    2385: ("", "014356020000", "014348040000050505"),
    2386: ("", "014356020000", "014348040000050505"),
    2388: ("", "0143B2000000", VALUE_TOKEN, TARGET_FORCE_TOKEN, "014362020000050505"),
    2389: EXPECTED_BASE_GAPS[2389],
    2390: ("", "014362020000050505"),
    2391: EXPECTED_BASE_GAPS[2391],
    2392: ("", "014332020000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2382:2",
    "15:2390:0",
    "15:2391:0",
    "15:2392:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SC_CONTEXT = {
    2382: (("以本家现在的状态，有些不宜继续作战啊。\n若是肯帮忙的战友再多些，\n倒是叫人胆壮……",), ("", "050505")),
    2383: (("以本家现在的状态，不宜继续作战啊。\n士兵的数量和军粮储备\n都算不上充分。",), ("", "050505")),
    2384: (("以本家现在的状态，不宜继续作战啊。\n军粮储备与战友的战力\n算不上充分。",), ("", "050505")),
    2385: (("以本家现在的状态，不宜继续作战啊。\n本家的兵力与战友的战力\n算不上充分。",), ("", "050505")),
    2386: (("以本家现在的状态，不宜继续作战啊。\n军粮储备、本家的兵力与战友的战力\n算不上充分。",), ("", "050505")),
    2388: (
        ("如今我们与多个大势力相邻，\n尤其是", "的", "，\n最好不要轻启战端。"),
        ("", VALUE_TOKEN, TARGET_FORCE_TOKEN, "050505"),
    ),
    2389: (("的", "的动向\n需要留意。"), (VALUE_TOKEN, TARGET_FORCE_TOKEN, "050505")),
    2390: (("它似乎已经盯上本家了……\n应该尽早应对才是。",), ("", "050505")),
    2391: (("所幸它现在似乎对本家没有兴趣……\n我看还是少刺激为妙。",), ("", "050505")),
    2392: (("虽说没有什么像样的将领，\n但毕竟是一个强大的势力……",), ("", "050505")),
}
TC_CONTEXT = {
    2382: (("本家目前繼續打仗略微堪憂，\n若能有更多戰友將踏實許多……",), ("", "050505")),
    2383: (("本家目前繼續打仗暗藏隱憂，\n兵力及軍糧皆未十分充足。",), ("", "050505")),
    2384: (("本家目前繼續打仗暗藏隱憂，\n軍糧及我方戰力皆未十分充足。",), ("", "050505")),
    2385: (("本家目前繼續打仗暗藏隱憂，\n本家兵力及我方戰力皆未十分充足。",), ("", "050505")),
    2386: (("本家目前繼續打仗暗藏隱憂，\n軍糧、本家兵力、我方戰力\n皆未十分充足。",), ("", "050505")),
    2388: (
        ("我方目前鄰接多數大勢力，\n應極力避免和", "的", "挑起事端。"),
        ("", VALUE_TOKEN, TARGET_FORCE_TOKEN, "050505"),
    ),
    2389: (("的", "動向必須格外注意。"), (VALUE_TOKEN, TARGET_FORCE_TOKEN, "050505")),
    2390: (("對方似乎對本家虎視眈眈……\n及早設法因應方為上策。",), ("", "050505")),
    2391: (("所幸目前對本家似乎興趣缺缺……\n別隨意刺激方為明智之舉。",), ("", "050505")),
    2392: (("當中雖無出色武將，\n但勢力強大……",), ("", "050505")),
}
PK_EN_CONTEXT = {
    2382: (("Our clan might not last long enough in this battle. If we had more allies we could rely on for reinforcements, IÖd have more confidence...",), ("", "050505")),
    2383: (("It is uncertain whether our clan can hold out in a protracted battle. We are lacking in both soldiers and supplies.",), ("", "050505")),
    2384: (("It is uncertain whether our clan can hold out in a protracted battle. We are lacking in both supplies and allies.",), ("", "050505")),
    2385: (("It is uncertain whether our clan can hold out in a protracted battle. We are lacking in both soldiers and allies.",), ("", "050505")),
    2386: (("It is uncertain whether our clan can hold out in a protracted battle. We are lacking in supplies, soldiers, and allies.",), ("", "050505")),
    2388: (
        (
            "At present, we are adjacent to many large clans. We should probably avoid taking an aggressive stance with the ",
            " of ",
            " in particular.",
        ),
        ("", TARGET_FORCE_TOKEN, VALUE_TOKEN, "050505"),
    ),
    2389: (
        ("We ought to keep a close eye on the movements of the ", " of ", "."),
        ("", TARGET_FORCE_TOKEN, VALUE_TOKEN, "050505"),
    ),
    2390: (("It would seem theyÖre already targeting us... We need to begin taking preventive measures.",), ("", "050505")),
    2391: (("Thankfully, they donÖt seem to be concerned with us. IÖm just happy it didnÖt provoke us into a needless battle.",), ("", "050505")),
    2392: (("Although their officers arenÖt so impressive, the clan is simply enormous...",), ("", "050505")),
}
SHARED_AUXILIARY = {
    **{("SC", record_id): context for record_id, context in SC_CONTEXT.items()},
    **{("TC", record_id): context for record_id, context in TC_CONTEXT.items()},
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_CONTEXT,
)
EMPTY_RECORD_ID = 2387
EMPTY_PK_RECORD_ID = 2418
EMPTY_RECORD_HEX = "0143674A0200050505"
HISTORICAL_EVIDENCE_URLS = {
    "事を構える": "https://kotobank.jp/word/%E4%BA%8B%E3%82%92%E6%A7%8B%E3%81%88%E3%82%8B-502884",
    "めぼしい": "https://kotobank.jp/word/%E3%82%81%E3%81%BC%E3%81%97%E3%81%84-396520",
    "兵糧": "https://kotobank.jp/word/%E5%85%B5%E7%B3%A7-613629",
}
BASIS = (
    "review_queue_base_msggame_B118_C_pristine_base_pc_jp_authoritative_"
    "protracted_war_allied_force_balance_neighboring_major_power_risk_"
    "monitoring_and_officer_assessment_with_explicit_base2382_2392_"
    "excluding_empty2387_to_pk2413_2423_plus31_mapping_exact_base_pk_jp_"
    "sc_tc_literals_actual_pk_en_context_cross_language_dynamic_token_"
    "direction_explicit_gap_divergence_morphology_terminal_corpora_project_"
    "ellipsis_current_line_counts_our_clan_as_uri_gamun_hyoryo_as_"
    "byungryang_koto_o_kamaeru_as_start_dispute_meboshii_as_noteworthy_"
    "dictionary_evidence_and_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    88: ("있겠지요", "이리라", "입니다", "있습니다", "이겠지요"),
    178: ("있습니다", "있다", "있사옵니다"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    550: ("입니다", "다", "이오", "이옵니다"),
    586: ("이지요", "이군", "이군요", "이옵니다요", "이옵니다그려"),
    598: ("이겠지요", "이리라", "이겠지"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    88: ("있겠지요", "이리라", "이겠지요"),
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    562: EXPECTED_BASE_MORPHOLOGY_TERMINALS[550],
    598: EXPECTED_BASE_MORPHOLOGY_TERMINALS[586],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 991 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 991 Base-to-PK JP literal drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {2382, 2383, 2384, 2385, 2386, 2388, 2390, 2392}:
        raise RuntimeError("segment 991 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 991 pristine/current gap drifted")
    if (
        TRANSLATIONS_BY_RECORD[2382][0] is not PREVIOUS.PROTRACTED_UNEASE
        or any(
            TRANSLATIONS_BY_RECORD[record_id][0]
            is not PREVIOUS.PROTRACTED_RISK_LEAD
            for record_id in (2383, 2384, 2385, 2386)
        )
    ):
        raise RuntimeError("segment 991 cross-segment canonical lead reuse drifted")
    if (
        EXPECTED_BASE_GAPS[2388][2:4] != (VALUE_TOKEN, TARGET_FORCE_TOKEN)
        or EXPECTED_BASE_GAPS[2389][:2] != (VALUE_TOKEN, TARGET_FORCE_TOKEN)
        or PK_EN_CONTEXT[2388][1][1:3] != (TARGET_FORCE_TOKEN, VALUE_TOKEN)
        or PK_EN_CONTEXT[2389][1][1:3] != (TARGET_FORCE_TOKEN, VALUE_TOKEN)
    ):
        raise RuntimeError("segment 991 cross-language token direction drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(f"segment 991 project ellipsis pair drifted: {coordinate}")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "병량",
        "우군",
        "분쟁을 일으키",
        "동향",
        "눈에 띄는 무장",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 991 required terminology drifted: {required}")
    for forbidden in ("당가", "군량", "일을 벌이", "움직임에는", "별 볼 일 없는"):
        if forbidden in joined:
            raise RuntimeError(f"segment 991 forbidden wording retained: {forbidden}")
    if set(HISTORICAL_EVIDENCE_URLS) != {"事を構える", "めぼしい", "兵糧"}:
        raise RuntimeError("segment 991 historical evidence registry drifted")
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 991 visible decision count drifted")


def assert_empty_record(prepared: Any) -> None:
    resources = (
        ("base_msggame", EMPTY_RECORD_ID),
        ("pk_msggame", EMPTY_PK_RECORD_ID),
    )
    for resource_name, record_id in resources:
        resource = prepared.resources[resource_name]
        archives = {
            "pristine": resource.pristine_archive,
            "current": resource.current_archive,
            **resource.context_archives,
        }
        for label, archive in archives.items():
            record = ENGINE.archive_records(archive)[(15, record_id)]
            if (
                record.data.hex().upper() != EMPTY_RECORD_HEX
                or ENGINE.parse_record_literals(record)
            ):
                raise RuntimeError(
                    f"segment 991 empty record drifted: {resource_name}/{label}/{record_id}"
                )


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
    assert_empty_record(prepared)
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
    static_row = next(row for row in rows if row["coordinate"] == "15:2391:0")
    static_row["scope_classification"] = "retranslated"
    static_row["runtime_review"] = "not_required"
    static_row["basis"] = (
        "pristine_base_pc_jp_authoritative_static_complete_literal_"
        "avoid_unnecessary_provocation_translation"
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 991 validated count drifted")
    static_rows = [row for row in rows if row["coordinate"] == "15:2391:0"]
    pending_rows = [row for row in rows if row["coordinate"] != "15:2391:0"]
    if (
        len(static_rows) != 1
        or static_rows[0]["scope_classification"] != "retranslated"
        or static_rows[0]["runtime_review"] != "not_required"
        or any(
            row["scope_classification"] != "runtime_fragment_pending"
            or row["runtime_review"] != "pending"
            for row in pending_rows
        )
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError("segment 991 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B118_S991",
                "source_literal_count": 21,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "excluded_empty_record_ids": [EMPTY_RECORD_ID],
                "retranslated": 1,
                "runtime_fragment_pending": len(rows) - 1,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2382,
                    2383,
                    2384,
                    2385,
                    2386,
                    2388,
                    2390,
                    2392,
                ],
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
