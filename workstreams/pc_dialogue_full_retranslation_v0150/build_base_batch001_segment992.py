#!/usr/bin/env python3
"""Build Base authoring segment 992 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment991 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S992.private.v1.jsonl"
)
SEGMENT = 992
OFFICER_TOKEN = "024933"
TARGET_FORCE_TOKEN = "025032"
CASTLE_TOKEN = "026432"
GOAL_NUMBER_TOKEN = "0233"
ATTACK_IF_TRANSLATION = "을(를) 공격한다면"
ACHIEVEMENT_REWARD_FRAGMENT = (
    "\n무엇보다 목표를 제안한 이들의 공적이 크니\n각별히 포상"
)
TRANSLATIONS_BY_RECORD = {
    2393: (
        "특히",
        "은(는) 명장으로 이름이 높으니\n섣불리 손을 대지 않도록 조심",
    ),
    2394: (
        "이렇다 할 명장은",
        "지만\n",
        "같은 무장 앞에서는\n방심",
    ),
    2395: (
        "우리 가문은 목표로 삼을 성을 아직 정하지 못한 듯…\n",
        ATTACK_IF_TRANSLATION,
        "일대가\n추천할 만한 곳",
    ),
    2396: (
        "우리 가문은 목표로 삼을 세력을 아직 정하지 못한 듯…\n방금 추천한",
        "을(를) 목표로 ",
        "?",
    ),
    2397: (
        "우리 가문은 목표로 삼을 거점을 아직 정하지 못한 듯…\n",
        ATTACK_IF_TRANSLATION,
        "일대가\n추천할 만한 곳",
    ),
    2398: (
        "지배하는 성의 수가 목표치인",
        "개를 초과",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2399: (
        "휘하 가신의 수가 목표치인",
        "명을 초과",
        ACHIEVEMENT_REWARD_FRAGMENT,
    ),
    2400: (
        "발령한 정책의 수준이 목표치를 초과",
        ACHIEVEMENT_REWARD_FRAGMENT,
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
    2393: (
        "特に",
        "は名将として知られ\nうかつに手を出さば痛い目を見",
    ),
    2394: (
        "これといった名将は",
        "が\n",
        "といった将などには\n警戒をすべきかもし",
    ),
    2395: (
        "当家は目標とする城が決まっていない様子…\n",
        "を攻めるのであれば",
        "あたり\nがオススメ",
    ),
    2396: (
        "当家は目標とする勢力が決まっていない様子…\n先ほどオススメした",
        "と",
        "か？",
    ),
    2397: (
        "当家は目標とする拠点が決まっていない様子…\n",
        "を攻めるのであれば",
        "あたり\nがおすすめ",
    ),
    2398: (
        "支配城数が目標の",
        "を上回",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2399: (
        "配下の数が目標の",
        "名を上回",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
    2400: (
        "発令した政策の水準が目標を上回",
        "\nことに目標を提言した者らの功績は大きく\n格別の報奨を与えることと",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2393: ("", OFFICER_TOKEN, "01431E040000050505"),
    2394: ("", "0143A0000000", OFFICER_TOKEN, "01434E040000050505"),
    2395: ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "01431A020000050505"),
    2396: ("", TARGET_FORCE_TOKEN, "0143CC010000", "050505"),
    2397: ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "01431A020000050505"),
    2398: ("", GOAL_NUMBER_TOKEN, "014368020000", "0143CC010000050505"),
    2399: ("", GOAL_NUMBER_TOKEN, "014368020000", "0143CC010000050505"),
    2400: ("", "014368020000", "0143CC010000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2393: ("", OFFICER_TOKEN, "01432A040000050505"),
    2394: ("", "0143A0000000", OFFICER_TOKEN, "01435A040000050505"),
    2395: ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "014326020000050505"),
    2396: ("", TARGET_FORCE_TOKEN, "0143D2010000", "050505"),
    2397: ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "014326020000050505"),
    2398: ("", GOAL_NUMBER_TOKEN, "014374020000", "0143D2010000050505"),
    2399: ("", GOAL_NUMBER_TOKEN, "014374020000", "0143D2010000050505"),
    2400: ("", "014374020000", "0143D2010000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2395:0",
    "15:2396:0",
    "15:2397:0",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SC_CONTEXT = {
    2393: (("尤其是", "，是声名远播的名将，\n若是轻易出手，不会有好结果的。"), ("", OFFICER_TOKEN, "050505")),
    2394: (("此处没有值得一提的名将，\n但或许该注意一下\n", "等将领。"), ("", OFFICER_TOKEN, "050505")),
    2395: (("本家似乎尚未决定目标城……\n若要攻打", "，我建议选择\n", "一带。"), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505")),
    2396: (("本家似乎尚未决定目标势力……\n要选择先前推荐的", "吗？"), ("", TARGET_FORCE_TOKEN, "050505")),
    2397: (("本家似乎尚未决定目标城……\n若要攻打", "，我推荐选择", "一带。"), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505")),
    2398: (("因支配城数超过目标的", "座，\n提议此目标者的功绩不小，\n故将给予特别的奖励。"), ("", GOAL_NUMBER_TOKEN, "050505")),
    2399: (("因麾下人数超过目标的", "名，\n提议此目标者的功绩不小，\n故将给予特别的奖励。"), ("", GOAL_NUMBER_TOKEN, "050505")),
    2400: (("因颁布的政策水准超越了目标，\n提议此目标者的功绩不小，\n故将给予特别的奖励。",), ("", "050505")),
}
TC_CONTEXT = {
    2393: (("尤其", "乃人盡皆知的名將，\n魯莽出手必嚐苦果。"), ("", OFFICER_TOKEN, "050505")),
    2394: (("當中並無值得一提的名將，\n不過", "這位將領\n或許該稍加提防。"), ("", OFFICER_TOKEN, "050505")),
    2395: (("本家似乎未決定作為目標的城……\n若欲攻打", "，\n", "可列入考量。"), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505")),
    2396: (("本家似乎未決定作為目標的勢力……\n還是要照方才建議的", "？"), ("", TARGET_FORCE_TOKEN, "050505")),
    2397: (("本家似乎未決定作為目標的城……\n若欲攻打", "，\n", "可列入考量。"), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505")),
    2398: (("因支配城數超過目標的", "座，\n提議此目標者的功績不小，\n故將給予特別的獎勵。"), ("", GOAL_NUMBER_TOKEN, "050505")),
    2399: (("因麾下人數超過目標的", "名，\n提議此目標者的功績不小，\n故將給予特別的獎勵。"), ("", GOAL_NUMBER_TOKEN, "050505")),
    2400: (("因頒布的政策水準超越了目標，\n提議此目標者的功績不小，\n故將給予特別的獎勵。",), ("", "050505")),
}
PK_EN_CONTEXT = {
    2393: (("We ought to remember the name ", ". Going up against them unprepared would be a mistake."), ("", OFFICER_TOKEN, "050505")),
    2394: (("There arenÖt any noteworthy officers, but we might do well to stay vigilant around the likes of ", "."), ("", OFFICER_TOKEN, "050505")),
    2395: (("It seems we havenÖt set any target castles. If we are planning to attack the ", ", I would suggest targeting ", "."), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505")),
    2396: (("It seems we havenÖt chosen a clan to target. What do you think about the ", "?"), ("", TARGET_FORCE_TOKEN, "050505")),
    2397: (("It seems we havenÖt chosen a base to target. If we are planning to attack the ", ", I would suggest targeting ", "."), ("", TARGET_FORCE_TOKEN, CASTLE_TOKEN, "050505")),
    2398: (("We have exceeded our goal of controlling ", " castles. Those who proposed the goal should be well rewarded."), ("", GOAL_NUMBER_TOKEN, "050505")),
    2399: (("We have exceeded our goal of enlisting ", " retainers. Those who proposed the goal should be well rewarded."), ("", GOAL_NUMBER_TOKEN, "050505")),
    2400: (("We have exceeded our goal for the standard of issued policies. Those who proposed the goal should be well rewarded.",), ("", "050505")),
}
SHARED_AUXILIARY = {
    **{("SC", record_id): context for record_id, context in SC_CONTEXT.items()},
    **{("TC", record_id): context for record_id, context in TC_CONTEXT.items()},
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_CONTEXT,
)
HISTORICAL_EVIDENCE_URLS = {
    "名将": "https://kotobank.jp/word/%E5%90%8D%E5%B0%86-643030",
    "家中": "https://kotobank.jp/word/%E5%AE%B6%E4%B8%AD-45092",
    "勲功": "https://kotobank.jp/word/%E5%8B%B2%E5%8A%9F-487655",
}
BASIS = (
    "review_queue_base_msggame_B119_A_pristine_base_pc_jp_authoritative_"
    "noteworthy_officers_target_recommendations_and_goal_achievement_"
    "rewards_with_explicit_base2393_2400_to_pk2424_2431_plus31_mapping_"
    "exact_base_pk_jp_sc_tc_literals_actual_pk_en_context_officer_force_"
    "castle_and_goal_number_token_direction_repeated_reward_fragment_"
    "actual_morphology_terminal_corpora_project_ellipsis_current_line_"
    "counts_protected_skeleton_dictionary_evidence_and_runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    160: ("없사옵니다", "없다", "없습니다"),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    616: ("했습니다", "었다"),
    1054: ("합시다", "듯"),
    1102: ("할 수 없습니다", "할 수 없"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    160: EXPECTED_BASE_MORPHOLOGY_TERMINALS[160],
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1114: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1102],
}


def candidate_sha256(prepared: Any, translations: dict[str, str]) -> str:
    replacements = {
        tuple(int(value) for value in coordinate.split(":")): translation
        for coordinate, translation in translations.items()
    }
    rebuilt = ENGINE.rebuild_packed_with_literals(
        prepared.resources["base_msggame"].current_blob,
        replacements,
    )
    return hashlib.sha256(rebuilt).hexdigest().upper()


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 992 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 992 Base-to-PK JP literal drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    } != set(RECORD_ARITIES):
        raise RuntimeError("segment 992 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 992 pristine/current gap drifted")
    if (
        EXPECTED_BASE_GAPS[2393][1] != OFFICER_TOKEN
        or EXPECTED_BASE_GAPS[2394][2] != OFFICER_TOKEN
        or any(
            EXPECTED_BASE_GAPS[record_id][1:3]
            != (TARGET_FORCE_TOKEN, CASTLE_TOKEN)
            for record_id in (2395, 2397)
        )
        or EXPECTED_BASE_GAPS[2396][1] != TARGET_FORCE_TOKEN
        or any(
            GOAL_NUMBER_TOKEN not in EXPECTED_BASE_GAPS[record_id]
            for record_id in (2398, 2399)
        )
    ):
        raise RuntimeError("segment 992 dynamic token direction drifted")
    if (
        TRANSLATIONS_BY_RECORD[2395][1] is not ATTACK_IF_TRANSLATION
        or TRANSLATIONS_BY_RECORD[2397][1] is not ATTACK_IF_TRANSLATION
        or any(
            TRANSLATIONS_BY_RECORD[record_id][-1]
            is not ACHIEVEMENT_REWARD_FRAGMENT
            for record_id in (2398, 2399, 2400)
        )
    ):
        raise RuntimeError("segment 992 exact repeated fragment reuse drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(f"segment 992 project ellipsis pair drifted: {coordinate}")
    joined = "\n".join(translations.values())
    for required in (
        "명장",
        "우리 가문",
        "가신",
        "목표치",
        "공적",
        "포상",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 992 required terminology drifted: {required}")
    for forbidden in (
        "당가",
        "가중",
        "영국",
        "의기",
        "큰코다치",
        "경계해야 할지도 모",
        "。",
        "！",
        "？",
    ):
        if forbidden in joined:
            raise RuntimeError(f"segment 992 forbidden wording retained: {forbidden}")
    if {
        f"{translations['15:2394:2']}{ending}".splitlines()[-1]
        for ending in ("할 수 없습니다", "할 수 없")
    } != {"방심할 수 없습니다", "방심할 수 없"}:
        raise RuntimeError("segment 992 officer-warning morphology drifted")
    if set(HISTORICAL_EVIDENCE_URLS) != {"名将", "家中", "勲功"}:
        raise RuntimeError("segment 992 historical evidence registry drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 992 visible decision count drifted")


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
        raise RuntimeError("segment 992 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 992 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B119_S992",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": list(RECORD_ARITIES),
                "base_pk_sc_tc_literal_divergence_records": [],
                "base_pk_sc_tc_gap_divergence_records": [],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "candidate_sha256": candidate_sha256(prepared, translations),
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
