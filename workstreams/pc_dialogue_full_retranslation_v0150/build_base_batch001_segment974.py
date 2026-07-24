#!/usr/bin/env python3
"""Build Base authoring segment 974 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment973 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S974.private.v1.jsonl"
)
SEGMENT = 974
PERSON_TOKEN = "024635"
TRANSLATIONS_BY_RECORD = {
    2193: ("채택해 주시다니 감사하옵니다!\n곧바로 착수",),
    2194: (
        "알겠습니다",
        "\n기대 이상의 성과를",
        "거두어 보이겠습니다",
    ),
    2195: (
        "미력이나마 온 힘을 다하겠습니다",
        "\n좋은 소식을 기다려 주십시오",
    ),
    2196: (
        "모든 일은 이 원숭이에게 맡겨 주시옵소서!\n"
        "금세 길보를 가져오겠사옵니다",
    ),
    2197: (
        "고메 고로자라는 별호답게\n"
        "어떠한 요청에도 응해 보이겠습니다",
    ),
    2198: (
        "에게 맡겨 주시오\n"
        "아타고 권현에 맹세코, 이 소임을 완수하겠소",
    ),
    2199: (
        "이 소임은",
        "에게 맡겨 주시오\n무슨 수를 써서라도 이루어 드리",
    ),
    2200: (
        "일의 자세한 사정은",
        "에게 맡겨 주시오\n예리한 지략을 보여 드리",
    ),
    2201: (
        "이제야말로 효웅의 솜씨를 보일 때…\n",
        "의 술책 앞에 떨지어다!",
    ),
    2202: (
        "이 미약한 목숨을 걸고\n"
        "제가 지닌 모든 계책을 다 쓰겠습니다",
    ),
    2203: (
        "이번 일은,",
        "도 잠시 생각할 시간이 필요하오…\n"
        "좋은 소식을 조금만 더 기다려",
    ),
    2204: (
        "소임을 받들겠습니다",
        "\n충실한 종으로서 맡은 바를 다하겠습니다",
    ),
    2205: (
        "병학을 수련한 성과를 여기서 보여 드리겠습니다",
        "\n곧 좋은 소식을 전해 올리겠습니다",
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
    2193: ("採り上げていただけようとは！\nすぐに着手",),
    2194: ("承知いたし", "\n成果に", "期待"),
    2195: ("微力を尽く", "\n朗報を"),
    2196: (
        "万事このサルめにお任せあれ！\n"
        "たちまちのうちに吉報お届けに参りますぞ",
    ),
    2197: ("米五郎左の二つ名が如く\n如何様なる求めにも応えてみせ",),
    2198: ("にお任せくだされ\n愛宕権現に誓い、この勤め果しまする",),
    2199: ("この勤めは", "にお任せを\n如何なる手を用いても叶えて進ぜ"),
    2200: ("事の仔細、", "にお任せあれ\n知略の冴えをご覧に入れ"),
    2201: ("ここは梟雄が腕の見せどころ…\n", "が術策に慄き召されよ！"),
    2202: ("我が薄弱なる身命を賭して\n持ちうる策の限りを尽く",),
    2203: ("この", "、思案には暫し時間要したく…\n吉報を今暫しお待ち"),
    2204: ("お役目承", "\n忠実なる僕として任を遂行"),
    2205: ("兵学修行の成果、ここにお見せ", "\n直ぐに吉報お届けに上が"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2193: ("", "0143940000000143fc010000050505"),
    2194: ("", "014314020000", "01438a040000", "014396010000050505"),
    2195: ("", "0143b4010000", "01438e030000050505"),
    2196: ("", "050505"),
    2197: ("", "01431e040000050505"),
    2198: ("014301000000", "050505"),
    2199: ("", PERSON_TOKEN, "01431e040000050505"),
    2200: ("", PERSON_TOKEN, "01431e040000050505"),
    2201: ("", PERSON_TOKEN, "050505"),
    2202: ("", "01437e040000050505"),
    2203: ("", "014301000000", "014396010000050505"),
    2204: ("", "014368020000", "014394000000050505"),
    2205: ("", "01438e000000", "01435a040000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    2194: ("", "", "", "050505"),
    2195: ("", "", "050505"),
    2197: ("", "050505"),
    2202: ("", "050505"),
    2204: ("", "", "050505"),
    2205: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2193: ("", "014394000000014302020000050505"),
    2194: ("", "01431a020000", "014396040000", "01439c010000050505"),
    2195: ("", "0143ba010000", "01439a030000050505"),
    2197: ("", "01432a040000050505"),
    2199: ("", PERSON_TOKEN, "01432a040000050505"),
    2200: ("", PERSON_TOKEN, "01432a040000050505"),
    2202: ("", "01438a040000050505"),
    2203: ("", "014301000000", "01439c010000050505"),
    2204: ("", "014374020000", "014394000000050505"),
    2205: ("", "01438e000000", "014366040000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2201:0", "15:2203:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2193): (("不胜感激。\n那么，就立即执行吧。",), ("", "050505")),
    ("TC", 2193): (("真是感激不盡！\n那麼就立刻進行吧！",), ("", "050505")),
    ("SC", 2194): (("就请期待成果吧。",), ("", "050505")),
    ("TC", 2194): (("期待成果吧。",), ("", "050505")),
    ("SC", 2195): (("我会尽自己的微薄之力，\n带来好消息。",), ("", "050505")),
    ("TC", 2195): (("我會盡力的，\n等好消息吧。",), ("", "050505")),
    ("SC", 2196): (
        ("全都交给我这只猴子吧！\n马上就给您送上捷报。",),
        ("", "050505"),
    ),
    ("TC", 2196): (
        ("全部交給我這隻猴子吧！\n很快就會為您送上好消息！",),
        ("", "050505"),
    ),
    ("SC", 2197): (
        ("正如我米五郎左的异名，\n不论什么要求，我都在所不辞。",),
        ("", "050505"),
    ),
    ("TC", 2197): (
        ("正如米五郎左的異名，\n不論什麼要求，我都在所不辭。",),
        ("", "050505"),
    ),
    ("SC", 2198): (
        ("交给", "吧。\n向爱宕权现发誓，绝不负所托。"),
        ("", "014301000000", "050505"),
    ),
    ("TC", 2198): (
        ("放心交給", "吧！\n向愛宕權現發誓，絕對不負所托。"),
        ("", "014301000000", "050505"),
    ),
    ("SC", 2199): (
        ("这项任务就交给我", "吧！\n无论使用任何手段我都要完成。"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("TC", 2199): (
        ("這工作就交給我", "吧！\n我一定會想盡辦法達成使命。"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("SC", 2200): (
        ("全盘交给我", "吧。\n是时候展现我·巧妙的计谋了。"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("TC", 2200): (
        ("就全盤交給我", "吧。\n是時候一展我在計謀上的長才了。"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("SC", 2201): (
        ("是时候展现枭雄的手段了…\n让", "尝尝谋略的恐怖吧！"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("TC", 2201): (
        ("是時候展現梟雄的手腕了……\n在", "的謀術前顫抖吧！"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("SC", 2202): (
        ("就算赌上我的性命，\n我会使出所有计策完成使命。",),
        ("", "050505"),
    ),
    ("TC", 2202): (
        ("就算賭上這身羸弱的身軀，\n我也會用盡所有計策達成使命。",),
        ("", "050505"),
    ),
    ("SC", 2203): (
        ("需要一些时间考虑…\n请先耐心等待捷报。",),
        ("014301000000", "050505"),
    ),
    ("TC", 2203): (
        ("需要些時間來出謀劃策……\n還請靜候佳音。",),
        ("014301000000", "050505"),
    ),
    ("SC", 2204): (
        ("明白我的职责了。\n我会尽忠尽责来执行任务的。",),
        ("", "050505"),
    ),
    ("TC", 2204): (("職責內容我了解了。\n我會忠實地履行的。",), ("", "050505")),
    ("SC", 2205): (
        ("在此展示我修行兵学的成果吧。\n马上就给您呈上捷报。",),
        ("", "050505"),
    ),
    ("TC", 2205): (
        ("就讓我展現學習兵法的成果吧。\n敬請期待捷報。",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2193: (
        ("My thanks for assigning this task. I will begin work at once!",),
        ("", "050505"),
    ),
    2194: (
        ("Understood. My results will exceed your expectations.",),
        ("", "050505"),
    ),
    2195: (
        ("I will put in my best effort. Expect to hear good news.",),
        ("", "050505"),
    ),
    2196: (
        (
            "You can count on this little runt to get the job done! "
            "I will return with good news!",
        ),
        ("", "050505"),
    ),
    2197: (
        (
            "Just like Gorªza the Indispensable, no matter what the task, "
            "I will see it completed!",
        ),
        ("", "050505"),
    ),
    2198: (
        ("Leave it to me. I swear to Atago Gongen, I will fulfill my duty.",),
        ("", "050505"),
    ),
    2199: (
        ("You just leave this to ", ". IÖll do whatever it takes to get the job done."),
        ("", PERSON_TOKEN, "050505"),
    ),
    2200: (
        ("Leave the matter to me, ", ". Observe the work of my sharp intellect."),
        ("", PERSON_TOKEN, "050505"),
    ),
    2201: (
        (
            "The ringleader shall demonstrate their true skill! "
            "Feast your eyes on the ferocious tactics of ",
            "!",
        ),
        ("", PERSON_TOKEN, "050505"),
    ),
    2202: (
        ("I shall expend my worthless life to see this task fulfilled.",),
        ("", "050505"),
    ),
    2203: (
        (
            "I must give this some thought... But you will surely be pleased "
            "by what you will soon hear.",
        ),
        ("", "050505"),
    ),
    2204: (
        ("I understand your orders. Your loyal subject will get the job done.",),
        ("", "050505"),
    ),
    2205: (
        (
            "I will demonstrate the results of all my training. "
            "Expect to hear good news before long!",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_A_pristine_base_pc_jp_authoritative_"
    "assignment_acceptance_persona_and_stratagem_responses_with_explicit_"
    "base2193_2205_to_pk2223_2235_mapping_exact_base_pk_jp_sc_tc_and_pk_"
    "en_auxiliary_context_米五郎左_as_gome_goroza_niwa_nagahide_nickname_"
    "愛宕権現_as_atago_gwonhyeon_梟雄_as_hyounge_and_事の仔細_as_detailed_"
    "circumstances_慄き召されよ_without_death_meaning_person_token_"
    "direction_current_korean_morphology_terminal_corpora_all_pristine_"
    "current_and_base_pk_opcode_divergences_recorded_project_ellipsis_"
    "current_line_counts_and_protected_skeleton_preserved_mixed_static_and_"
    "runtime_pending_classification"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    1: ("소승", "나", "저", "소인", "이 몸"),
    148: ("하겠습니다", "하겠다", "하자"),
    406: ("주십시오", "해 다오", "저것", "주시오"),
    508: ("", "다"),
    1054: ("합시다", "듯"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    1: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1],
    142: ("하겠습니다", "하다", "하겠사옵니다"),
    148: EXPECTED_BASE_MORPHOLOGY_TERMINALS[148],
    412: EXPECTED_BASE_MORPHOLOGY_TERMINALS[406],
    442: ("합니다", "하", "하옵니다"),
    514: EXPECTED_BASE_MORPHOLOGY_TERMINALS[508],
    538: ("했습니다", "다"),
    628: ("했습니다", "었다"),
    922: (
        "기다려 주십시오",
        "기다리시오",
        "기다리거라",
        "기다려 주시기를",
        "기다려 주시게",
    ),
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1126: ("합시다", "하리라"),
    1162: ("합시다", "그렇군"),
    1174: ("고", ""),
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 974 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 974 Base-to-PK JP literal drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    } != {2193, 2194, 2195, 2197, 2199, 2200, 2202, 2203, 2204, 2205}:
        raise RuntimeError("segment 974 Base-to-PK gap divergence drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    } != {2194, 2195, 2197, 2202, 2204, 2205}:
        raise RuntimeError("segment 974 pristine/current gap divergence drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id][1] != PERSON_TOKEN
        for record_id in (2199, 2200, 2201)
    ):
        raise RuntimeError("segment 974 person-token direction drifted")
    if "米五郎左" not in "".join(EXPECTED_BASE_JP[2197]):
        raise RuntimeError("segment 974 米五郎左 source guard drifted")
    joined = "\n".join(translations.values())
    for required in (
        "고메 고로자",
        "아타고 권현",
        "효웅",
        "자세한 사정",
        "떨지어다",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 974 historical or semantic terminology drifted: {required}"
            )
    for forbidden in ("고메고로자", "모리 요시나리", "떨며 죽", "자초지종"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 974 forbidden wording retained: {forbidden}"
            )
    if raw_translations["15:2197:0"].count("고메 고로자") != 1:
        raise RuntimeError("segment 974 米五郎左 translation drifted")
    if raw_translations["15:2201:1"] != "의 술책 앞에 떨지어다!":
        raise RuntimeError("segment 974 慄き召されよ meaning drifted")
    for speaker in EXPECTED_BASE_MORPHOLOGY_TERMINALS[1]:
        assembled = (
            raw_translations["15:2203:0"]
            + speaker
            + raw_translations["15:2203:1"]
        )
        if not assembled.startswith(
            f"이번 일은,{speaker}도 잠시 생각할 시간이 필요하오…\n"
        ):
            raise RuntimeError(
                f"segment 974 Base2203 speaker branch assembly drifted: {speaker}"
            )
    if any(
        punctuation in raw_translations["15:2203:0"]
        + raw_translations["15:2203:1"]
        for punctuation in ("(", ")")
    ):
        raise RuntimeError("segment 974 Base2203 parenthetical speaker retained")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 974 project ellipsis normalization drifted: {coordinate}"
            )
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 974 visible decision count drifted")


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
    for row in rows:
        if row["coordinate"] == "15:2196:0":
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 974 validated count drifted")
    if any(
        (
            row["scope_classification"],
            row["runtime_review"],
        )
        != (
            ("retranslated", "not_required")
            if row["coordinate"] == "15:2196:0"
            else ("runtime_fragment_pending", "pending")
        )
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 974 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S974",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": 21,
                "retranslated_static": 1,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2193,
                    2194,
                    2195,
                    2197,
                    2199,
                    2200,
                    2202,
                    2203,
                    2204,
                    2205,
                ],
                "pristine_current_gap_divergence_records": [
                    2194,
                    2195,
                    2197,
                    2202,
                    2204,
                    2205,
                ],
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
