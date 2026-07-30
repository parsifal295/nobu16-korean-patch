#!/usr/bin/env python3
"""Build Base authoring segment 970 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment969 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S970.private.v1.jsonl"
)
SEGMENT = 970
FORCE_TOKEN = PREVIOUS.FORCE_TOKEN
CASTLE_TOKEN = PREVIOUS.CASTLE_TOKEN
TRANSLATIONS_BY_RECORD = {
    2150: (
        "에서 소동이 있었던 모양이라\n상세한 사정을 조사",
        "만\n그 내용을 확인",
        "?",
    ),
    2151: (
        "에서 사건이 일어난 듯하오\n자세한 이야기를 듣고 왔으니\n"
        "아뢰겠나이다!",
    ),
    2152: (
        "소문에 따르면, ",
        "에서 무슨\n사건이 있었던 모양입니다\n듣자 하니…",
    ),
    2153: (
        "풍문에 따르면, ",
        "에서 일어난 사건의 소식이\n어디선가 새어 나왔다 하옵니다\n"
        "제가 들은 바로는…",
    ),
    2154: (
        "에서 사건이 일어났다 하오…\n풍문",
        "만,\n보고",
        "?",
    ),
    2155: (
        "에서 풍문을 입수했소\n듣자 하니, 이런 이야기가\n"
        "있었다는 듯하오…",
    ),
    2156: (
        "보물을 다루는 상인이 내방",
        "\n장수들의 충근을 포상하는 데\n명품을 쓰는 것이 상책",
    ),
    2157: (
        "일품을 다루는 상인이 내방",
        "\n수집해도 좋고, 하사해도 좋으니\n",
        "도 구입을 검토해 보시",
        "겠습니까?",
    ),
    2158: (
        "찾아온 상인이 일품을 판다는 소식에\n장수들이 기대",
        "\n",
        "도 물품을 살펴보시겠습니까?",
    ),
    2159: (
        "에서 새 시설을 건설할 수 있게 되었습니다\n"
        "성하 마을 명령으로 이동하시겠습니까?",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:2158:1": "\n"}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2150: ("で騒ぎがあった様子\n詳細を調べて参", "が\nお聞きにな", "か？"),
    2151: ("で事件が起きた様子\n詳しい話を聞いてきたゆえ、\n言上つかまつらん！",),
    2152: ("噂では、", "で何やら\n出来事があったようなのです\nなんでも…"),
    2153: ("風聞にて", "の事件が\n何やら漏れ伝わっているとか\n私が聞いた話によれば…"),
    2154: ("で事件が起きたとか…\n風の噂では", "が、\nお話し", "か？"),
    2155: ("から風聞を入手いたした\nなんでも、このような話が\nあったらしく…",),
    2156: ("宝物を扱う商人が来訪してお", "\n諸将の忠勤を賞するのに\n名品をもってしてはいかが"),
    2157: (
        "逸品を扱う商人が訪れてお",
        "\n収集するもよし、下賜するもよし\n",
        "も購入を",
        "検討されては？",
    ),
    2158: (
        "来訪した商人が逸品を売っていると\n諸将が色めきたってお",
        "\n",
        "もご覧なさってはいかが？",
    ),
    2159: ("で新しく施設が建設可能になりました\n城下町コマンドに遷移しますか？",),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2150: (FORCE_TOKEN, "014368020000", "014336040000", "050505"),
    2151: (FORCE_TOKEN, "050505"),
    2152: ("", FORCE_TOKEN, "050505"),
    2153: ("", FORCE_TOKEN, "050505"),
    2154: (FORCE_TOKEN, "014378010000", "014394000000", "050505"),
    2155: (FORCE_TOKEN, "050505"),
    2156: ("", "014336040000", "014356020000050505"),
    2157: (
        "",
        "014336040000",
        "014308000000",
        "01438A040000",
        "050505",
    ),
    2158: ("", "014336040000", "014308000000", "050505"),
    2159: (CASTLE_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2150: (FORCE_TOKEN, "014374020000", "014342040000", "050505"),
    2156: ("", "014342040000", "014362020000050505"),
    2157: (
        "",
        "014342040000",
        "014308000000",
        "014396040000",
        "050505",
    ),
    2158: ("", "014342040000", "014308000000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2152:1",
    "15:2153:1",
    "15:2154:0",
    "15:2155:0",
}
SHARED_AUXILIARY = {
    ("SC", 2150): (
        ("关于在", "发生的事件，\n已经搞清楚详情了。\n是否要听一下呢？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2150): (
        ("關於在", "發生的事件，\n已經搞清楚詳情了。\n是否要聽一下呢？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("SC", 2152): (
        ("据传闻，\n好像在", "发生了什么事情。\n什么都……"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2152): (
        ("聽說在", "似乎發生了\n什麼事。\n聽說是……"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("SC", 2154): (
        ("在", "发生的事……\n虽然只是传言，\n可否容臣禀告？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2154): (
        ("在", "發生的事……\n雖然只是傳言，\n可否容臣稟告？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("SC", 2156): (
        ("据说商人各自带来的名品中，\n有些不易到手的逸品……\n可否考虑买进？",),
        ("", "050505"),
    ),
    ("TC", 2156): (
        ("據說商人各自帶來的名品中，\n有些不易到手的逸品……\n可否考慮買進？",),
        ("", "050505"),
    ),
    ("SC", 2157): (
        ("据说这次是从商人那儿买进\n不为人知的逸品的好机会……\n不买也行，先看看再说吧。",),
        ("", "050505"),
    ),
    ("TC", 2157): (
        ("據說這次是從商人那兒買進\n不為人知的逸品的好機會……\n不買也行，先看看再說吧。",),
        ("", "050505"),
    ),
    ("SC", 2158): (
        ("据说到城里来的\n商人带来了珍品，\n说实话，真的非买不可。",),
        ("", "050505"),
    ),
    ("TC", 2158): (
        ("據說到城裡來的\n商人帶來了珍品，\n說實話，真的非買不可。",),
        ("", "050505"),
    ),
    ("SC", 2159): (
        ("已能够在", "新建设施了。\n是否跳转至城下町命令？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2159): (
        ("已可於", "建設新設施。\n要遷移至城下町指令嗎？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2150: (
        (
            "I looked into the apparent disturbance with the ",
            ". Would you like to hear what IÖve learned?",
        ),
        ("", FORCE_TOKEN, "050505"),
    ),
    2154: (
        (
            "IÖve heard tales about an incident concerning the ",
            ". Would you like to hear?",
        ),
        ("", FORCE_TOKEN, "050505"),
    ),
    2156: (
        (
            "A merchant who deals in treasures has made an appearance. "
            "What do you think about procuring some gifts to reward the "
            "officersÖ loyalty?",
        ),
        ("", "050505"),
    ),
    2157: (
        (
            "A merchant has come bearing some very valuable items. "
            "Whether as items for your own collection or as gifts, "
            "are you interested in making a purchase?",
        ),
        ("", "050505"),
    ),
    2158: (
        (
            "A merchant has arrived selling some valuable items that have "
            "caught the eyes of our officers. Would you like to peruse "
            "their wares as well?",
        ),
        ("", "050505"),
    ),
    2159: (
        (
            "A new facility has become available to add at ",
            ". Shall we move to castle town command?",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B116_B_pristine_base_pc_jp_authoritative_"
    "incident_rumor_treasure_merchant_and_new_facility_advice_with_"
    "explicit_base2150_2159_to_pk2180_2189_mapping_exact_base_pk_jp_sc_"
    "tc_and_actual_pk_en_auxiliary_context_dynamic_force_castle_and_"
    "honorific_tokens_direction_fubun_term_tenkin_reward_meaning_shinobi_"
    "register_and_seongha_maeul_spacing_current_korean_morphology_terminal_"
    "corpora_base_pk_opcode_divergences_recorded_hidden_lf_excluded_"
    "project_ellipsis_pairs_current_line_counts_and_protected_skeleton_"
    "preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    8: PREVIOUS.EXPECTED_BASE_MORPHOLOGY_TERMINALS[8],
    148: PREVIOUS.EXPECTED_BASE_MORPHOLOGY_TERMINALS[148],
    376: ("입니다", "있소", "있다"),
    598: ("이겠지요", "이리라", "이겠지"),
    616: ("했습니다", "었다"),
    1078: PREVIOUS.EXPECTED_BASE_MORPHOLOGY_TERMINALS[1078],
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    8: PREVIOUS.EXPECTED_PK_MORPHOLOGY_TERMINALS[8],
    148: PREVIOUS.EXPECTED_PK_MORPHOLOGY_TERMINALS[148],
    376: EXPECTED_BASE_MORPHOLOGY_TERMINALS[376],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    1090: PREVIOUS.EXPECTED_PK_MORPHOLOGY_TERMINALS[1090],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 970 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 970 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2150, 2156, 2157, 2158}:
        raise RuntimeError("segment 970 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 970 pristine/current gap drifted")
    if any(
        PREVIOUS.ACTION_TOKEN in gap
        for gaps in EXPECTED_BASE_GAPS.values()
        for gap in gaps
    ):
        raise RuntimeError("segment 970 unexpected action token retained")
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:2158:1": "\n"}:
        raise RuntimeError("segment 970 hidden LF exclusion drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 970 project ellipsis pair drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "풍문",
        "소문",
        "충근을 포상",
        "하사",
        "성하 마을",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 970 required meaning drifted: {required}")
    for forbidden in ("상찬", "성하마을", "닌자", "。"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 970 forbidden wording retained: {forbidden}"
            )
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 970 visible decision count drifted")


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
        skip_records={2158},
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
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 970 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 970 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S970",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2150, 2156, 2157, 2158],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
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
