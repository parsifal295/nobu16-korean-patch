#!/usr/bin/env python3
"""Build Base authoring segment 847 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment824 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S847.private.v1.jsonl"
SEGMENT = 847
FAILURE_TRANSLATION = (
    "에서 잇키 선동에 실패했습니다\n"
    "송구하옵니다…"
)
DOMAIN_TRANSLATIONS = (
    "제 영지",
    "의 지배력을 확대하고자 하오니\n원조해 주실 수 없겠사옵니까",
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:840:0": "·",
    "15:840:1": "에서 잇키가 발생했습니다",
    **{f"15:{record_id}:0": FAILURE_TRANSLATION for record_id in range(841, 853)},
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(853, 858)
        for literal_id, translation in enumerate(DOMAIN_TRANSLATIONS)
    },
}
RECORD_ARITIES = {
    840: 2,
    **{record_id: 1 for record_id in range(841, 853)},
    **{record_id: 2 for record_id in range(853, 858)},
}
EXPECTED_BASE_GAPS = {
    840: ("", "029632", "050505"),
    **{record_id: ("029632", "050505") for record_id in range(841, 853)},
    **{record_id: ("", "029632", "050505") for record_id in range(853, 858)},
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {
    840: 1,
    **{record_id: 1 for record_id in range(841, 855)},
    **{record_id: 2 for record_id in range(855, 858)},
}
EXPECTED_PK_EN_GAPS = {
    **{record_id: ("", "050505") for record_id in range(840, 855)},
    **{record_id: ("", "029632", "050505") for record_id in range(855, 858)},
}
CURRENT_ELLIPSIS_COORDINATES = {
    f"15:{record_id}:0" for record_id in range(841, 853)
}
BASIS = (
    "pristine_base_pc_jp_authoritative_ikki_failure_report_outbreak_ui_and_"
    "first_person_domain_control_assistance_request_fragments_with_exact_"
    "failure_and_cross_batch_domain_source_groups_uniform_plus_7_pk_jp_sc_tc_"
    "arrays_pk_en_sc_tc_auxiliary_context_historical_polite_register_current_"
    "pc_line_token_gap_outer_whitespace_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    source_literals = COMMON.source_literals
    failure_source = (
        "で一揆の煽動に失敗しました\n申し訳ありません…",
    )
    if any(
        source_literals(source_records, record_id) != failure_source
        for record_id in range(841, 853)
    ):
        raise RuntimeError("segment 847 841-852 exact failure source group drifted")
    if len(
        {raw_translations[f"15:{record_id}:0"] for record_id in range(841, 853)}
    ) != 1:
        raise RuntimeError("segment 847 841-852 exact failure translation group drifted")

    domain_source = (
        "我が領地",
        "の支配を進める\n援助をお願いできませぬか",
    )
    if any(
        source_literals(source_records, record_id) != domain_source
        for record_id in range(853, 865)
    ):
        raise RuntimeError("segment 847 853-864 cross-batch domain source group drifted")
    for literal_id, expected in enumerate(DOMAIN_TRANSLATIONS):
        if len(
            {
                raw_translations[f"15:{record_id}:{literal_id}"]
                for record_id in range(853, 858)
            }
        ) != 1:
            raise RuntimeError(
                f"segment 847 853-857 domain translation group drifted: {literal_id}"
            )
        if raw_translations[f"15:853:{literal_id}"] != expected:
            raise RuntimeError(
                f"segment 847 domain canonical drifted: 15:853:{literal_id}"
            )

    if raw_translations["15:840:0"] != "·":
        raise RuntimeError("segment 847 UI middle dot drifted")
    joined = "\n".join(translations.values())
    for required in ("잇키 선동", "송구하옵니다", "제 영지", "지배력을 확대", "원조"):
        if required not in joined:
            raise RuntimeError(f"segment 847 terminology/register drifted: {required}")
    if any(
        term in joined
        for term in ("폭동", "반란 선동", "내 영지", "지배를 진행")
    ):
        raise RuntimeError("segment 847 retained forbidden terminology")


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
        raise RuntimeError("segment 847 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S847",
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
