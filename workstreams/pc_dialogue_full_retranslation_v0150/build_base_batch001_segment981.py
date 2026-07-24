#!/usr/bin/env python3
"""Build Base authoring segment 981 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment980 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S981.private.v1.jsonl"
)
SEGMENT = 981
CASTLE_TOKEN = "026432"
FACILITY_TOKEN = "023C"
COUNT_TOKEN = "0232"
DESTINATION_TOKEN = "029633"
SINGLE_REBUILD_TRANSLATION = (
    "의",
    "을(를)\n정세에 맞추어\n다시 짓고자",
)
MULTIPLE_REBUILD_TRANSLATION = (
    "의",
    "등의",
    "개 시설을\n정세에 맞추어\n다시 짓고자",
)
TRANSFER_PROPOSAL = "(으)로\n전봉하는 것은"
TRANSLATIONS_BY_RECORD = {
    2268: ("",),
    2269: (
        "지시받은 방침에 따라\n개축을 시행하고자 하므로\n성하 시설 정리",
        "허가를…",
    ),
    2270: SINGLE_REBUILD_TRANSLATION,
    2271: SINGLE_REBUILD_TRANSLATION,
    2272: MULTIPLE_REBUILD_TRANSLATION,
    2273: MULTIPLE_REBUILD_TRANSLATION,
    2274: MULTIPLE_REBUILD_TRANSLATION,
    2275: (
        "의",
        "을(를) 철거",
    ),
    2276: (
        "의",
        "등의",
        "개 시설을 철거",
    ),
    2277: (
        "전선으로 전봉되기를 바라는 자가",
        "\n일손이 부족한",
        TRANSFER_PROPOSAL,
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:2268:0": ""}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
SINGLE_REBUILD_JP = (
    "の",
    "を\n時勢にあわせ\n建て直したく",
)
MULTIPLE_REBUILD_JP = (
    "の",
    "など",
    "施設を\n時勢にあわせ\n建て直したく",
)
EXPECTED_BASE_JP = {
    2268: ("",),
    2269: (
        "指示された方針に従い\n建て替えを実施したいため\n城下施設整理の",
        "許可を…",
    ),
    2270: SINGLE_REBUILD_JP,
    2271: SINGLE_REBUILD_JP,
    2272: MULTIPLE_REBUILD_JP,
    2273: MULTIPLE_REBUILD_JP,
    2274: MULTIPLE_REBUILD_JP,
    2275: ("の", "を撤去"),
    2276: ("の", "など", "施設を撤去"),
    2277: (
        "前線への転封を望む者が",
        "\n人手不足の",
        "へ\n転封しては",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
SINGLE_REBUILD_GAPS = (
    CASTLE_TOKEN,
    FACILITY_TOKEN,
    "0143E2000000050505",
)
MULTIPLE_REBUILD_GAPS = (
    CASTLE_TOKEN,
    FACILITY_TOKEN,
    COUNT_TOKEN,
    "0143E2000000050505",
)
EXPECTED_BASE_GAPS = {
    2268: ("", "050505"),
    2269: ("", "01438A040000", "050505"),
    2270: SINGLE_REBUILD_GAPS,
    2271: SINGLE_REBUILD_GAPS,
    2272: MULTIPLE_REBUILD_GAPS,
    2273: MULTIPLE_REBUILD_GAPS,
    2274: MULTIPLE_REBUILD_GAPS,
    2275: (CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    2276: (CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    2277: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "0143B0020000014356020000050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2269: ("", "014396040000", "050505"),
    2277: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "0143BC020000014362020000050505",
    ),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2269:1"}
SHARED_AUXILIARY = {
    ("SC", 2268): (("",), ("", "050505")),
    ("TC", 2268): (("",), ("", "050505")),
    ("SC", 2269): (
        ("为了依照指示的方针进行重建，\n请允许对城下设施进行清理。",),
        ("", "050505"),
    ),
    ("TC", 2269): (
        ("為了依照所指示的方針，進行重建，\n請允許整理城下設施。",),
        ("", "050505"),
    ),
    ("SC", 2270): (
        ("依现在的战况看来，\n", "的", "\n应变更为", "吧。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "023D", "050505"),
    ),
    ("TC", 2270): (
        ("依現在的戰況看來，\n", "的", "\n應變更為", "吧。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "023D", "050505"),
    ),
    ("SC", 2271): (
        ("为顺应情势变化，\n将", "的", "\n重建为", "如何？"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "023D", "050505"),
    ),
    ("TC", 2271): (
        ("為順應情勢變化，\n將", "的", "\n重建為", "如何？"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "023D", "050505"),
    ),
    ("SC", 2272): (
        ("的", "等", "设施，\n差不多是时候重建了。"),
        (CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("TC", 2272): (
        ("該順應時勢重建", "的\n", "等", "設施了。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("SC", 2273): (
        ("的", "等", "设施，\n差不多是时候重建了。"),
        (CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("TC", 2273): (
        ("該順應時勢重建", "的\n", "等", "設施了。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("SC", 2274): (
        ("的", "等", "设施，\n差不多是时候重建了。"),
        (CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("TC", 2274): (
        ("該順應時勢重建", "的\n", "等", "設施了。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("SC", 2275): (
        ("将", "的", "改建为", "。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "023D", "050505"),
    ),
    ("TC", 2275): (
        ("將", "的", "改建為", "。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "023D", "050505"),
    ),
    ("SC", 2276): (
        ("拆除", "的", "等", "处设施。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("TC", 2276): (
        ("拆除", "的", "等", "處設施。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("SC", 2277): (
        ("有人愿转封至前线。\n转封至人手不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2277): (
        ("有人願轉封至前線。\n轉封至人手不足的", "\n如何？"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2268: (("",), ("", "050505")),
    2269: (
        (
            "I would like to change the facilities within the castle town as "
            "stipulated in the plan. May I have permission to do so?",
        ),
        ("", "050505"),
    ),
    2270: (
        (
            "I would like to reconstruct ",
            " in ",
            " to better match our current situation.",
        ),
        ("", FACILITY_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2271: (
        (
            "I would like to reconstruct ",
            " in ",
            " to better match our current situation.",
        ),
        ("", FACILITY_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2272: (
        (
            "I would like to reconstruct ",
            " facilities in ",
            ", including ",
            ", to better match our current situation.",
        ),
        ("", COUNT_TOKEN, CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    ),
    2273: (
        (
            "I would like to reconstruct ",
            " facilities in ",
            ", including ",
            ", to better match our current situation.",
        ),
        ("", COUNT_TOKEN, CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    ),
    2274: (
        (
            "I would like to reconstruct ",
            " facilities in ",
            ", including ",
            ", to better match our current situation.",
        ),
        ("", COUNT_TOKEN, CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    ),
    2275: (
        (" in ", " has been dismantled."),
        (FACILITY_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2276: (
        (" facilities in ", ", including ", ", have been dismantled."),
        (COUNT_TOKEN, CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    ),
    2277: (
        (
            "There is an officer wishing to be relocated to the front lines. ",
            " lacks sufficient personnel, so what do you think of moving them "
            "there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_C_pristine_base_pc_jp_authoritative_"
    "castle_town_facility_reorganization_rebuilding_dismantling_and_front_"
    "line_relocation_with_explicit_base2268_2277_to_pk2299_2308_plus31_"
    "mapping_exact_base_pk_jp_sc_tc_literals_actual_pk_en_auxiliary_"
    "context_城下施設_as_seongha_facility_建て替え_as_gaechuk_"
    "建て直す_as_dasi_jitda_撤去_as_cheolgeo_転封_as_jeonbong_"
    "exact_2270_2271_and_2272_2274_tuple_object_reuse_など_as_deungui_"
    "dynamic_castle_facility_count_destination_token_direction_hidden_"
    "empty2268_project_ellipsis_pair_morphology_terminal_corpora_current_"
    "line_counts_and_protected_skeleton_preserved_runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    178: ("있습니다", "있다", "있사옵니다"),
    226: (
        "생각합니다",
        "생각한다",
        "생각하오",
        "생각하옵니다",
        "생각하옵나이다",
    ),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 981 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 981 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2269, 2277}:
        raise RuntimeError("segment 981 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 981 pristine/current gap drifted")
    if (
        TRANSLATIONS_BY_RECORD[2270] is not TRANSLATIONS_BY_RECORD[2271]
        or EXPECTED_BASE_JP[2270] is not EXPECTED_BASE_JP[2271]
        or EXPECTED_BASE_GAPS[2270] is not EXPECTED_BASE_GAPS[2271]
    ):
        raise RuntimeError("segment 981 exact 2270/2271 reuse drifted")
    if (
        TRANSLATIONS_BY_RECORD[2272] is not TRANSLATIONS_BY_RECORD[2273]
        or TRANSLATIONS_BY_RECORD[2272] is not TRANSLATIONS_BY_RECORD[2274]
        or EXPECTED_BASE_JP[2272] is not EXPECTED_BASE_JP[2273]
        or EXPECTED_BASE_JP[2272] is not EXPECTED_BASE_JP[2274]
        or EXPECTED_BASE_GAPS[2272] is not EXPECTED_BASE_GAPS[2273]
        or EXPECTED_BASE_GAPS[2272] is not EXPECTED_BASE_GAPS[2274]
    ):
        raise RuntimeError("segment 981 exact 2272/2273/2274 reuse drifted")
    if (
        EXPECTED_BASE_GAPS[2270][:2] != (CASTLE_TOKEN, FACILITY_TOKEN)
        or EXPECTED_BASE_GAPS[2272][:3]
        != (CASTLE_TOKEN, FACILITY_TOKEN, COUNT_TOKEN)
        or EXPECTED_BASE_GAPS[2277][2] != DESTINATION_TOKEN
    ):
        raise RuntimeError("segment 981 dynamic token direction drifted")
    joined = "\n".join(translations.values())
    for required in (
        "성하 시설 정리",
        "개축",
        "다시 짓",
        "철거",
        "전봉",
        "등의",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 981 terminology drifted: {required}")
    for forbidden in ("따위", "철수", "퇴각", "撤", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 981 forbidden wording retained: {forbidden}")
    if "시세" in joined:
        raise RuntimeError("segment 981 時勢 market-price mistranslation retained")
    if any(
        raw_translations[f"15:{record_id}:1"] != "등의"
        for record_id in (2272, 2273, 2274)
    ):
        raise RuntimeError("segment 981 など translation drifted")
    if (
        "개축" not in raw_translations["15:2269:0"]
        or any(
            "다시 짓" not in raw_translations[f"15:{record_id}:{literal_id}"]
            for record_id, literal_id in (
                (2270, 1),
                (2271, 1),
                (2272, 2),
                (2273, 2),
                (2274, 2),
            )
        )
    ):
        raise RuntimeError("segment 981 rebuilding distinction drifted")
    if (
        any(
            not raw_translations[f"15:{record_id}:2"].startswith(
                "개 시설을\n정세에 맞추어\n"
            )
            for record_id in (2272, 2273, 2274)
        )
        or raw_translations["15:2276:2"] != "개 시설을 철거"
    ):
        raise RuntimeError("segment 981 numeric facility classifier drifted")
    if (
        raw_translations["15:2277:2"] != TRANSFER_PROPOSAL
        or "어떻겠소" in raw_translations["15:2277:2"]
        or SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[2277][3])
        != (688, 598)
        or SUPPORT.morphology_operands(EXPECTED_PK_JP_GAPS[2277][3])
        != (700, 610)
    ):
        raise RuntimeError("segment 981 dynamic transfer proposal ending drifted")
    if (
        raw_translations["15:2269:1"].count("…") != 1
        or translations["15:2269:1"].count("…") != 2
    ):
        raise RuntimeError("segment 981 ellipsis pair drifted")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 981 visible decision count drifted")


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
        skip_records={2268},
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 981 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 981 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S981",
                "source_literal_count": 24,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "runtime_fragment_pending": len(rows),
                "exact_translation_groups": [[2270, 2271], [2272, 2273, 2274]],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2269, 2277],
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
