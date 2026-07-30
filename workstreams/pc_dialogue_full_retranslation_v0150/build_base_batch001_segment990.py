#!/usr/bin/env python3
"""Build Base authoring segment 990 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment989 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S990.private.v1.jsonl"
)
SEGMENT = 990
PROTRACTED_RISK_LEAD = "현재 우리 가문이 전투를 계속하기에는 불안한 상황"
PROTRACTED_UNEASE = "현재 우리 가문이 전투를 계속하기에는 다소 불안한 상황"
TRANSLATIONS_BY_RECORD = {
    2373: (
        "유감스럽게도 현재 우리는 열세지만\n장병은 모두 출진할 준비가 되어",
        "\n판단은",
        "맡기",
    ),
    2374: (
        "아직 충분한 준비가",
        "\n열세인 채로 공격하면 승산이 희박하니\n출진 시기를 신중히 판단하",
        "결정해 주시기를 청하",
    ),
    2375: (
        "양측의 전력은 팽팽히 맞서고",
        "만,\n이미 아군 장병도 출진할 준비가 되어\n",
        "그러므로 언제든 출진할 수 있",
    ),
    2376: (
        "아직 출진할 채비가",
        "만,\n다행히 양측의 전력은 팽팽히 맞서고",
        "\n출진 시기를 신중히 판단해",
    ),
    2377: (
        "우리 병력이 우세한 것은 분명…\n장병의 채비도 모두 갖추어져",
        "그러므로\n언제든 출진할 수 있",
    ),
    2378: (
        "모든 군에서 채비를 마친 것은 아니지만\n이미 우리가 우세한 상태",
        "\n출진 여부는",
        "맡기",
    ),
    2379: ("우리 측은 준비를 모두 마쳤고\n문제는 없는 상태",),
    2380: (
        PROTRACTED_RISK_LEAD,
        "\n병력과 병량 비축이 모두\n충분하다고 말하기 곤란",
    ),
    2381: (
        PROTRACTED_UNEASE,
        "\n병량을 더 많이 비축하면\n한결 든든한 상태",
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
    2373: (
        "残念ながら目下、我らは劣勢なれど\n将兵の支度は整って",
        "\nご判断は",
        "任せ",
    ),
    2374: (
        "こちらはまだ十分に準備が整って",
        "\n劣勢のまま攻め込めば勝機は薄いゆえ\n出陣の時期は慎重に",
        "判断願",
    ),
    2375: (
        "双方の戦力は拮抗して",
        "が、\nすでにこちらの将兵の支度は整って\n",
        "ゆえ、いつでも出陣でき",
    ),
    2376: (
        "こちらの支度はまだ整って",
        "が、\n幸い、戦力は拮抗して",
        "\n出陣の時期は慎重に見極めて",
    ),
    2377: (
        "我らの兵力が優位にあるは明白…\n将兵の支度もすべて整って",
        "ゆえ\nいつでも出陣でき",
    ),
    2378: (
        "すべての郡で支度を終えたとは言えぬものの\nすでに我らが優勢な状態",
        "\n出陣の判断は",
        "任せ",
    ),
    2379: ("こちらの準備は万端\n問題はないはず",),
    2380: (
        "今の当家では戦を続けるには不安",
        "\n兵の数と兵糧の備蓄共に\n十分とは言いかね",
    ),
    2381: (
        "今の当家では戦を続けるにはやや不安",
        "\n兵糧の備蓄がもっとあれば\n心強いの",
        "が…",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2373: ("", "0143B2000000", "014384040000", "01438E000000050505"),
    2374: ("", "0143A0000000", "01438A040000", "0143BE000000050505"),
    2375: ("", "0143B2000000", "0143B2000000", "01433C0400000143F6010000050505"),
    2376: ("", "0143A0000000", "0143B2000000", "014342010000050505"),
    2377: ("", "0143B2000000", "01433C0400000143F6010000050505"),
    2378: ("", "01431A020000", "014384040000", "01438E000000050505"),
    2379: ("", "01431A020000050505"),
    2380: ("", "01434A020000", "01433C040000050505"),
    2381: ("", "01434A020000", "01431A020000", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2373: ("", "0143B2000000", "014390040000", "01438E000000050505"),
    2374: ("", "0143A0000000", "014396040000", "0143BE000000050505"),
    2375: ("", "0143B2000000", "0143B2000000", "0143480400000143FC010000050505"),
    2376: EXPECTED_BASE_GAPS[2376],
    2377: ("", "0143B2000000", "0143480400000143FC010000050505"),
    2378: ("", "014326020000", "014390040000", "01438E000000050505"),
    2379: ("", "014326020000050505"),
    2380: ("", "014356020000", "014348040000050505"),
    2381: ("", "014356020000", "014326020000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2377:0",
    "15:2381:2",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SC_TEXT = {
    2373: "很遗憾，眼下我们处于劣势，\n但将士都已准备就绪。\n就由您来做出决断吧。",
    2374: "我们尚未准备万全，\n处于劣势时就进攻，胜算太小，\n请您谨慎选择出阵的时期。",
    2375: "双方的战力不相上下，\n但我方将士已准备就绪，\n随时可以出阵。",
    2376: "我方尚未准备就绪，\n但所幸双方战力不相上下，\n还是谨慎选择出阵时机吧。",
    2377: "我们的兵力明显处于优势……\n将士也已准备万全，\n随时都可以出阵。",
    2378: "眼下并非所有郡都准备就绪了，\n但我方已处于优势，\n何时出阵就请您来决断了。",
    2379: "我们已经准备万全，\n应该没有问题了。",
    2380: "以本家现在的状态，不宜继续作战啊。\n士兵的数量和军粮的储备\n都算不上充分。",
    2381: "以本家现在的状态，有些不宜继续作战啊。\n若是军粮储备再多些，\n倒是叫人胆壮……",
}
TC_TEXT = {
    2373: "遺憾的是，我方目前處於劣勢，\n將士則已蓄勢待發，\n一切遵照大人判斷。",
    2374: "這邊尚未做好充分準備，\n以劣勢進攻難有勝算，\n望請大人謹慎判斷出陣時機。",
    2375: "雙方戰力旗鼓相當，\n這邊的將士則已蓄勢待發，\n隨時皆可出征。",
    2376: "這邊尚未做好萬全準備，\n所幸戰力旗鼓相當，\n望請大人謹慎評估出陣時機。",
    2377: "我方兵力明顯佔上風……\n將士也已蓄勢待發，\n隨時都可出陣。",
    2378: "儘管稱不上所有郡皆已做好準備，\n不過我方處於優勢，\n出陣與否遵照大人判斷。",
    2379: "這邊一切準備就緒，\n應該不成問題。",
    2380: "本家目前繼續打仗暗藏隱憂，\n兵力及軍糧皆未十分充足。",
    2381: "本家目前繼續打仗略微堪憂，\n若能有更多軍糧將踏實許多……",
}
PK_EN_TEXT = {
    2373: (
        "Unfortunately, we are at a disadvantage, but our soldiers are all "
        "ready and waiting. I trust your judgment."
    ),
    2374: (
        "We have yet to finish preparations; our chances for victory are slim "
        "if we launch the attack in this state. I ask that you carefully "
        "consider when to order the march."
    ),
    2375: (
        "Our forces are of comparable size, and the soldiers are all prepared. "
        "We are ready to march on your order."
    ),
    2376: (
        "We are not yet prepared, but our force luckily matches their strength. "
        "Please carefully consider the timing when ordering the march."
    ),
    2377: (
        "We clearly outmatch the enemy, and our preparations are in order. "
        "We are ready to march on your order."
    ),
    2378: (
        "Although not every county has finished its preparations, we already "
        "have the superior force. We await your order to march."
    ),
    2379: "We are fully prepared. There should be no problems.",
    2380: (
        "It is uncertain whether our clan can hold out in a protracted battle. "
        "We are lacking in both soldiers and supplies."
    ),
    2381: (
        "Our clan might not last long enough in this battle. If we only had a "
        "larger stock of supplies, IÖd have more confidence..."
    ),
}
SHARED_AUXILIARY = {
    (language, record_id): ((texts[record_id],), ("", "050505"))
    for language, texts in (("SC", SC_TEXT), ("TC", TC_TEXT))
    for record_id in RECORD_ARITIES
}
PK_EN_AUXILIARY = {
    record_id: ((PK_EN_TEXT[record_id],), ("", "050505"))
    for record_id in RECORD_ARITIES
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
HISTORICAL_EVIDENCE_URLS = {
    "万端": "https://kotobank.jp/word/%E4%B8%87%E7%AB%AF-606854",
    "拮抗": "https://kotobank.jp/word/%E6%8B%AE%E6%8A%97-474707",
    "将兵": "https://kotobank.jp/word/%E5%B0%86%E5%85%B5-533207",
    "兵糧": "https://kotobank.jp/word/%E5%85%B5%E7%B3%A7-613629",
}
BASIS = (
    "review_queue_base_msggame_B118_C_pristine_base_pc_jp_authoritative_"
    "battle_readiness_force_balance_sortie_timing_protracted_war_manpower_"
    "and_hyoryo_with_explicit_base2373_2381_to_pk2404_2412_plus31_mapping_"
    "exact_base_pk_jp_sc_tc_literals_actual_pk_en_context_explicit_gap_"
    "divergence_and_morphology_terminal_corpora_project_ellipsis_current_"
    "line_counts_our_clan_as_uri_gamun_gun_as_county_hyoryo_as_byungryang_"
    "dictionary_evidence_and_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    142: ("하겠습니다", "하다", "하겠사옵니다"),
    160: ("없사옵니다", "없다", "없습니다"),
    178: ("있습니다", "있다", "있사옵니다"),
    190: ("있습니다", "으", "있사옵니다"),
    322: ("주시오", "다오", "주소서"),
    502: ("", "다", "여"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    586: ("이지요", "이군", "이군요", "이옵니다요", "이옵니다그려"),
    1084: ("합니다", "다", "하옵니다"),
    1156: ("오", ""),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
    160: EXPECTED_BASE_MORPHOLOGY_TERMINALS[160],
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    190: EXPECTED_BASE_MORPHOLOGY_TERMINALS[190],
    322: EXPECTED_BASE_MORPHOLOGY_TERMINALS[322],
    508: EXPECTED_BASE_MORPHOLOGY_TERMINALS[502],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    598: EXPECTED_BASE_MORPHOLOGY_TERMINALS[586],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
    1168: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1156],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 990 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 990 Base-to-PK JP literal drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {2373, 2374, 2375, 2377, 2378, 2379, 2380, 2381}:
        raise RuntimeError("segment 990 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 990 pristine/current gap drifted")
    if (
        raw_translations["15:2377:0"].count("…") != 1
        or translations["15:2377:0"].count("…") != 2
        or raw_translations["15:2381:2"].count("…") != 1
        or translations["15:2381:2"].count("…") != 2
    ):
        raise RuntimeError("segment 990 project ellipsis pair drifted")
    joined = "\n".join(translations.values())
    for required in ("장병", "팽팽히 맞서", "모든 군", "병량", "우리 가문"):
        if required not in joined:
            raise RuntimeError(f"segment 990 required terminology drifted: {required}")
    for forbidden in ("당가", "장수와 병사", "군량", "균형을 이루"):
        if forbidden in joined:
            raise RuntimeError(f"segment 990 forbidden wording retained: {forbidden}")
    if TRANSLATIONS_BY_RECORD[2379] != (
        "우리 측은 준비를 모두 마쳤고\n문제는 없는 상태",
    ):
        raise RuntimeError("segment 990 readiness conclusion drifted")
    if set(HISTORICAL_EVIDENCE_URLS) != {"万端", "拮抗", "将兵", "兵糧"}:
        raise RuntimeError("segment 990 historical evidence registry drifted")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 990 visible decision count drifted")


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
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 990 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 990 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B118_S990",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2373,
                    2374,
                    2375,
                    2377,
                    2378,
                    2379,
                    2380,
                    2381,
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
