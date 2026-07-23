#!/usr/bin/env python3
"""Build Base authoring segment 885 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment884 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S885.private.v1.jsonl"
)
SEGMENT = 885
TROOP_CHANGE_ARROW = ("의 병력이", "→", "에")
TROOP_INCREASE = ("의 병력이", "증가")
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:1336:{literal_id}": translation
        for literal_id, translation in enumerate(
            COMMON.TROOP_CHANGE_SUMMARY
        )
    },
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in (1337, 1338)
        for literal_id, translation in enumerate(TROOP_CHANGE_ARROW)
    },
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in (1339, 1340)
        for literal_id, translation in enumerate(TROOP_INCREASE)
    },
    "15:1341:0": "에게 자객을 보내",
    "15:1341:1": "인가\n",
    "15:1341:2": (
        "의 병사들의 움직임을 봉쇄하려면\n"
        "지휘하는 자를 노리는 것이"
    ),
    "15:1341:3": "인가 하고",
    "15:1342:0": "에 자객을 보내",
    "15:1342:1": (
        "인가\n"
        "대군의 움직임을 봉쇄하려면\n"
        "장수를 노리는 것이 가장 빠를 듯하옵니다"
    ),
    "15:1343:0": (
        "에 주둔한 대군도\n"
        "성주가 자객의 습격을 받으면\n"
        "제대로 움직이지 못할 것이옵니다"
    ),
}
RECORD_ARITIES = {
    1336: 5,
    1337: 3,
    1338: 3,
    1339: 2,
    1340: 2,
    1341: 4,
    1342: 2,
    1343: 1,
}
EXPECTED_BASE_JP = {
    1336: ("・", "の兵力が", "増加\n・", "の兵力が", "減少"),
    1337: ("の兵力が", "→", "に"),
    1338: ("の兵力が", "→", "に"),
    1339: ("の兵力が", "増加"),
    1340: ("の兵力が", "増加"),
    1341: (
        "に刺客を送",
        "か\n",
        "の兵の動きを封じるには\n采配する者を狙うのが",
        "かと",
    ),
    1342: (
        "に刺客を送",
        "か\n大軍の動きを封じるには\n将を狙うのが手っ取り早いかと",
    ),
    1343: (
        "が抱える大軍も\n"
        "城主が刺客に襲われれば\n"
        "まともに動けぬようになりましょう",
    ),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1336: ("", "026e32", "0232", "026432", "0232", "050505"),
    1337: ("026e32", "0232", "0233", "050505"),
    1338: ("026e32", "0232", "0233", "050505"),
    1339: ("026e32", "0232", "050505"),
    1340: ("026e32", "0232", "050505"),
    1341: (
        "024833",
        "01432a040000",
        "026432",
        "01430c040000",
        "050505",
    ),
    1342: ("026432", "01432a040000", "050505"),
    1343: ("026432", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **{
        record_id: EXPECTED_BASE_GAPS[record_id]
        for record_id in range(1336, 1341)
    },
    1341: (
        "024833",
        "014336040000",
        "026432",
        "014318040000",
        "050505",
    ),
    1342: ("026432", "014336040000", "050505"),
    1343: ("026432", "050505"),
}
PK_RECORD_MAP = {
    record_id: record_id + 8 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

ARROW_SC = (
    ("的兵力由", "→", "。"),
    ("026e32", "0232", "0233", "050505"),
)
ARROW_TC = (
    ("的兵力", "→", "。"),
    ("026e32", "0232", "0233", "050505"),
)
ARROW_EN = (
    ("Ös soldiers went from ", " to ", "."),
    ("026e32", "0232", "0233", "050505"),
)
INCREASE_SC = (
    ("的兵力增加了", "。"),
    ("026e32", "0232", "050505"),
)
INCREASE_TC = (
    ("的兵力增加", "。"),
    ("026e32", "0232", "050505"),
)
INCREASE_EN = (
    ("Ös soldiers increased by ", "."),
    ("026e32", "0232", "050505"),
)
ASSASSIN_COMMANDER_SC = (
    (
        "向",
        "派出刺客吧？\n要想让",
        "的兵动弹不得，\n就应该以指挥者为目标。",
    ),
    ("", "024833", "026432", "050505"),
)
ASSASSIN_COMMANDER_TC = (
    (
        "不妨向",
        "派出刺客吧？\n我認為，若想牽制",
        "的士兵，\n必須擒拿指揮的大將。",
    ),
    ("", "024833", "026432", "050505"),
)
ASSASSIN_COMMANDER_EN = (
    (
        "Should we send an assassin to deal with ",
        "? If we want to inhibit soldier movement from ",
        ", eliminate the one giving them orders.",
    ),
    ("", "024833", "026432", "050505"),
)
ARMY_COMMAND_SC = (
    (
        "虽有大军，\n但若统领的大将不作为，\n"
        "那大军也形同虚无。",
    ),
    ("026432", "050505"),
)
ARMY_COMMAND_TC = (
    (
        "雖軍勢強大，\n但率軍的將領若毫無作為，\n"
        "大軍則無用武之地。",
    ),
    ("026432", "050505"),
)
ASSASSIN_LORD_EN = (
    (
        "The large army at ",
        " would be rendered useless if an assassin were to kill their lord.",
    ),
    ("", "026432", "050505"),
)
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): ARROW_SC
        for side in ("base", "pk")
        for record_id in (1337, 1338)
    },
    **{
        (side, "TC", record_id): ARROW_TC
        for side in ("base", "pk")
        for record_id in (1337, 1338)
    },
    **{
        ("pk", "EN", record_id): ARROW_EN
        for record_id in (1337, 1338)
    },
    **{
        (side, "SC", 1339): INCREASE_SC
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1339): INCREASE_TC
        for side in ("base", "pk")
    },
    ("pk", "EN", 1339): INCREASE_EN,
    **{
        (side, "SC", 1341): ASSASSIN_COMMANDER_SC
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1341): ASSASSIN_COMMANDER_TC
        for side in ("base", "pk")
    },
    ("pk", "EN", 1341): ASSASSIN_COMMANDER_EN,
    **{
        (side, "SC", record_id): ARMY_COMMAND_SC
        for side in ("base", "pk")
        for record_id in (1342, 1343)
    },
    **{
        (side, "TC", record_id): ARMY_COMMAND_TC
        for side in ("base", "pk")
        for record_id in (1342, 1343)
    },
    ("pk", "EN", 1343): ASSASSIN_LORD_EN,
}
BASIS = (
    "review_queue_base_msggame_B107_pristine_base_pc_jp_authoritative_"
    "troop_change_ui_and_assassin_proposals_against_commanders_and_castle_"
    "lords_with_explicit_plus_8_pk_jp_mapping_base_pk_sc_tc_exact_pk_en_"
    "auxiliary_context_exact_ui_pairs_assassination_inhibited_troop_"
    "movement_dynamic_person_castle_unit_and_value_tokens_live_morphology_"
    "stems_speaker_register_current_layout_and_opcode_skeleton_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if tuple(
        raw_translations[f"15:1336:{literal_id}"]
        for literal_id in range(RECORD_ARITIES[1336])
    ) != COMMON.TROOP_CHANGE_SUMMARY:
        raise RuntimeError(
            "segment 885 B107 S884 troop-change summary canonical drifted"
        )
    for left, right in ((1337, 1338), (1339, 1340)):
        if COMMON.CORE.source_literals(
            source_records,
            left,
        ) != COMMON.CORE.source_literals(source_records, right):
            raise RuntimeError(
                f"segment 885 exact troop UI source pair drifted: "
                f"{left}/{right}"
            )
        left_group = tuple(
            raw_translations[f"15:{left}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[left])
        )
        right_group = tuple(
            raw_translations[f"15:{right}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[right])
        )
        if left_group != right_group:
            raise RuntimeError(
                f"segment 885 exact troop UI translation pair drifted: "
                f"{left}/{right}"
            )
    if (
        EXPECTED_BASE_GAPS[1341][0] != "024833"
        or EXPECTED_BASE_GAPS[1341][2] != "026432"
        or EXPECTED_BASE_GAPS[1342][0] != "026432"
        or EXPECTED_BASE_GAPS[1343][0] != "026432"
    ):
        raise RuntimeError(
            "segment 885 assassin person/castle token order drifted"
        )
    joined = "\n".join(translations.values())
    for required in (
        "자객",
        "병사들의 움직임",
        "봉쇄",
        "지휘하는 자",
        "장수를 노리는 것",
        "가장 빠",
        "성주",
        "습격",
        "제대로 움직이지 못",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 885 assassin semantics drifted: {required}"
            )
    if any(term in joined for term in ("암살자", "병사의 움직임을 봉하")):
        raise RuntimeError("segment 885 retained forbidden assassin phrasing")
    if not raw_translations["15:1341:0"].endswith("보내"):
        raise RuntimeError("segment 885 1341 live send stem drifted")
    if raw_translations["15:1341:1"] != "인가\n":
        raise RuntimeError("segment 885 1341 question continuation drifted")
    if not raw_translations["15:1342:0"].startswith("에 자객"):
        raise RuntimeError("segment 885 1342 castle destination particle drifted")
    if not raw_translations["15:1343:0"].startswith("에 주둔한 대군"):
        raise RuntimeError("segment 885 1343 castle army relation drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != len(translations):
        raise RuntimeError("segment 885 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S885",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "exact_troop_ui_pairs": 2,
                "assassin_proposal_records": 3,
                "explicit_pk_mapping": True,
                "contextual_ellipsis_normalized_to_project_pair": 0,
                "record_count": 19152,
                "outside_scope_records_exact": True,
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
