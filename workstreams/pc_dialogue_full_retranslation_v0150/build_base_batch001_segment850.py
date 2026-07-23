#!/usr/bin/env python3
"""Build Base authoring segment 850 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment849 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S850.private.v1.jsonl"
SEGMENT = 850
CASTLE_ASSAULT_CANONICAL_893_925 = (
    "다가올 공성에 대비하여\n"
    "미리 적의 힘을 깎아 둔다면\n"
    "손쉽게 공략할 수 있을 터…"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:883:0": "의",
    "15:883:1": (
        "은(는)\n"
        "제법 까다로운 성인 듯하군\n"
        "조금 공작을 걸어 보는 게 어떤가?"
    ),
    "15:884:0": (
        "적의 성을 공략하기 전에 약화 공작을\n"
        "벌이는 것은 상도… 노릴 곳은\n"
    ),
    "15:884:1": "의",
    "15:884:2": "일까",
    "15:885:0": "의",
    "15:885:1": (
        "은(는)\n"
        "견고한 성으로 이름났사오나\n"
        "미리 공작을 벌인다면 혹시…"
    ),
    "15:886:0": "의",
    "15:886:1": (
        "은(는)\n"
        "정면으로 쳐서는 함락되지 않는다!\n"
        "공작을 벌여야 한다"
    ),
    "15:887:0": "의",
    "15:887:1": (
        "\n공략하기 어려워 보이네요… 하지만\n"
        "미리 공작을 벌여 두면 어떨까요?"
    ),
    "15:888:0": "의",
    "15:888:1": (
        "은(는)\n"
        "다소 성가신 존재… 공략하기 전에\n"
        "힘을 깎아 두어야 할까…"
    ),
    "15:889:0": (
        "은(는) 공략하기 어렵다고\n"
        "말씀하시는 분이 많은 듯하네요\n"
        "뭔가 방도가 없을까…"
    ),
    "15:890:0": "의",
    "15:890:1": (
        "은(는)\n"
        "상당히 견고한 성인 듯하옵니다\n"
        "미리 힘을 깎아 두심이 어떻겠사옵니까?"
    ),
    "15:891:0": (
        "적의 성을 공략한다고 고지식하게\n"
        "포위할 필요는 없지. 공략하기 전에\n"
        "성벽이라도 조금 부숴 두면…"
    ),
    "15:892:0": (
        "공성이야말로 전국 난세의 묘미. 마음껏\n"
        "무공을 세우고자 하오나\n"
        "그 전에 할 일이 있사옵니다"
    ),
    "15:893:0": CASTLE_ASSAULT_CANONICAL_893_925,
    "15:894:0": (
        "정면으로 적의 성을 공략하는 것은 어리석은 계책\n"
        "포위하기 전에 성의 방비를\n"
        "약화시켜 두어야 할 듯하옵니다"
    ),
    "15:895:0": (
        "공성은 정정당당하게 임하고 싶다만\n"
        "전국의 난세라면 그것만으로는\n"
        "부족한 법…"
    ),
}
RECORD_ARITIES = {
    883: 2,
    884: 3,
    885: 2,
    886: 2,
    887: 2,
    888: 2,
    889: 1,
    890: 2,
    **{record_id: 1 for record_id in range(891, 896)},
}
EXPECTED_BASE_GAPS = {
    883: ("025032", "026432", "050505"),
    884: ("", "025032", "026432", "050505"),
    885: ("025032", "026432", "050505"),
    886: ("025032", "026432", "050505"),
    887: ("025032", "026432", "050505"),
    888: ("025032", "026432", "050505"),
    889: ("026432", "050505"),
    890: ("025032", "026432", "050505"),
    **{record_id: ("", "050505") for record_id in range(891, 896)},
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {record_id: 1 for record_id in range(883, 896)}
EXPECTED_PK_EN_GAPS = {
    record_id: ("", "050505") for record_id in range(883, 896)
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:884:0",
    "15:885:1",
    "15:887:1",
    "15:888:1",
    "15:889:0",
    "15:891:0",
    "15:893:0",
    "15:895:0",
}
BASIS = (
    "base_msggame_B103_pristine_base_pc_jp_authoritative_personality_castle_"
    "assault_subterfuge_proposals_and_exact_893_925_cross_batch_canonical_"
    "uniform_plus_7_pk_jp_sc_arrays_base_pk_sc_tc_exact_pk_en_auxiliary_"
    "context_dynamic_faction_castle_tokens_castle_assault_terminology_"
    "historical_register_current_pc_line_gap_outer_signature_preserved_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    expected_jp = {
        883: (
            "の",
            "は\nなかなか厄介な城のようだ\n少し細工を仕掛けたらどうだ？",
        ),
        884: (
            "敵城を攻める前に弱体化の工作\nを仕掛けるは常道…狙い目は\n",
            "の",
            "かな",
        ),
        885: (
            "の",
            "は\n堅固な城という評判ですが\n事前に工作すればあるいは…",
        ),
        886: (
            "の",
            "は\nまともに攻めても落ちはせん！\n工作を仕掛けるべきよ",
        ),
        887: (
            "の",
            "\n攻めにくそうですね…でも\nあらかじめ細工をしておけば？",
        ),
        888: (
            "の",
            "は\n少々厄介な存在…攻める前に\n力を削いでおくべきか…",
        ),
        889: (
            "は攻めにくいと\n仰る方が多いようですね\n何か工夫できないかしら…",
        ),
        890: (
            "の",
            "は\n中々に堅固な城のようです\n力を削いでおくべきでは？",
        ),
        891: (
            "敵の城を攻めるのに馬鹿正直に\n"
            "包囲することはない。攻める前\n"
            "に少し城壁でも壊しときゃ…",
        ),
        892: (
            "城攻めこそ戦国の醍醐味。存分\n"
            "に武功を挙げようと存ずるが\n"
            "その前にやることがあります",
        ),
        893: (
            "来るべき城攻めに備えて\n"
            "事前に敵の力を削いでおけば\n"
            "容易に攻め込めるはず…",
        ),
        894: (
            "真正面から敵城を攻めるは愚策\n"
            "包囲する前に城の防備を\n"
            "弱体化させておくべきかと",
        ),
        895: (
            "城攻めは正々堂々とありたいが\n"
            "戦国の世となればそれだけでは\n"
            "足りぬというもの…",
        ),
    }
    for record_id, expected in expected_jp.items():
        if COMMON.source_literals(source_records, record_id) != expected:
            raise RuntimeError(f"segment 850 authoritative Base JP drifted: {record_id}")

    if COMMON.source_literals(source_records, 893) != COMMON.source_literals(
        source_records, 925
    ):
        raise RuntimeError("segment 850 893/925 exact source canonical drifted")
    if raw_translations["15:893:0"] != CASTLE_ASSAULT_CANONICAL_893_925:
        raise RuntimeError("segment 850 893/925 translation canonical drifted")

    exact_expectations = {
        "15:883:0": "의",
        "15:884:1": "의",
        "15:884:2": "일까",
        "15:885:0": "의",
        "15:886:0": "의",
        "15:887:0": "의",
        "15:888:0": "의",
        "15:890:0": "의",
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(f"segment 850 token role/particle drifted: {coordinate}")

    joined = "\n".join(translations.values())
    for required in ("공성", "공작", "공략", "함락", "성벽", "방비"):
        if required not in joined:
            raise RuntimeError(f"segment 850 terminology drifted: {required}")
    if any(term in joined for term in ("공성전", "성 공략", "떨어지지 않아")):
        raise RuntimeError("segment 850 retained forbidden legacy phrasing")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_en_arities=EXPECTED_PK_EN_ARITIES,
        pk_en_gaps=EXPECTED_PK_EN_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 850 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S850",
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
