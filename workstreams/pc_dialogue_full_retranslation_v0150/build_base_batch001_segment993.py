#!/usr/bin/env python3
"""Build Base authoring segment 993 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment992 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S993.private.v1.jsonl"
)
SEGMENT = 993
GOAL_NUMBER_TOKEN = PREVIOUS.GOAL_NUMBER_TOKEN
MERIT_NUMBER_TOKEN = "0232"
ACHIEVEMENT_REWARD_FRAGMENT = PREVIOUS.ACHIEVEMENT_REWARD_FRAGMENT
TRANSLATIONS_BY_RECORD: dict[int, tuple[str | None, ...]] = {
    2401: (
        "성하의 시설 수가 목표치인",
        "개를 초과",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2402: (
        "영내 석고가 목표치를 초과",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2403: (
        "영내 상업 수준이 목표치를 초과",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2404: (
        "목표 횟수만큼 공략 목표를 제압",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2405: (
        "목표 횟수만큼 합전에서 승리",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2406: (
        "마침내 목표를 달성",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2407: (
        "세력 목표를 제안한 무장",
        "명에게\n훈공",
        "을(를) 수여했습니다",
    ),
    2408: (
        "목표를 제안한 보람이 있군\n앞으로 더욱 힘써",
    ),
    2409: (
        "더 큰 발전과 가신단의 기강을 다잡기 위해\n우선 당면한 목표를 고안",
        None,
        "의 승인을 받는 대로 가신단에 전파",
    ),
    2410: (
        "요즘 여러 무장이 타성에 젖어\n움직임이 둔해진 듯",
        "\n기강을 다잡기 위해 단기 목표를 고안",
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
    2401: (
        "城下の施設数が目標の",
        "を上回",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2402: (
        "領国の石高が目標を上回",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2403: (
        "領国の商業が目標を上回",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2404: (
        "目標回数、攻略目標を制圧せしめ",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2405: (
        "目標回数、合戦にて勝利を飾れ",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2406: (
        "ついに目標を達成し",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2407: (
        "勢力目標を提案した武将",
        "名に\n勲功",
        "が与えられました",
    ),
    2408: ("目標を提案した甲斐があるというもの\n今後、一層励",),
    2409: (
        "一層の発展と家中の引き締めをはかるべく\nさしあたっての目標を考案し",
        "\n",
        "の承認次第、家中に伝え",
    ),
    2410: (
        "昨今、諸将の動きに慣れが出て\n動きが鈍く見受けられ",
        "\n引き締めのため、短期目標を考案し",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    2407: (
        "目標を提案した武将",
        "名に\n勲功",
        "が与えられました",
    ),
}
EXPECTED_BASE_GAPS = {
    2401: ("", GOAL_NUMBER_TOKEN, "014368020000", "0143CC010000050505"),
    2402: ("", "014368020000", "0143CC010000050505"),
    2403: ("", "014368020000", "0143CC010000050505"),
    2404: ("", "014314020000", "0143CC010000050505"),
    2405: ("", "014314020000", "0143CC010000050505"),
    2406: ("", "014314020000", "0143CC010000050505"),
    2407: ("", GOAL_NUMBER_TOKEN, MERIT_NUMBER_TOKEN, "050505"),
    2408: ("", "0143C4030000050505"),
    2409: ("", "014314020000", "014308000000", "01431E040000050505"),
    2410: ("", "01433C040000", "014314020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2401: ("", GOAL_NUMBER_TOKEN, "014374020000", "0143D2010000050505"),
    2402: ("", "014374020000", "0143D2010000050505"),
    2403: ("", "014374020000", "0143D2010000050505"),
    2404: ("", "01431A020000", "0143D2010000050505"),
    2405: ("", "01431A020000", "0143D2010000050505"),
    2406: ("", "01431A020000", "0143D2010000050505"),
    2407: EXPECTED_BASE_GAPS[2407],
    2408: ("", "0143D0030000050505"),
    2409: ("", "01431A020000", "014308000000", "01432A040000050505"),
    2410: ("", "014348040000", "01431A020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {"15:2409:1": "\n"}
SC_CONTEXT = {
    2401: (("因城下的设施数超过目标的", "座，\n提议此目标者的功绩不小，\n故将给予特别的奖励。"), ("", GOAL_NUMBER_TOKEN, "050505")),
    2402: (("因领国的石高超越了目标，\n提议此目标者的功绩不小，\n故将给予特别的奖励。",), ("", "050505")),
    2403: (("因领国的商业超越了目标，\n提议此目标者的功绩不小，\n故将给予特别的奖励。",), ("", "050505")),
    2404: (("因压制攻略目标的次数达到目标，\n提议此目标者的功绩不小，\n故将给予特别的奖励。",), ("", "050505")),
    2405: (("因于会战的获胜次数达到目标，\n提议此目标者的功绩不小，\n故将给予特别的奖励。",), ("", "050505")),
    2406: (("终于达成目标了，\n提议此目标者的功绩不小，\n故将给予特别的奖励。",), ("", "050505")),
    2407: (("提议势力目标的武将", "名\n获赐了功勋", "。"), ("", GOAL_NUMBER_TOKEN, MERIT_NUMBER_TOKEN, "050505")),
    2408: (("不枉我提议该目标的心意，\n今后将更加努力。",), ("", "050505")),
    2409: (("为了进一步发展并团结家中，\n已规划出当前的目标。\n", "同意的话，便向家臣传达。"), ("", "014308000000", "050505")),
    2410: (("近来，诸将领行事松散懈怠，漫不经心。\n建议设定短期目标，\n以提高众人的戒备心。",), ("", "050505")),
}
TC_CONTEXT = {
    2401: (("因城下的設施數超過目標的", "座，\n提議此目標者的功績不小，\n故將給予特別的獎勵。"), ("", GOAL_NUMBER_TOKEN, "050505")),
    2402: (("因領國的石高超越了目標，\n提議此目標者的功績不小，\n故將給予特別的獎勵。",), ("", "050505")),
    2403: (("因領國的商業超越了目標，\n提議此目標者的功績不小，\n故將給予特別的獎勵。",), ("", "050505")),
    2404: (("因壓制攻略目標的次數達到目標，\n提議此目標者的功績不小，\n故將給予特別的獎勵。",), ("", "050505")),
    2405: (("因於會戰的獲勝次數達到目標，\n提議此目標者的功績不小，\n故將給予特別的獎勵。",), ("", "050505")),
    2406: (("終於達成目標了，\n提議此目標者的功績不小，\n故將給予特別的獎勵。",), ("", "050505")),
    2407: (("提議勢力目標的武將", "名\n獲賜了功勳", "。"), ("", GOAL_NUMBER_TOKEN, MERIT_NUMBER_TOKEN, "050505")),
    2408: (("不枉我提議該目標的心意，\n今後將更加努力。",), ("", "050505")),
    2409: (("為了進一步發展與家中團結，\n我已規劃出當前的目標。\n", "同意後就會立刻向家中傳遞。"), ("", "014308000000", "050505")),
    2410: (("近來，諸將領行事鬆散懈怠，漫不經心。\n建議設定短期目標，\n以提高眾人的戒備心。",), ("", "050505")),
}
PK_EN_CONTEXT = {
    2401: (("We have exceeded our goal of ", " castle town facilities. Those who proposed the goal should be well rewarded."), ("", GOAL_NUMBER_TOKEN, "050505")),
    2402: (("We have exceeded our territorial crop production goals. Those who proposed the goal should be well rewarded.",), ("", "050505")),
    2403: (("We have exceeded our territorial commerce goals. Those who proposed the goal should be well rewarded.",), ("", "050505")),
    2404: (("WeÖve occupied our target number of capture targets. Those who proposed the goal should be well rewarded.",), ("", "050505")),
    2405: (("WeÖve achieved our target number of battle victories. Those who proposed the goal should be well rewarded.",), ("", "050505")),
    2406: (("Our goal has been attained. Those who proposed the goal should be well rewarded.",), ("", "050505")),
    2407: (("The ", " officer(s) who suggested the target received ", " honor."), ("", GOAL_NUMBER_TOKEN, MERIT_NUMBER_TOKEN, "050505")),
    2408: (("Proposing the goal has borne fruit, it would seem. Henceforth, I shall endeavor to work even harder.",), ("", "050505")),
    2409: (("IÖve developed a provisional target to further improve our clan. If you approve, I will share it with the clan members.",), ("", "050505")),
    2410: (("Recently, the officers have grown too complacent in their routines. IÖve thought of a short-term goal to whip everyone back into shape.",), ("", "050505")),
}
SHARED_AUXILIARY = {
    **{("SC", record_id): context for record_id, context in SC_CONTEXT.items()},
    **{("TC", record_id): context for record_id, context in TC_CONTEXT.items()},
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_CONTEXT,
)
AUXILIARY_OVERRIDES[("pk", "SC", 2407)] = (
    ("提议目标的武将", "名\n获赐了功勋", "。"),
    ("", GOAL_NUMBER_TOKEN, MERIT_NUMBER_TOKEN, "050505"),
)
AUXILIARY_OVERRIDES[("pk", "TC", 2407)] = (
    ("提議目標的武將", "名\n獲賜了功勳", "。"),
    ("", GOAL_NUMBER_TOKEN, MERIT_NUMBER_TOKEN, "050505"),
)
HISTORICAL_EVIDENCE_URLS = {
    "家中": "https://kotobank.jp/word/%E5%AE%B6%E4%B8%AD-45092",
    "勲功": "https://kotobank.jp/word/%E5%8B%B2%E5%8A%9F-487655",
    "合戦": "https://kotobank.jp/word/%E5%90%88%E6%88%A6-464384",
}
BASIS = (
    "review_queue_base_msggame_B119_A_pristine_base_pc_jp_authoritative_"
    "goal_achievement_rewards_merit_award_and_short_term_goal_counsel_"
    "with_explicit_base2401_2410_to_pk2432_2441_plus31_mapping_record2407_"
    "base_pk_jp_sc_tc_literal_divergence_exact_auxiliary_context_goal_and_"
    "merit_number_token_direction_cross_segment_reward_fragment_identity_"
    "hidden2409_lf_actual_morphology_terminal_corpora_current_line_counts_"
    "protected_skeleton_dictionary_evidence_static2407_and_runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    8: (
        "아버님", "어머님", "할아버님", "할머님", "숙부님", "숙모님",
        "그대", "너", "주군님", "주군", "도련님", "공주님", "쇼군님",
        "스님", "네놈", "귀하", "귀공", "원숭이", "놈", "이놈", "누님", "형님",
    ),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    532: ("했습니다", "다"),
    616: ("했습니다", "었다"),
    964: ("봅시다", "이제"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    8: (
        "아버님", "어머님", "할아버님", "할머님", "숙부님", "숙모님",
        "그대", "너", "주군님", "주군", "도련님", "공주님", "쇼군님",
        "스님", "네놈", "님", "귀하", "귀공", "원숭이", "놈", "이놈",
        "누님", "형님",
    ),
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
    538: EXPECTED_BASE_MORPHOLOGY_TERMINALS[532],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    976: EXPECTED_BASE_MORPHOLOGY_TERMINALS[964],
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
        raise RuntimeError("segment 993 Base-to-PK mapping drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
    } != {2407}:
        raise RuntimeError("segment 993 Base-to-PK JP literal divergence drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    } != {2401, 2402, 2403, 2404, 2405, 2406, 2408, 2409, 2410}:
        raise RuntimeError("segment 993 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 993 pristine/current gap drifted")
    if any(
        TRANSLATIONS_BY_RECORD[record_id][-1]
        is not ACHIEVEMENT_REWARD_FRAGMENT
        for record_id in (2401, 2402, 2403, 2404, 2405, 2406)
    ):
        raise RuntimeError("segment 993 cross-segment reward fragment reuse drifted")
    if (
        EXPECTED_BASE_GAPS[2407][1:3]
        != (GOAL_NUMBER_TOKEN, MERIT_NUMBER_TOKEN)
        or raw_translations["15:2407:0"] != "세력 목표를 제안한 무장"
    ):
        raise RuntimeError("segment 993 merit award token/source direction drifted")
    if set(EXCLUDED_NONVISIBLE_COORDINATES) != {"15:2409:1"}:
        raise RuntimeError("segment 993 hidden LF coordinate drifted")
    joined = "\n".join(translations.values())
    for required in (
        "성하",
        "석고",
        "합전",
        "훈공",
        "가신단",
        "기강",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 993 required terminology drifted: {required}")
    for forbidden in ("당가", "가중", "영국", "의기", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 993 forbidden wording retained: {forbidden}")
    if set(HISTORICAL_EVIDENCE_URLS) != {"家中", "勲功", "合戦"}:
        raise RuntimeError("segment 993 historical evidence registry drifted")
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 993 visible decision count drifted")


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
    hidden_morphology_row: dict[str, object] = {"coordinate": "15:2409:1"}
    rows.append(hidden_morphology_row)
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
    rows.remove(hidden_morphology_row)
    for row in rows:
        if str(row["coordinate"]).startswith("15:2407:"):
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
            row["basis"] = (
                "pristine_base_pc_jp_authoritative_static_numeric_token_"
                "merit_award_message"
            )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 993 validated count drifted")
    static_rows = [row for row in rows if str(row["coordinate"]).startswith("15:2407:")]
    pending_rows = [row for row in rows if not str(row["coordinate"]).startswith("15:2407:")]
    if (
        len(static_rows) != 3
        or any(
            row["scope_classification"] != "retranslated"
            or row["runtime_review"] != "not_required"
            for row in static_rows
        )
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
        raise RuntimeError("segment 993 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B119_S993",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "retranslated": len(static_rows),
                "runtime_fragment_pending": len(pending_rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [2407],
                "base_pk_jp_gap_divergence_records": [
                    2401, 2402, 2403, 2404, 2405, 2406, 2408, 2409, 2410
                ],
                "base_pk_sc_tc_literal_divergence_records": [2407],
                "base_pk_sc_tc_gap_divergence_records": [],
                "pristine_current_gap_divergence_records": [],
                "excluded_nonvisible_coordinates": sorted(EXCLUDED_NONVISIBLE_COORDINATES),
                "candidate_sha256": PREVIOUS.candidate_sha256(prepared, translations),
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
