#!/usr/bin/env python3
"""Build Base authoring segment 852 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment851 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S852.private.v1.jsonl"
SEGMENT = 852
RAW_TRANSLATIONS: dict[str, str] = {
    "15:908:0": "공작으로 적 성을 약화해 두는 것이 어떻겠사옵니까?\n",
    "15:908:1": "의",
    "15:908:2": "을(를)\n적은 병력으로도 공략할 수 있사옵니다",
    "15:909:0": "성을 공격하시기 전에 공작을 벌이시옵소서\n",
    "15:909:1": "의",
    "15:909:2": "을(를)\n멋지게 함락시킬 수 있을 것이옵니다",
    "15:910:0": "공성 전에 공작을 벌이시옵소서\n",
    "15:910:1": "의",
    "15:910:2": "은(는)\n정공법으로 공략해서는 함락하기 어렵사옵니다",
    "15:911:0": "공작을 제안드리옵니다\n",
    "15:911:1": "의",
    "15:911:2": "은(는) 견고합니다\n허나 미리 손을 써 두면…",
    "15:912:0": "미리 공작을 벌여 두고 싶소\n",
    "15:912:1": "의",
    "15:912:2": "은(는) 공략하기 까다로운 성\n미리 힘을 약화해 두어야 할 듯하오",
    "15:913:0": "공작을 벌이는 것이 어떻겠습니까\n",
    "15:913:1": "의",
    "15:913:2": "은(는) 견고합니다\n쓸 수 있는 수는 미리 써 두고 싶군요…",
    "15:914:0": "의",
    "15:914:1": "은(는)\n상당히 견고한 성인 듯합니다\n미리 힘을 약화해야 하지 않겠습니까?",
    "15:915:0": "에 간자를 보내\n방벽에 구멍을 내고자 하옵니다",
}
RECORD_ARITIES = {
    908: 3,
    909: 3,
    910: 3,
    911: 3,
    912: 3,
    913: 3,
    914: 2,
    915: 1,
}
EXPECTED_JP = {
    908: (
        "工作にて敵城を弱体化させましては？\n",
        "の",
        "を\n少ない兵力で攻められますぞ",
    ),
    909: (
        "城をお攻めになる前に工作をなされませ\n",
        "の",
        "を\n鮮やかに落とすことができましょう",
    ),
    910: (
        "城攻め前に工作を仕掛けられるべし\n",
        "の",
        "は\nまともに攻めても落とすは難じゃ",
    ),
    911: (
        "工作を提案いたします\n",
        "の",
        "は堅固\nしかし、あらかじめ細工をしておけば…",
    ),
    912: (
        "事前に工作をしておきたい\n",
        "の",
        "は厄介な城\n力を削いでおくべきかと",
    ),
    913: (
        "工作はいかがでしょう\n",
        "の",
        "は堅固です\n打てる手は打っておきたいもの…",
    ),
    914: (
        "の",
        "は\nなかなかに堅固な城のようです\n力を削いでおくべきでは？",
    ),
    915: ("に間者を放ち\n防壁に穴を穿ちたく",),
}
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("", "025032", "026432", "050505")
        for record_id in range(908, 914)
    },
    914: ("025032", "026432", "050505"),
    915: ("026432", "0143e2000000050505"),
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES = {
    "15:911:2",
    "15:913:2",
}
SC_AUXILIARY = {
    911: (
        ("我建议做破坏工作。\n", "的", "十分坚固，\n但若事先先下些工夫……"),
        ("", "025032", "026432", "050505"),
    ),
    915: (
        ("向", "放出间谍，\n目的是要在防壁上穿洞。"),
        ("", "026432", "050505"),
    ),
}
TC_AUXILIARY = {
    911: (
        ("微臣建議破壞工作。\n", "的", "固若金湯。\n不過，只要事先耍點技倆……"),
        ("", "025032", "026432", "050505"),
    ),
    915: (
        ("向", "放出間諜，\n目的是要在防壁上穿洞。"),
        ("", "026432", "050505"),
    ),
}
EN_AUXILIARY = {
    911: (
        (
            "I propose we use destabilization. The ",
            "Ös ",
            " is pretty solid, but if we were to sabotage things in advance...",
        ),
        ("", "025032", "026432", "050505"),
    ),
    915: (
        (
            "I would like to unleash our spies on ",
            " so they can poke a few holes in those walls.",
        ),
        ("", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "pristine_base_pc_jp_authoritative_siege_preparation_defense_weakening_"
    "proposals_and_spy_wall_sabotage_with_uniform_plus_7_pk_jp_mapping_pc_"
    "sc_tc_and_pk_en_auxiliary_context_dynamic_castle_tokens_historical_"
    "speaker_register_current_layout_opcode_skeleton_and_isolated_reverse_"
    "overlay_verified_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(908, 914):
        if translations[f"15:{record_id}:1"] != "의":
            raise RuntimeError(
                f"segment 852 dynamic castle possessive drifted: 15:{record_id}:1"
            )
    if translations["15:914:0"] != "의":
        raise RuntimeError("segment 852 15:914 dynamic castle possessive drifted")
    if not translations["15:915:0"].startswith("에 간자를 보내\n"):
        raise RuntimeError("segment 852 15:915 spy destination particle drifted")
    exact_expectations = {
        "15:908:0": "공작으로 적 성을 약화해 두는 것이 어떻겠사옵니까?\n",
        "15:909:2": "을(를)\n멋지게 함락시킬 수 있을 것이옵니다",
        "15:910:0": "공성 전에 공작을 벌이시옵소서\n",
        "15:910:2": "은(는)\n정공법으로 공략해서는 함락하기 어렵사옵니다",
        "15:915:0": "에 간자를 보내\n방벽에 구멍을 내고자 하옵니다",
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 852 audited canonical drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("공성", "공작", "간자", "방벽"):
        if required not in joined:
            raise RuntimeError(
                f"segment 852 siege/sabotage terminology drifted: {required}"
            )
    if any(term in joined for term in ("닌자", "방어력", "책략")):
        raise RuntimeError("segment 852 retained forbidden legacy terminology")


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
        excluded_blank_literals={},
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 852 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S852",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
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
