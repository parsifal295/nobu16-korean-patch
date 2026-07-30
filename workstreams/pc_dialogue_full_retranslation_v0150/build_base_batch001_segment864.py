#!/usr/bin/env python3
"""Build Base authoring segment 864 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment863 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S864.private.v1.jsonl"
SEGMENT = 864
REPAIR_NEXT_BATTLE = (
    "을(를) 수복하였사옵니다\n"
    "이로써 다음 싸움에도 만전을 기할 수 있겠사옵니다"
)
REPAIR_OPCODE_STEMS = (
    "을(를) 서둘러 수복하",
    "\n이제 어지간한 공격은 견딜 수 있",
)
ENEMY_REPAIR_OPCODE_STEMS = (
    "의",
    "에서\n",
    "이(가) 시행되",
    "\n분하게도 방비가 강화되",
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1078:0": COMMON.REPAIR_GALLANT,
    "15:1079:0": COMMON.REPAIR_RUMOR,
    "15:1080:0": REPAIR_NEXT_BATTLE,
    "15:1081:0": COMMON.REPAIR_RESTORED_VOCATIVE[0],
    "15:1081:1": COMMON.REPAIR_RESTORED_VOCATIVE[1],
    "15:1082:0": COMMON.REPAIR_BATTLE_READY,
    "15:1083:0": COMMON.REPAIR_THOUGHTS,
    "15:1084:0": COMMON.REPAIR_FEMININE,
    "15:1085:0": COMMON.REPAIR_SLEEP,
    "15:1086:0": "·",
    "15:1086:1": "의 내구가",
    "15:1086:2": "회복",
    "15:1087:0": REPAIR_OPCODE_STEMS[0],
    "15:1087:1": REPAIR_OPCODE_STEMS[1],
    "15:1088:0": ENEMY_REPAIR_OPCODE_STEMS[0],
    "15:1088:1": ENEMY_REPAIR_OPCODE_STEMS[1],
    "15:1088:2": ENEMY_REPAIR_OPCODE_STEMS[2],
    "15:1088:3": ENEMY_REPAIR_OPCODE_STEMS[3],
    "15:1089:0": "의 내구가",
    "15:1089:1": "회복(",
    "15:1089:2": "→",
    "15:1089:3": ")",
}
RECORD_ARITIES = {
    1078: 1,
    1079: 1,
    1080: 1,
    1081: 2,
    1082: 1,
    1083: 1,
    1084: 1,
    1085: 1,
    1086: 3,
    1087: 2,
    1088: 4,
    1089: 4,
}
EXPECTED_JP = {
    1078: (
        "、一気に修復いたしてござる\n"
        "ご覧あれ、この城の勇姿\n"
        "これでまだまだ戦えまするぞ",
    ),
    1079: (
        "の修復、一気に完了させました\n"
        "この城が傷ついたとの噂に釣られて\n"
        "敵が参っても、返り討ちにしてやれまする",
    ),
    1080: (
        "を修復いたしてございまする\n"
        "これで次の戦にも万全に臨めましょう",
    ),
    1081: (
        "修復で、あの荒れ城が早や元通りでござるわ\n",
        "よ、またよう戦ってくれい",
    ),
    1082: ("を修復しました\nこれでいつ合戦になっても安心ですね",),
    1083: (
        "修復が完了した\n"
        "携わった者の思いがこもっている\n"
        "どんな攻撃にも耐えてくれよう",
    ),
    1084: (
        "を修復しましたわ\n"
        "これでいつ攻められようと\n"
        "憂いはありません",
    ),
    1085: (
        "を修復いたしましたぞ\n"
        "これで耐久は十分でしょう\n"
        "安心して眠れますな！",
    ),
    1086: ("・", "の耐久が", "回復"),
    1087: ("を急ぎ修復いたし", "\nこれで多少の攻撃なら耐えられ"),
    1088: (
        "の",
        "にて\n",
        "が実施され",
        "\n忌々しくも、防備が増強されて",
    ),
    1089: ("の耐久が", "回復(", "→", ")"),
}
EXPECTED_BASE_GAPS = {
    1078: ("026432", "050505"),
    1079: ("026432", "050505"),
    1080: ("026432", "050505"),
    1081: ("", "026432", "050505"),
    1082: ("026432", "050505"),
    1083: ("026432", "050505"),
    1084: ("026432", "050505"),
    1085: ("026432", "050505"),
    1086: ("", "026432", "1b434a02321b435a", "050505"),
    1087: ("026432", "014314020000", "01431e0400000143d4020000050505"),
    1088: (
        "025032",
        "026432",
        "023c",
        "014314020000",
        "0143b2000000050505",
    ),
    1089: ("026432", "0232", "0233", "0234", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1087: ("026432", "01431a020000", "01432a0400000143e0020000050505"),
    1088: (
        "025032",
        "026432",
        "023c",
        "01431a020000",
        "0143b2000000050505",
    ),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1087): (
            ("迅速修复了", "。\n这下可以承受一些攻击了。"),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1087): (
            ("已完成對", "的緊急修復了。\n這樣多少又能承受敵方的攻擊了吧。"),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1087): (
        (" was quickly repaired. It should be able to withstand a few more attacks now.",),
        ("026432", "050505"),
    ),
    **{
        (side, "SC", 1088): (
            ("的", "，\n进行了", "。"),
            ("025032", "026432", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1088): (
            ("的", "，\n進行了", "。"),
            ("025032", "026432", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1088): (
        (" was enacted at the ", "Ös ", ". ItÖs annoying, but the defenses were bolstered."),
        ("023c", "025032", "026432", "050505"),
    ),
    **{
        (side, "SC", 1089): (
            ("的耐久度恢复", "。(", "→", ")。"),
            ("026432", "0232", "0233", "0234", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1089): (
            ("的耐久恢復", "(", "→", ")。"),
            ("026432", "0232", "0233", "0234", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1089): (
        (" has restored ", " HP (", " Ð ", ")."),
        ("026432", "0232", "0233", "0234", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B104_pristine_base_pc_jp_authoritative_castle_"
    "repair_completion_enemy_repair_and_durability_recovery_fragments_with_"
    "uniform_plus_8_pk_jp_sc_tc_exact_mapping_pk_en_auxiliary_context_cross_"
    "segment_exact_source_pairs_distinct_1068_1080_endings_0143_korean_verb_"
    "stems_historical_speaker_register_current_layout_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    exact_pairs = {
        1066: 1078,
        1067: 1079,
        1069: 1081,
        1070: 1082,
        1071: 1083,
        1072: 1084,
        1073: 1085,
    }
    for left, right in exact_pairs.items():
        if COMMON.CORE.source_literals(
            source_records, left
        ) != COMMON.CORE.source_literals(source_records, right):
            raise RuntimeError(
                f"segment 864 exact repair source pair drifted: {left}/{right}"
            )
        left_translations = tuple(
            COMMON.RAW_TRANSLATIONS[
                f"15:{left}:{literal_id}"
            ]
            for literal_id in range(len(COMMON.CORE.source_literals(source_records, left)))
        )
        right_translations = tuple(
            raw_translations[f"15:{right}:{literal_id}"]
            for literal_id in range(len(COMMON.CORE.source_literals(source_records, right)))
        )
        if left_translations != right_translations:
            raise RuntimeError(
                f"segment 864 exact repair translation pair drifted: {left}/{right}"
            )
    if COMMON.CORE.source_literals(
        source_records, 1068
    ) == COMMON.CORE.source_literals(source_records, 1080):
        raise RuntimeError("segment 864 distinct 1068/1080 repair sources collapsed")
    if raw_translations["15:1080:0"] == COMMON.RAW_TRANSLATIONS["15:1068:0"]:
        raise RuntimeError("segment 864 distinct 1068/1080 translations collapsed")

    if tuple(raw_translations[f"15:1087:{i}"] for i in range(2)) != REPAIR_OPCODE_STEMS:
        raise RuntimeError("segment 864 1087 repair opcode stems drifted")
    if tuple(
        raw_translations[f"15:1088:{i}"] for i in range(4)
    ) != ENEMY_REPAIR_OPCODE_STEMS:
        raise RuntimeError("segment 864 1088 enemy repair opcode stems drifted")
    for coordinate in ("15:1087:0", "15:1087:1", "15:1088:2", "15:1088:3"):
        if raw_translations[coordinate].endswith(
            ("다", "요", "오", "니다", "사옵니다", "습니다")
        ):
            raise RuntimeError(
                f"segment 864 completed verb precedes live 0143 opcode: {coordinate}"
            )

    joined = "\n".join(translations.values())
    for required in ("수복", "내구", "회복", "방비", "강화"):
        if required not in joined:
            raise RuntimeError(f"segment 864 repair terminology drifted: {required}")
    if "、" in joined or "합전" in joined:
        raise RuntimeError("segment 864 retained forbidden repair phrasing")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 864 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S864",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "excluded_nonvisible_decisions": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
