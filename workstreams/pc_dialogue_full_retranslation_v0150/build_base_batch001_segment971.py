#!/usr/bin/env python3
"""Build Base authoring segment 971 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment970 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S971.private.v1.jsonl"
)
SEGMENT = 971
CASTLE_TOKEN = "026432"
FACILITY_COMPLETION_CANONICAL = (
    "군 시설이 완성되어,",
    "에\n새로운 시설을 건설할 수 있게 되",
)
TRANSLATIONS_BY_RECORD = {
    2160: (
        "취락을 지배하게 되어\n",
        "에 새 시설을\n착공할 수 있게 되었",
    ),
    2161: (
        "에서 새 시설을\n건설할 수 있게 되었다 하오…\n"
        "취락 지배를 진척시킨 덕택",
    ),
    2162: (
        "의 성하 마을에서\n취락 지배가 진척되어\n"
        "새 시설을 건설할 수 있게 된 모양",
    ),
    2163: (
        "아무래도",
        "에 새 시설을\n지을 수 있을 모양",
        "!",
    ),
    2164: (
        "군 시설이 완성되어,",
        "에서 새로운\n시설을 지을 수 있게 되었다 하옵니다!",
    ),
    2165: (
        "각 군의 시설을 정비한 덕분에,",
        "에도\n새 시설을 건설할 수 있게 된 모양…",
    ),
    2166: FACILITY_COMPLETION_CANONICAL,
    2167: (
        "에 새로운 종류의 시설을\n건설할 수 있게 되었다 하옵니다!",
    ),
    2168: (
        "각 군의 시설이 갖춰",
        "\n이로써",
        "에 새로운 시설도\n건설할 수 있을 터…",
    ),
    2169: (
        "각 군의 시설이 완성되어,",
        "에\n새로운 시설을 건설할 수 있게 된 듯",
    ),
    2170: (
        "듣자 하니",
        "에 새 시설을\n건설할 수 있게 된 모양이구려",
    ),
    2171: (
        "군 시설이 갖춰진 덕분에",
        "에도\n새 시설을 지을 수 있게 되었다는군요?",
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
    2160: ("集落の支配に伴い\n", "に新たな施設が\n着工可能とな"),
    2161: (
        "で新たな施設が\n建設できるようになったとか…\n"
        "集落の支配を進めた賜物",
    ),
    2162: (
        "の城下町にて\n集落の支配が進み\n"
        "新たな施設が建設可能になった模様",
    ),
    2163: ("どうやら", "に、新しい施設が\n作れそう", "！"),
    2164: ("郡施設の完成により、", "で新たな\n施設が作れるとのこと！"),
    2165: (
        "各郡の施設が整ったことで、",
        "にも\n新しい施設が建設可能となった模様…",
    ),
    2166: (
        "郡の施設が完成したことで、",
        "に\n新たな施設が建設できるようにな",
    ),
    2167: ("に新しい種類の施設が\n建設できるようになったとのこと！",),
    2168: (
        "各郡の施設が整",
        "\nこれで",
        "に新しい施設の建設も\n可能となるはず…",
    ),
    2169: (
        "各郡の施設が完成し、",
        "に\n新たな施設が建設可能となったよう",
    ),
    2170: ("何やら", "に新しい施設が\n建設できるようになったようじゃ"),
    2171: (
        "郡の施設が整ったことで",
        "にも\n新しい施設を建てられるようですよ？",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2160: ("", CASTLE_TOKEN, "014368020000050505"),
    2161: (CASTLE_TOKEN, "01434A020000050505"),
    2162: (CASTLE_TOKEN, "050505"),
    2163: ("", CASTLE_TOKEN, "01431A0200000143F6010000", "050505"),
    2164: ("", CASTLE_TOKEN, "050505"),
    2165: ("", CASTLE_TOKEN, "050505"),
    2166: ("", CASTLE_TOKEN, "0143680200000143F6010000050505"),
    2167: (CASTLE_TOKEN, "050505"),
    2168: ("", "01436E0200000143C8020000", CASTLE_TOKEN, "050505"),
    2169: ("", CASTLE_TOKEN, "01431A020000050505"),
    2170: ("", CASTLE_TOKEN, "050505"),
    2171: ("", CASTLE_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2160: ("", CASTLE_TOKEN, "014374020000050505"),
    2161: (CASTLE_TOKEN, "014356020000050505"),
    2163: ("", CASTLE_TOKEN, "0143260200000143FC010000", "050505"),
    2166: ("", CASTLE_TOKEN, "0143740200000143FC010000050505"),
    2168: ("", "01437A0200000143D4020000", CASTLE_TOKEN, "050505"),
    2169: ("", CASTLE_TOKEN, "014326020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2161:0",
    "15:2165:1",
    "15:2168:2",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2160): (
        ("随着对聚落的掌控，\n可在", "建设的新设施\n已经可以动工了。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2160): (
        ("隨著對聚落的掌控，\n可在", "建設的新設施\n已經可以動工了。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2161): (
        ("已经可以在", "\n建设新设施了……\n都是拜掌控聚落所赐啊。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2161): (
        ("已經可以在", "\n建設新設施了……\n都是拜掌控聚落所賜啊。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2162): (
        ("似乎是因为", "城下町中的\n郡村落增加了，\n所以可以建设新的设施了。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2162): (
        ("由於郡村落的支配，", "的\n城下町將可建設新的設施。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2165): (
        ("由于各郡的设施都已齐全，\n看来也可在", "建新设施了……"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2165): (
        ("因各郡的設施已整備，\n", "似乎也可建設新設施了……"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2166): (
        ("由于郡的设施已完成，\n也可在", "新建设了呢！"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2166): (
        ("因郡的設施已完成，\n故已可開始於", "建設新的設施。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2167): (
        ("看来能够在", "\n建设新种类的设施了！"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2167): (
        ("聽說在", "已經能開始\n建設新的設施了！"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2171): (
        ("由于郡的设施已齐全，\n看来也可在", "建新设施了呢。？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2171): (
        ("因郡的設施已整備，\n在", "似乎也能建設新的設施？"),
        ("", CASTLE_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2160: (
        ("Control over settlements has made a new facility available to build in ", "."),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2161: (
        (
            "New facilities have become available to build in ",
            "? ThatÖs what comes from controlling settlements.",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2165: (
        (
            "Now that each county has been provided with facilities, "
            "it seems that a new facility has become available to add in ",
            ".",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2166: (
        (
            "Now that the countyÖs facilities have been completed, "
            "a new facility has become available for adding at ",
            ".",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2167: (
        ("It would seem that a new type of facility can be built at ", "!"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2171: (
        (
            "It looks like we can build a new facility at ",
            " now that the countiesÖ facilities have been set up.",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B116_C_pristine_base_pc_jp_authoritative_"
    "county_settlement_control_and_new_facility_unlock_reports_with_"
    "explicit_base2160_2171_to_pk2190_2201_mapping_exact_base_pk_jp_"
    "sc_tc_literals_dynamic_castle_token_direction_郡施設_as_gun_siseol_"
    "集落_as_chwirak_城下町_as_seongha_maeul_current_korean_morphology_"
    "terminal_corpora_all_base_pk_opcode_divergences_recorded_project_"
    "ellipsis_pairs_ascii_punctuation_current_line_counts_and_protected_"
    "skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    502: ("", "다", "여"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    586: ("이지요", "이군", "이군요", "이옵니다요", "이옵니다그려"),
    616: ("했습니다", "었다"),
    622: ("있었습니다", "었다"),
    712: ("와", "군", "네"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    508: EXPECTED_BASE_MORPHOLOGY_TERMINALS[502],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    598: EXPECTED_BASE_MORPHOLOGY_TERMINALS[586],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    634: EXPECTED_BASE_MORPHOLOGY_TERMINALS[622],
    724: EXPECTED_BASE_MORPHOLOGY_TERMINALS[712],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if TRANSLATIONS_BY_RECORD[2166] is not FACILITY_COMPLETION_CANONICAL:
        raise RuntimeError("segment 971 facility canonical tuple alias drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 971 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 971 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2160, 2161, 2163, 2166, 2168, 2169}:
        raise RuntimeError("segment 971 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 971 pristine/current gap drifted")
    if any(
        sum(gap.count(CASTLE_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 971 castle-token cardinality drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 971 project ellipsis pair drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("취락", "군 시설", "성하 마을", "착공"):
        if required not in joined:
            raise RuntimeError(
                f"segment 971 historical facility term drifted: {required}"
            )
    for forbidden in ("마을 시설", "커맨드", "。", "！"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 971 forbidden wording retained: {forbidden}"
            )
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 971 visible decision count drifted")


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
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 971 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 971 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S971",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "canonical_facility_record": 2166,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2160,
                    2161,
                    2163,
                    2166,
                    2168,
                    2169,
                ],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
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
