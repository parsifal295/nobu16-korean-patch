#!/usr/bin/env python3
"""Build Base authoring segment 982 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment981 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S982.private.v1.jsonl"
)
SEGMENT = 982
DESTINATION_TOKEN = PREVIOUS.DESTINATION_TOKEN
PERSON_TOKEN = "024833"
FRONT_TRANSFER = "전선으로 전봉되기를 바라는 자가"
REAR_TRANSFER = "후방으로 전봉되기를 바라는 자가"
TRANSFER_PROPOSAL = PREVIOUS.TRANSFER_PROPOSAL
TRANSLATIONS_BY_RECORD = {
    2278: (
        FRONT_TRANSFER,
        "\n인재가 드문",
        TRANSFER_PROPOSAL,
    ),
    2279: (
        FRONT_TRANSFER,
        "\n더욱 능력을 발휘할 수 있는",
        TRANSFER_PROPOSAL,
    ),
    2280: (
        REAR_TRANSFER,
        "\n일손이 부족한",
        TRANSFER_PROPOSAL,
    ),
    2281: (
        REAR_TRANSFER,
        "\n인재가 드문",
        TRANSFER_PROPOSAL,
    ),
    2282: (
        REAR_TRANSFER,
        "\n더욱 능력을 발휘할 수 있는",
        TRANSFER_PROPOSAL,
    ),
    2283: (
        FRONT_TRANSFER,
        "\n방비에 힘을 발휘하게 하고자\n",
        "(으)로 배치해 주",
        "겠습니까?",
    ),
    2284: (
        "이(가) 싸움이 벌어지면 반드시\n"
        "참전하여 힘을 발휘하고 싶다고 하옵니다\n"
        "전선의 성에 배치해 주",
        "겠습니까?",
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
    2278: (
        "前線への転封を望む者が",
        "\n人材が手薄な",
        "へ\n転封しては",
    ),
    2279: (
        "前線への転封を望む者が",
        "\nより能力を振るえる",
        "へ\n転封しては",
    ),
    2280: (
        "後方への転封を望む者が",
        "\n人手不足の",
        "へ\n転封しては",
    ),
    2281: (
        "後方への転封を望む者が",
        "\n人材が手薄な",
        "へ\n転封しては",
    ),
    2282: (
        "後方への転封を望む者が",
        "\nより能力を振るえる",
        "へ\n転封しては",
    ),
    2283: (
        "前線への転封を望む者が",
        "\n防備に力を発揮してもらうべく\n",
        "へ配してや",
        "か",
    ),
    2284: (
        "が戦の際は必ずや\n参陣し力を振るいたいとのこと\n前線の城に配してや",
        "か",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
TRANSFER_GAPS = (
    "",
    "0143B2000000",
    DESTINATION_TOKEN,
    "0143B0020000014356020000050505",
)
PK_TRANSFER_GAPS = (
    "",
    "0143B2000000",
    DESTINATION_TOKEN,
    "0143BC020000014362020000050505",
)
EXPECTED_BASE_GAPS = {
    2278: TRANSFER_GAPS,
    2279: TRANSFER_GAPS,
    2280: TRANSFER_GAPS,
    2281: TRANSFER_GAPS,
    2282: TRANSFER_GAPS,
    2283: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "01432A040000",
        "050505",
    ),
    2284: (PERSON_TOKEN, "01432A040000", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2278: PK_TRANSFER_GAPS,
    2279: PK_TRANSFER_GAPS,
    2280: PK_TRANSFER_GAPS,
    2281: PK_TRANSFER_GAPS,
    2282: PK_TRANSFER_GAPS,
    2283: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "014336040000",
        "050505",
    ),
    2284: (PERSON_TOKEN, "014336040000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2278): (
        ("有人愿转封至前线。\n转封至人才不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2278): (
        ("有人願轉封至前線。\n轉封至人才不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2279): (
        ("有人愿转封至前线。\n转封至更能发挥能力的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2279): (
        ("有人願轉封至前線。\n轉封至更能發揮能力的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2280): (
        ("有人愿转封至后方。\n转封至人手不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2280): (
        ("有人願轉封至後方。\n轉封至人手不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2281): (
        ("有人愿转封至后方。\n转封至人才不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2281): (
        ("有人願轉封至後方。\n轉封至人才不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2282): (
        ("有人愿转封至后方。\n转封至更能发挥能力的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2282): (
        ("有人願轉封至後方。\n轉封至更能發揮能力的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2283): (
        ("有人希望被调往前线。\n为了在防备上发挥其实力，\n应该配属至", "。"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2283): (
        ("有人自願改封至前線。\n為使其能在防備方面發揮實力，\n就派至", "吧。"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2284): (
        ("一到开战之时，\n就想上阵大闹一番。\n不如就派到前线的城去吧？",),
        (PERSON_TOKEN, "050505"),
    ),
    ("TC", 2284): (
        ("盼戰爭時能夠參陣，全力奮戰。\n就派至前線的城吧。",),
        (PERSON_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2278: (
        (
            "There is an officer wishing to be relocated to the front lines. ",
            " is shorthanded, so what do you think of moving them there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2279: (
        (
            "There is an officer wishing to be relocated to the front lines. ",
            " could use a boost in ability, so what do you think of moving them "
            "there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2280: (
        (
            "There is an officer wishing to be relocated to the rear. ",
            " lacks sufficient personnel, so what do you think of moving them "
            "there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2281: (
        (
            "There is an officer wishing to be relocated to the rear. ",
            " is shorthanded, so what do you think of moving them there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2282: (
        (
            "There is an officer wishing to be relocated to the rear. ",
            " could use a boost in ability, so what do you think of moving them "
            "there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2283: (
        (
            "There is an officer wishing to be relocated to the front lines. ",
            " needs to supplement their defenses, so what do you think of moving "
            "them there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2284: (
        (
            " wants to be of aid when the fighting starts. Will you assign them "
            "to a castle on the front lines?",
        ),
        (PERSON_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_C_pristine_base_pc_jp_authoritative_"
    "front_rear_relocation_requests_personnel_talent_ability_defense_and_"
    "battle_participation_with_explicit_base2278_2284_to_pk2309_2315_"
    "plus31_mapping_exact_base_pk_jp_sc_tc_literals_actual_pk_en_"
    "auxiliary_context_転封_as_jeonbong_参陣_as_chamjeon_配する_as_"
    "baechi_without_conflating_relocation_and_assignment_dynamic_"
    "destination_and_person_token_direction_personnel_vs_talent_wording_"
    "morphology_terminal_corpora_current_line_counts_and_protected_"
    "skeleton_preserved_runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    178: ("있습니다", "있다", "있사옵니다"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    1066: ("하지 않습니다", "않는", "않"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    1078: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1066],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 982 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 982 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != set(range(2278, 2285)):
        raise RuntimeError("segment 982 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 982 pristine/current gap drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id][2] != DESTINATION_TOKEN
        for record_id in range(2278, 2284)
    ) or EXPECTED_BASE_GAPS[2284][0] != PERSON_TOKEN:
        raise RuntimeError("segment 982 destination/person token direction drifted")
    joined = "\n".join(translations.values())
    for required in ("전봉", "배치", "참전", "전선", "후방"):
        if required not in joined:
            raise RuntimeError(f"segment 982 terminology drifted: {required}")
    for forbidden in ("전근", "전출", "배속", "참진", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 982 forbidden wording retained: {forbidden}")
    if (
        "전봉" in raw_translations["15:2283:2"]
        or "배치" not in raw_translations["15:2283:2"]
        or "전봉" in raw_translations["15:2284:0"]
        or "배치" not in raw_translations["15:2284:0"]
    ):
        raise RuntimeError("segment 982 relocation/assignment distinction drifted")
    if (
        "일손이 부족한" not in raw_translations["15:2280:1"]
        or "인재가 드문" not in raw_translations["15:2281:1"]
        or "능력을 발휘" not in raw_translations["15:2282:1"]
    ):
        raise RuntimeError("segment 982 destination rationale distinction drifted")
    if (
        any(
            raw_translations[f"15:{record_id}:2"] != TRANSFER_PROPOSAL
            or "어떻겠소" in raw_translations[f"15:{record_id}:2"]
            for record_id in range(2278, 2283)
        )
        or SUPPORT.morphology_operands(TRANSFER_GAPS[3]) != (688, 598)
        or SUPPORT.morphology_operands(PK_TRANSFER_GAPS[3]) != (700, 610)
    ):
        raise RuntimeError("segment 982 dynamic transfer proposal ending drifted")
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 982 visible decision count drifted")


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
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 982 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 982 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S982",
                "source_literal_count": 21,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": list(range(2278, 2285)),
                "pristine_current_gap_divergence_records": [],
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
