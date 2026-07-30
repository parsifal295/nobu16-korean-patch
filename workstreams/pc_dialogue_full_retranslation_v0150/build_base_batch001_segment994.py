#!/usr/bin/env python3
"""Build Base authoring segment 994 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment993 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S994.private.v1.jsonl"
)
SEGMENT = 994
SCHEME_TOKEN = "023C"
SPY_FORCE_TOKEN = "02483E"
DETECTOR_TOKEN = "024635"
OFFICER_TOKEN = "024833"
TARGET_FORCE_TOKEN = "025032"
CASTLE_TOKEN = "026432"
TRANSLATIONS_BY_RECORD: dict[int, tuple[str | None, ...]] = {
    2411: (
        "천하통일까지는 아직 갈 길이 머니\n"
        "신하들의 전의를 북돋우기 위해\n"
        "단기 목표를 내거는 것은",
    ),
    2412: (
        "눈앞의 목표가 있어야\n"
        "평소 임무에도 힘이 나는 법…\n"
        "그래서 한 가지 방안을 고안",
    ),
    2413: (
        "붙잡은 간자는",
        "의 소속자",
        "\n보복을 위해 이번에는",
        "을(를) 뜻대로 조종해\n적을 동요시키",
    ),
    2414: (
        "을(를) 겨냥한",
        "공작을\n이",
        "이(가) 간파",
        "!",
    ),
    2415: (
        "이번",
        ",",
        "에게 간파되어\n오히려 아군까지 동요",
        None,
        "을(를) 상대로 조략을 펼칠 때는 신중하",
        "주의해",
    ),
    2416: (
        "에서 수상한 움직임을 감지",
        "\n즉시 경비를 보내자 간자는 물러났고\n다행히 이번에는 무사했다는 보고",
    ),
    2417: (
        "우리 가문을 얕보고 조략을 꾸민 대가를\n치르게 해 주",
    ),
    2418: (
        "이(가) 조략을 간파한 여파로\n",
        "에서는",
        "이(가)\n",
        "에게 의심을 품은 듯…",
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
EXPECTED_BASE_JP = {
    2411: (
        "天下統一までは未だ道遠く\n臣下の戦意を盛り上げるためにも\n短期目標を掲げては",
    ),
    2412: (
        "手近な目標があってこそ\n日頃の任にも精が出るというもの…\nそこでひとつ、考えてみ",
    ),
    2413: (
        "捕らえた間者は",
        "の者",
        "\n意趣返しとしてここは",
        "を手玉にとり\n敵へ動揺を与え",
    ),
    2414: (
        "への",
        "工作\nこの",
        "が看破し",
        "！",
    ),
    2415: (
        "此度の",
        "、",
        "により看破され\nかえって味方に動揺が広が",
        "\n",
        "への調略は",
        "注意",
    ),
    2416: (
        "にて不審な動きを察知し",
        "\n直ちに警固を差し向けると、間者は退散し\n此度は幸いにも事なきを得た",
    ),
    2417: ("当家を侮り、調略した報い\n受けてもら",),
    2418: (
        "が調略を看破した余波で\n",
        "において",
        "が\n",
        "に疑念を抱いている模様…",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    2414: (
        "への",
        "工作\nこの",
        "が看破してみせ",
        "！",
    ),
}
EXPECTED_BASE_GAPS = {
    2411: ("", "0143B0020000014356020000050505"),
    2412: ("", "014314020000050505"),
    2413: ("", SPY_FORCE_TOKEN, "0143BC020000", "014315000000", "01431E040000050505"),
    2414: (CASTLE_TOKEN, SCHEME_TOKEN, DETECTOR_TOKEN, "0143140200000143F6010000", "050505"),
    2415: ("", SCHEME_TOKEN, OFFICER_TOKEN, "014368020000", CASTLE_TOKEN, "01438A040000", "014396010000050505"),
    2416: (CASTLE_TOKEN, "014314020000", "0143BC020000050505"),
    2417: ("", "0143CA000000050505"),
    2418: (TARGET_FORCE_TOKEN, CASTLE_TOKEN, "01431D000000", "014308000000", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2411: ("", "0143BC020000014362020000050505"),
    2412: ("", "01431A020000050505"),
    2413: ("", SPY_FORCE_TOKEN, "0143C8020000", "014315000000", "01432A040000050505"),
    2414: (CASTLE_TOKEN, SCHEME_TOKEN, DETECTOR_TOKEN, "01431B0200000143FC010000", "050505"),
    2415: ("", SCHEME_TOKEN, OFFICER_TOKEN, "014374020000", CASTLE_TOKEN, "014396040000", "01439C010000050505"),
    2416: (CASTLE_TOKEN, "01431A020000", "0143C8020000050505"),
    2417: EXPECTED_BASE_GAPS[2417],
    2418: (TARGET_FORCE_TOKEN, CASTLE_TOKEN, "014322000000", "014308000000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2412:0",
    "15:2418:3",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:2415:3": "\n"}
SC_CONTEXT = {
    2411: (("天下统一之日依然遥远，\n不妨明示短期目标以激发\n臣民们的斗志如何？",), ("", "050505")),
    2412: (("若有近期内必须达成的目标，\n平日的行事必将战战兢兢……\n故而想出设定目标的对策。",), ("", "050505")),
    2413: (("据称抓住的间谍来自", "。\n作为报复手段，操纵", "，\n给敌人造成动摇吧。"), ("", SPY_FORCE_TOKEN, "014315000000", "050505")),
    2414: (("对", "的", "工作，\n已被我", "识破了！"), ("", CASTLE_TOKEN, SCHEME_TOKEN, DETECTOR_TOKEN, "050505")),
    2415: (("这次的", "被", "给识破了，\n反倒是己方开始大范围动摇。\n请小心对", "的谋略。"), ("", SCHEME_TOKEN, OFFICER_TOKEN, CASTLE_TOKEN, "050505")),
    2416: (("发现", "有可疑的动作。\n在立即加强警戒后，间谍逃跑了。\n这次没出什么大事真是万幸。"), ("", CASTLE_TOKEN, "050505")),
    2417: (("对本家的侮辱与谋害，\n好好尝尝这报应吧。",), ("", "050505")),
    2418: (("由于", "的谋略遭识破，\n其余波使", "的", "对\n", "心存猜疑的样子…"), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "01431D000000", "014308000000", "050505")),
}
TC_CONTEXT = {
    2411: (("天下統一之日依然遙遠，\n不妨明示短期目標以激發\n臣民們的鬥志如何？",), ("", "050505")),
    2412: (("若有近期內必須達成的目標，\n平日的行事必將戰戰兢兢……\n故而想出設定目標的對策。",), ("", "050505")),
    2413: (("擒獲的間諜是", "的人。\n那就利用", "來動搖敵方陣營，\n進行報復。"), ("", SPY_FORCE_TOKEN, "014315000000", "050505")),
    2414: (("這", "早已識破\n對", "的", "工作！"), ("", DETECTOR_TOKEN, CASTLE_TOKEN, SCHEME_TOKEN, "050505")),
    2415: (("這次的", "遭", "識破，\n令我方軍心動搖。\n務必留心針對", "的謀略。"), ("", SCHEME_TOKEN, OFFICER_TOKEN, CASTLE_TOKEN, "050505")),
    2416: (("在察覺", "中有可疑之人後，\n立刻加強警戒並驅逐了間諜，\n成功避免了一場禍事。"), ("", CASTLE_TOKEN, "050505")),
    2417: (("務必要讓他們接受漠視本家，\n暗自謀略的懲罰。",), ("", "050505")),
    2418: (("識破謀略後餘波盪漾，\n關於", "，", "對", "\n似乎心存猜疑……"), (TARGET_FORCE_TOKEN, CASTLE_TOKEN, "01431D000000", "014308000000", "050505")),
}
PK_EN_CONTEXT = {
    2411: (("The road towards unification is still long. What do you think of setting a short-term objective to boost the fighting spirit of our retainers?",), ("", "050505")),
    2412: (("IÖve thought up a short-term goal that would help boost morale for even our mundane, everyday tasks.",), ("", "050505")),
    2413: (("The captured spy turned out to be from the ", ". As revenge, we could use them to throw the enemy into disarray."), ("", SPY_FORCE_TOKEN, "050505")),
    2414: (("Ha! As if a ", " plot against ", " would ever get past me, the vigilant ", "!"), ("", SCHEME_TOKEN, CASTLE_TOKEN, DETECTOR_TOKEN, "050505")),
    2415: (("The recent ", " attempt was discovered by ", ", and the failure has caused a disturbance among our allies. We ought to be cautious performing any covert actions against ", "."), ("", SCHEME_TOKEN, OFFICER_TOKEN, CASTLE_TOKEN, "050505")),
    2416: (("A suspicious person was detected lurking around ", ", but they fled once guards were dispatched. Fortunately, the matter has been resolved without cause for alarm."), ("", CASTLE_TOKEN, "050505")),
    2417: (("They will pay for this insult to our clan.",), ("", "050505")),
    2418: (("After the ", " detected our scheme, it seems the people of ", " are harboring some misgivings about you."), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505")),
}
SHARED_AUXILIARY = {
    **{("SC", record_id): context for record_id, context in SC_CONTEXT.items()},
    **{("TC", record_id): context for record_id, context in TC_CONTEXT.items()},
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_CONTEXT,
)
AUXILIARY_OVERRIDES[("pk", "SC", 2418)] = (
    SC_CONTEXT[2418][0],
    ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "014322000000", "014308000000", "050505"),
)
AUXILIARY_OVERRIDES[("pk", "TC", 2418)] = (
    TC_CONTEXT[2418][0],
    (TARGET_FORCE_TOKEN, CASTLE_TOKEN, "014322000000", "014308000000", "050505"),
)
HISTORICAL_EVIDENCE_URLS = {
    "間者": "https://kotobank.jp/word/%E9%96%93%E8%80%85-172144",
    "調略": "https://kotobank.jp/word/%E8%AA%BF%E7%95%A5-569172",
    "意趣返し": "https://kotobank.jp/word/%E6%84%8F%E8%B6%A3%E8%BF%94%E3%81%97-432293",
    "手玉に取る": "https://kotobank.jp/word/%E6%89%8B%E7%8E%89%E3%81%AB%E5%8F%96%E3%82%8B-576003",
}
BASIS = (
    "review_queue_base_msggame_B119_A_pristine_base_pc_jp_authoritative_"
    "short_term_goal_counsel_counterintelligence_spy_revenge_scheme_"
    "detection_and_suspicion_with_explicit_base2411_2418_to_pk2442_2449_"
    "plus31_mapping_record2414_jp_literal_divergence_record2418_sc_tc_gap_"
    "divergence_cross_language_scheme_castle_officer_force_token_direction_"
    "hidden2415_lf_actual_morphology_terminal_corpora_project_ellipsis_"
    "current_line_counts_protected_skeleton_kotobank_evidence_and_runtime_"
    "fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    8: (
        "아버님", "어머님", "할아버님", "할머님", "숙부님", "숙모님",
        "그대", "너", "주군님", "주군", "도련님", "공주님", "쇼군님",
        "스님", "네놈", "귀하", "귀공", "원숭이", "놈", "이놈", "누님", "형님",
    ),
    21: (
        "아버님", "어머님", "할아버님", "할머님", "숙부님", "숙모님",
        "님", "주군님", "주군", "도련님", "공주님", "쇼군님", "스님",
        "그자", "그분", "원숭이", "저놈 녀석", "저놈", "이놈", "누님", "형님",
    ),
    29: (
        "아버님", "어머님", "할아버님", "할머님", "숙부님", "숙모님",
        "님", "주군님", "주군", "도련님", "공주님", "그분", "그자",
        "쇼군님", "스님", "원숭이", "놈", "누님", "형님",
    ),
    202: ("있겠지요", "오"),
    406: ("주십시오", "해 다오", "저것", "주시오"),
    502: ("", "다", "여"),
    532: ("했습니다", "다"),
    598: ("이겠지요", "이리라", "이겠지"),
    616: ("했습니다", "었다"),
    688: ("어떻게", "어떠하오"),
    700: ("라고 함", "라는 이야기", "라는 것", "라는 소식", "와의 이야기"),
    1054: ("합시다", "듯"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    8: (
        "아버님", "어머님", "할아버님", "할머님", "숙부님", "숙모님",
        "그대", "너", "주군님", "주군", "도련님", "공주님", "쇼군님",
        "스님", "네놈", "님", "귀하", "귀공", "원숭이", "놈", "이놈",
        "누님", "형님",
    ),
    21: (
        "아버님", "어머님", "할아버님", "할머님", "숙부님", "숙모님",
        "님", "주군님", "주군", "도련님", "공주님", "쇼군님", "스님",
        "그자", "그분", "원숭이", "저놈 녀석", "저놈", "이놈", "누님", "형님",
    ),
    34: ("님", "주군"),
    202: EXPECTED_BASE_MORPHOLOGY_TERMINALS[202],
    412: EXPECTED_BASE_MORPHOLOGY_TERMINALS[406],
    508: EXPECTED_BASE_MORPHOLOGY_TERMINALS[502],
    538: EXPECTED_BASE_MORPHOLOGY_TERMINALS[532],
    539: EXPECTED_BASE_MORPHOLOGY_TERMINALS[532],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    712: EXPECTED_BASE_MORPHOLOGY_TERMINALS[700],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 994 Base-to-PK mapping drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
    } != {2414}:
        raise RuntimeError("segment 994 Base-to-PK JP literal divergence drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    } != {2411, 2412, 2413, 2414, 2415, 2416, 2418}:
        raise RuntimeError("segment 994 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 994 pristine/current gap drifted")
    if (
        EXPECTED_BASE_GAPS[2414][:3]
        != (CASTLE_TOKEN, SCHEME_TOKEN, DETECTOR_TOKEN)
        or EXPECTED_BASE_GAPS[2415][1:3] != (SCHEME_TOKEN, OFFICER_TOKEN)
        or EXPECTED_BASE_GAPS[2415][4] != CASTLE_TOKEN
        or EXPECTED_BASE_GAPS[2416][0] != CASTLE_TOKEN
        or EXPECTED_BASE_GAPS[2418][:2] != (TARGET_FORCE_TOKEN, CASTLE_TOKEN)
        or PK_EN_CONTEXT[2414][1][1:4]
        != (SCHEME_TOKEN, CASTLE_TOKEN, DETECTOR_TOKEN)
    ):
        raise RuntimeError("segment 994 cross-language token direction drifted")
    if set(EXCLUDED_NONVISIBLE_COORDINATES) != {"15:2415:3"}:
        raise RuntimeError("segment 994 hidden LF coordinate drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(f"segment 994 project ellipsis pair drifted: {coordinate}")
    joined = "\n".join(translations.values())
    for required in (
        "천하통일",
        "간자",
        "보복",
        "조종",
        "공작",
        "조략",
        "우리 가문",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 994 required terminology drifted: {required}")
    for forbidden in ("당가", "가중", "스파이", "모략", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 994 forbidden wording retained: {forbidden}")
    if set(HISTORICAL_EVIDENCE_URLS) != {
        "間者", "調略", "意趣返し", "手玉に取る"
    }:
        raise RuntimeError("segment 994 historical evidence registry drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 994 visible decision count drifted")


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
        raise RuntimeError("segment 994 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 994 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B119_S994",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [2414],
                "base_pk_jp_gap_divergence_records": [
                    2411, 2412, 2413, 2414, 2415, 2416, 2418
                ],
                "base_pk_sc_tc_literal_divergence_records": [],
                "base_pk_sc_tc_gap_divergence_records": [2418],
                "pristine_current_gap_divergence_records": [],
                "excluded_nonvisible_coordinates": sorted(EXCLUDED_NONVISIBLE_COORDINATES),
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "candidate_sha256": PREVIOUS.PREVIOUS.candidate_sha256(
                    prepared, translations
                ),
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3)
                },
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
