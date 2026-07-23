#!/usr/bin/env python3
"""Build Base authoring segment 881 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment856 as CAPTURE_B103
import build_base_batch001_segment869 as COMMON
import build_base_batch001_segment870 as CAPTURE_B105


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S881.private.v1.jsonl"
)
SEGMENT = 881
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1275:0": "에게서",
    "15:1275:1": "을(를) 받아\n",
    "15:1275:2": "의 방비가 흔들리고",
    "15:1275:3": "…",
    "15:1276:0": "에서 간자를 붙잡아",
    "15:1276:2": "이(가) 벌인",
    "15:1276:3": "이(가) 밀명이었다니…\n하마터면 큰일 날 뻔했소",
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in (1277, 1278)
        for literal_id, translation in enumerate(("·", "의 내구가", "감소"))
    },
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in (1279, 1280)
        for literal_id, translation in enumerate(
            ("·", "에 대한 땅굴 공략에 실패")
        )
    },
    "15:1281:0": "의 땅굴 공략으로",
    "15:1281:1": "의 내구-",
    "15:1282:0": "의 땅굴 공략을 받아",
    "15:1282:1": "의 내구-",
}
RECORD_ARITIES = {
    1275: 4,
    1276: 4,
    1277: 3,
    1278: 3,
    1279: 2,
    1280: 2,
    1281: 2,
    1282: 2,
}
EXPECTED_BASE_JP = {
    1275: ("より", "を受け\n", "の防備が揺らいで", "…"),
    1276: (
        "にて間者を捕らえ",
        "\n",
        "による",
        "が密命とか…\n危ないところ",
    ),
    1277: ("・", "の耐久が", "減少"),
    1278: ("・", "の耐久が", "減少"),
    1279: ("・", "への土竜攻めに失敗"),
    1280: ("・", "への土竜攻めに失敗"),
    1281: ("の土竜攻めにより", "の耐久-"),
    1282: ("の土竜攻めを受け", "の耐久-"),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1275: ("025032", "023C", "026432", "0143B2000000", "050505"),
    1276: (
        "026432",
        "014314020000",
        "025032",
        "023C",
        "014344020000050505",
    ),
    **{
        record_id: ("", "026432", "0232", "050505")
        for record_id in (1277, 1278)
    },
    **{
        record_id: ("", "026432", "050505")
        for record_id in (1279, 1280)
    },
    **{
        record_id: ("024633", "026432", "0232050505")
        for record_id in (1281, 1282)
    },
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1276: (
        "026432",
        "01431A020000",
        "025032",
        "023C",
        "014350020000050505",
    ),
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1275:3", "15:1276:3"}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1276:1": "\n"}


def make_auxiliary_overrides(
    shared: dict[
        tuple[str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    pk_en: dict[int, tuple[tuple[str, ...], tuple[str, ...]]],
) -> dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
]:
    return {
        **{
            (side, language, record_id): expected
            for (language, record_id), expected in shared.items()
            for side in ("base", "pk")
        },
        **{
            ("pk", "EN", record_id): expected
            for record_id, expected in pk_en.items()
        },
    }


SHARED_AUXILIARY = {
    ("SC", 1275): (
        ("因", "发动的", "，\n", "的防备正产生动摇……"),
        ("", "025032", "023C", "026432", "050505"),
    ),
    ("TC", 1275): (
        ("因", "發動的", "，\n", "的防備正產生動搖……"),
        ("", "025032", "023C", "026432", "050505"),
    ),
    ("SC", 1276): (
        (
            "已于",
            "逮捕间谍。\n据说是",
            "的",
            "发出密令……\n差点就没命了。",
        ),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("TC", 1276): (
        (
            "已於",
            "逮捕間諜。\n據說是",
            "的",
            "發出密令……\n差點就沒命了。",
        ),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("SC", 1281): (
        ("因为", "进行的地道攻势，", "的耐久-", "。"),
        ("", "024633", "026432", "0232", "050505"),
    ),
    ("TC", 1281): (
        ("由於", "的地道攻勢，", "的耐久-", "。"),
        ("", "024633", "026432", "0232", "050505"),
    ),
    ("SC", 1282): (
        ("受到了", "的地道攻势，", "的耐久-", "。"),
        ("", "024633", "026432", "0232", "050505"),
    ),
    ("TC", 1282): (
        ("因遭受", "的地道攻勢，", "的耐久-", "。"),
        ("", "024633", "026432", "0232", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1275: (
        ("After the ", "Ös ", ", ", "Ös defenses were weakened."),
        ("", "025032", "023C", "026432", "050505"),
    ),
    1276: (
        (
            "WeÖve captured spies in ",
            ". They had the ",
            "Ös ",
            " secret orders... That could have been bad.",
        ),
        ("", "026432", "025032", "023C", "050505"),
    ),
    1281: (
        (" lost ", " HP due to ", "Ös tunneling."),
        ("026432", "0232", "024633", "050505"),
    ),
    1282: (
        (" lost ", " HP after suffering ", "Ös tunneling."),
        ("026432", "0232", "024633", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "tunneling_results_ui_spy_capture_and_miner_corps_runtime_tokens_with_"
    "uniform_plus_8_pk_jp_sc_tc_mapping_distinct_1276_base_pk_opcode_params_"
    "hidden_newline_preserved_b103_b105_spy_capture_canonical_exact_result_"
    "pairs_distinct_attacker_victim_viewpoints_project_tunneling_terminology_"
    "current_layout_and_opcode_skeleton_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if "15:1276:1" in raw_translations or "15:1276:1" in translations:
        raise RuntimeError("segment 881 excluded 1276 newline received a decision")
    capture_pairs = (
        (
            "15:1276:0",
            CAPTURE_B103.CAPTURE_TRANSLATIONS["15:973:0"],
        ),
        (
            "15:1276:2",
            CAPTURE_B103.CAPTURE_TRANSLATIONS["15:973:2"],
        ),
        (
            "15:1276:3",
            CAPTURE_B103.CAPTURE_TRANSLATIONS["15:973:3"],
        ),
    )
    for coordinate, canonical in capture_pairs:
        if raw_translations[coordinate] != canonical:
            raise RuntimeError(
                f"segment 881 B103 capture canonical drifted: {coordinate}"
            )
    for literal_id in (2, 3):
        if raw_translations[f"15:1276:{literal_id}"] != (
            CAPTURE_B105.RAW_TRANSLATIONS[f"15:1129:{literal_id}"]
        ):
            raise RuntimeError(
                f"segment 881 B105 capture canonical drifted: 15:1276:{literal_id}"
            )
    for left, right in ((1277, 1278), (1279, 1280)):
        if COMMON.CORE.source_literals(
            source_records, left
        ) != COMMON.CORE.source_literals(source_records, right):
            raise RuntimeError(
                f"segment 881 exact tunneling result source pair drifted: "
                f"{left}/{right}"
            )
        left_group = tuple(
            translations[f"15:{left}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[left])
        )
        right_group = tuple(
            translations[f"15:{right}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[right])
        )
        if left_group != right_group:
            raise RuntimeError(
                f"segment 881 exact tunneling result translation pair drifted: "
                f"{left}/{right}"
            )
    if (
        EXPECTED_BASE_JP[1281] == EXPECTED_BASE_JP[1282]
        or raw_translations["15:1281:0"] == raw_translations["15:1282:0"]
    ):
        raise RuntimeError(
            "segment 881 attacker/victim tunneling viewpoints collapsed"
        )
    joined = "\n".join(translations.values())
    for required in ("간자를 붙잡아", "이(가) 벌인", "밀명이었다니", "땅굴 공략"):
        if required not in joined:
            raise RuntimeError(f"segment 881 terminology drifted: {required}")
    if any(term in joined for term in ("두더지 공격", "갱도 공격", "금굴중")):
        raise RuntimeError("segment 881 retained forbidden tunneling terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 881 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S881",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "excluded_nonvisible_decisions": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
                "dynamic_runtime_review_pending": len(rows),
                "exact_tunneling_result_pairs": 2,
                "distinct_tunneling_viewpoints": 2,
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
