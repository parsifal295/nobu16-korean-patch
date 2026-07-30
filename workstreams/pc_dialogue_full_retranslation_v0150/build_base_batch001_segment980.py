#!/usr/bin/env python3
"""Build Base authoring segment 980 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment979 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S980.private.v1.jsonl"
)
SEGMENT = 980
CASTLE_CONTEXT_TOKEN = "02463F"
TRANSLATIONS_BY_RECORD = {
    2260: (
        "중대사",
        ",",
        "이(가)\n독단으로 출진한 듯한 상태",
        "!\n원호를 위해 병사를 내",
        "인가?",
    ),
    2261: (
        "알겠습니다.",
        "\n출진 채비에 들어가겠습니다.",
    ),
    2262: (
        "어쩔 수 없는 일인 듯하옵니다\n그저 무운을 빌",
        "…",
    ),
    2263: (
        "우리",
        "아래에 군다이가 다스리는\n땅이",
        "\n제게 맡겨 주신다면",
        "인가?",
    ),
    2264: (
        "의 성하를 번영시키기 위해서라도\n영지를 넓히려는 뜻",
        "\n검토해",
    ),
    2265: (
        "나날이 우리 가문의 정세도 변하고",
        "\n맞지 않는 성하 방침을 둔 성이 없는지\n재검토하셔도",
        "고 여깁니다",
    ),
    2266: (
        "성하 방침을 명받은 지\n오래된 성도 존재",
        "\n다시 한번 검토하는 것은",
    ),
    2267: (
        "성의 내정은 성하 방침을 정해\n성주에게 위임하는 것도 가능한 것",
        "\n필요에 따라",
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
    2260: (
        "一大事",
        "、",
        "が\n独断で出陣したよう",
        "！\n援護のため、兵を出",
        "か？",
    ),
    2261: ("かしこま", "\n出陣の手配に移"),
    2262: ("致し方なきことかと\nせめて武運を祈", "…"),
    2263: (
        "我が",
        "下に郡代の治める\n地が",
        "\n私におまかせいただけ",
        "か？",
    ),
    2264: ("城下を栄えさせるためにも\n領地を広げたい", "\nご検討"),
    2265: (
        "日々当家の情勢も変わって",
        "\n合わない城下方針の城がないか\n見直されても",
        "かと",
    ),
    2266: (
        "城下方針を命じられてから\n長く経った城も見受けられ",
        "\n今一度見直されては",
    ),
    2267: (
        "城の内政は、城下方針を定めて\n城主に委任することも可能",
        "\n必要に応じて",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2260: (
        "",
        "01431A020000",
        "01431D000000",
        "01431A020000",
        "01437E040000",
        "050505",
    ),
    2261: ("", "014368020000", "01435A040000050505"),
    2262: ("", "01435A040000", "050505"),
    2263: (
        "",
        CASTLE_CONTEXT_TOKEN,
        "014352000000",
        "0143E0020000",
        "050505",
    ),
    2264: (
        CASTLE_CONTEXT_TOKEN,
        "014346030000",
        "014342010000050505",
    ),
    2265: ("", "0143B2000000", "01430C040000", "050505"),
    2266: (
        "",
        "01433C040000",
        "0143B0020000014356020000050505",
    ),
    2267: ("", "01431A020000", "0143B2030000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    2261: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    2260: (
        "",
        "014326020000",
        "01431D000000",
        "014326020000",
        "01438A040000",
        "050505",
    ),
    2261: ("", "014374020000", "014366040000050505"),
    2262: ("", "014366040000", "050505"),
    2263: (
        "",
        CASTLE_CONTEXT_TOKEN,
        "014352000000",
        "0143EC020000",
        "050505",
    ),
    2264: (
        CASTLE_CONTEXT_TOKEN,
        "014352030000",
        "014342010000050505",
    ),
    2265: ("", "0143B2000000", "014318040000", "050505"),
    2266: (
        "",
        "014348040000",
        "0143BC020000014362020000050505",
    ),
    2267: ("", "014326020000", "0143BE030000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2262:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2260): (
        ("大事不好！", "\n擅自出阵了！\n是否要出兵进行援护？"),
        ("", "01431D000000", "050505"),
    ),
    ("TC", 2260): (
        ("大事不好！", "\n擅自出陣了！\n是否要出兵進行援護？"),
        ("", "01431D000000", "050505"),
    ),
    ("SC", 2261): (("明白。\n这就准备出阵。",), ("", "050505")),
    ("TC", 2261): (("遵命！\n立刻準備出陣！",), ("", "050505")),
    ("SC", 2262): (
        ("虽然别无他法，\n但至少祝愿武运昌盛……",),
        ("", "050505"),
    ),
    ("TC", 2262): (("事出無奈。\n但求出師順利……",), ("", "050505")),
    ("SC", 2263): (
        ("我的", "下有郡代治理之地。\n由于并无太大压力，\n不如就交给我吧？"),
        ("", CASTLE_CONTEXT_TOKEN, "050505"),
    ),
    ("TC", 2263): (
        ("我的", "下有郡代治理之地。\n由於並無太大壓力，\n不如就交給我吧？"),
        ("", CASTLE_CONTEXT_TOKEN, "050505"),
    ),
    ("SC", 2264): (
        ("也是为了让", "城下更加繁荣，\n可否考虑下扩张领地呢？"),
        ("", CASTLE_CONTEXT_TOKEN, "050505"),
    ),
    ("TC", 2264): (
        ("也是為了讓", "城下更加繁榮，\n可否考慮下擴張領地呢？"),
        ("", CASTLE_CONTEXT_TOKEN, "050505"),
    ),
    ("SC", 2265): (
        ("本家的情况有所好转，\n应该重新考虑下\n有没有不符合城下方针的城。",),
        ("", "050505"),
    ),
    ("TC", 2265): (
        ("本家的情況有所好轉，\n應該重新考慮下\n有沒有不符合城下方針的城。",),
        ("", "050505"),
    ),
    ("SC", 2266): (
        ("自从下令城下方针，\n有的城已经经过很长一段时间了。\n现在重新考虑一下如何？ ",),
        ("", "050505"),
    ),
    ("TC", 2266): (
        ("自從下令城下方針，\n有的城已經經過很長一段時間了。\n現在重新考慮一下如何？ ",),
        ("", "050505"),
    ),
    ("SC", 2267): (
        ("城的内政也可以通过城下方针委任城主施行。\n如有需要便请下令。",),
        ("", "050505"),
    ),
    ("TC", 2267): (
        ("城的內政亦可制定城下方針后委任城主施行。\n請依需求下達命令。",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2260: (
        (
            "Urgent news! One of our officers has charged into battle without "
            "permission! Should we send soldiers to assist them?",
        ),
        ("", "050505"),
    ),
    2261: (
        ("Understood. We will begin preparations to march.",),
        ("", "050505"),
    ),
    2262: (
        ("It would seem the best I can do is wish for luck on the battlefield...",),
        ("", "050505"),
    ),
    2263: (
        (
            "The land around ",
            " requires the governance of a county representative. Will you allow "
            "me the responsibility?",
        ),
        ("", CASTLE_CONTEXT_TOKEN, "050505"),
    ),
    2264: (
        (
            "I want to expand our domain to bring further prosperity to the "
            "castle town of ",
            ". Will you consider it?",
        ),
        ("", CASTLE_CONTEXT_TOKEN, "050505"),
    ),
    2265: (
        (
            "Our situation has been changing over time. It might be a good idea "
            "to make certain all the castle town plans are still appropriate.",
        ),
        ("", "050505"),
    ),
    2266: (
        (
            "Some of our castles received their castle town plans quite a while "
            "ago. What do you say to taking another look at them?",
        ),
        ("", "050505"),
    ),
    2267: (
        (
            "It is possible to set the plan and delegate administration of a "
            "castle to the lord. Command as you see fit.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_C_pristine_base_pc_jp_authoritative_"
    "unauthorized_march_castle_town_policy_county_representative_and_"
    "delegated_castle_governance_with_explicit_base2260_2267_to_pk2291_"
    "2298_plus31_mapping_exact_base_pk_jp_sc_tc_literals_actual_pk_en_"
    "auxiliary_context_郡代_as_gundai_城下_as_seongha_城下方針_as_"
    "seongha_bangchim_当家_as_uri_gamun_ASCII_comma_2260_project_"
    "ellipsis_pair_current2261_gap_divergence_morphology_terminal_corpora_"
    "current_line_counts_and_protected_skeleton_preserved_runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    29: (
        "아버님",
        "어머님",
        "할아버님",
        "할머님",
        "숙부님",
        "숙모님",
        "님",
        "주군님",
        "주군",
        "도련님",
        "공주님",
        "그분",
        "그자",
        "쇼군님",
        "스님",
        "원숭이",
        "놈",
        "누님",
        "형님",
    ),
    82: ("있습니다", "있다", "있사옵니다", "입니다", "이옵니다"),
    178: ("있습니다", "있다", "있사옵니다"),
    322: ("주시오", "다오", "주소서"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    736: ("않습니다", "않는다"),
    838: ("인 것입니다", "인 것이다", "이니라"),
    946: (
        "명하여 주십시오",
        "명령해 다오",
        "명령해 주십시오",
        "명령을 내려 주소서",
        "명하여 주시게",
    ),
    1036: ("좋다",),
    1084: ("합니다", "다", "하옵니다"),
    1114: ("합시다", "하리라"),
    1150: ("합시다", "그렇군"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    29: EXPECTED_BASE_MORPHOLOGY_TERMINALS[29],
    82: EXPECTED_BASE_MORPHOLOGY_TERMINALS[82],
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    322: EXPECTED_BASE_MORPHOLOGY_TERMINALS[322],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    628: ("했습니다", "었다"),
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    748: EXPECTED_BASE_MORPHOLOGY_TERMINALS[736],
    850: EXPECTED_BASE_MORPHOLOGY_TERMINALS[838],
    958: EXPECTED_BASE_MORPHOLOGY_TERMINALS[946],
    1048: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1036],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
    1162: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1150],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 980 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 980 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != set(range(2260, 2268)):
        raise RuntimeError("segment 980 Base-to-PK gap divergence drifted")
    current_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    }
    if current_divergences != {2261}:
        raise RuntimeError("segment 980 pristine/current gap divergence drifted")
    if (
        EXPECTED_BASE_GAPS[2263][1] != CASTLE_CONTEXT_TOKEN
        or EXPECTED_BASE_GAPS[2264][0] != CASTLE_CONTEXT_TOKEN
    ):
        raise RuntimeError("segment 980 castle-context token direction drifted")
    if (
        raw_translations["15:2260:1"] != ","
        or "、" in "\n".join(translations.values())
    ):
        raise RuntimeError("segment 980 Japanese comma survived")
    expected_2260_combinations = {
        "중대사입니다",
        "중대사다",
        "중대사이니라",
        "중대사이오",
        "중대사이옵니다",
    }
    expected_2260_subject_combinations = {
        "이(가)\n독단으로 출진한 듯한 상태입니다",
        "이(가)\n독단으로 출진한 듯한 상태다",
        "이(가)\n독단으로 출진한 듯한 상태이니라",
        "이(가)\n독단으로 출진한 듯한 상태이오",
        "이(가)\n독단으로 출진한 듯한 상태이옵니다",
    }
    if (
        raw_translations["15:2260:0"] != "중대사"
        or {
            raw_translations["15:2260:0"] + terminal
            for terminal in EXPECTED_BASE_MORPHOLOGY_TERMINALS[538]
        }
        != expected_2260_combinations
        or {
            raw_translations["15:2260:0"] + terminal
            for terminal in EXPECTED_PK_MORPHOLOGY_TERMINALS[550]
        }
        != expected_2260_combinations
        or {
            raw_translations["15:2260:2"] + terminal
            for terminal in EXPECTED_BASE_MORPHOLOGY_TERMINALS[538]
        }
        != expected_2260_subject_combinations
        or {
            raw_translations["15:2260:2"] + terminal
            for terminal in EXPECTED_PK_MORPHOLOGY_TERMINALS[550]
        }
        != expected_2260_subject_combinations
    ):
        raise RuntimeError("segment 980 root538/550 noun-terminal combinations drifted")
    if (
        SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[2260][1]) != (538,)
        or SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[2260][2]) != (29,)
        or SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[2260][3]) != (538,)
        or SUPPORT.morphology_operands(EXPECTED_PK_JP_GAPS[2260][1]) != (550,)
        or SUPPORT.morphology_operands(EXPECTED_PK_JP_GAPS[2260][2]) != (29,)
        or SUPPORT.morphology_operands(EXPECTED_PK_JP_GAPS[2260][3]) != (550,)
        or raw_translations["15:2260:1"] != ","
        or not raw_translations["15:2260:2"].startswith("이(가)\n")
    ):
        raise RuntimeError("segment 980 root29 dynamic-person boundary drifted")
    if (
        raw_translations["15:2263:0"] != "우리"
        or "명받은 지" not in raw_translations["15:2266:0"]
    ):
        raise RuntimeError("segment 980 possessive or passive-voice meaning drifted")
    if (
        EXPECTED_BASE_GAPS[2264][0] != CASTLE_CONTEXT_TOKEN
        or not raw_translations["15:2264:0"].startswith("의 성하를 ")
    ):
        raise RuntimeError("segment 980 leading castle-token possessive drifted")
    joined = "\n".join(translations.values())
    for required in ("군다이", "성하", "성하 방침", "우리 가문", "출진", "무운"):
        if required not in joined:
            raise RuntimeError(f"segment 980 terminology drifted: {required}")
    for forbidden in ("군대", "당가", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 980 forbidden wording retained: {forbidden}")
    if (
        raw_translations["15:2262:1"].count("…") != 1
        or translations["15:2262:1"].count("…") != 2
    ):
        raise RuntimeError("segment 980 ellipsis pair drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 980 visible decision count drifted")


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
        raise RuntimeError("segment 980 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 980 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S980",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": list(range(2260, 2268)),
                "pristine_current_gap_divergence_records": [2261],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
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
