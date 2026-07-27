#!/usr/bin/env python3
"""Build source-redacted PK B121 segment 1367 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

DEVELOPMENT_RECORD_IDS = tuple(range(1400, 1409))
DEVELOPMENT_MATCHES = tuple((15, record_id) for record_id in range(1370, 1394))

TARGET_COORDINATES = (
    tuple(
        f"15:{record_id}:{literal_index}"
        for record_id in DEVELOPMENT_RECORD_IDS
        for literal_index in (0, 4)
    )
    + (
        "15:1409:0",
        "15:1409:1",
        "15:1409:2",
        "15:1410:0",
        "15:1410:1",
        "15:1410:2",
        "15:1411:0",
        "15:1412:2",
        "15:1414:0",
        "15:1414:1",
        "15:1415:0",
        "15:1415:1",
    )
)
TRANSLATIONS = {
    **{
        f"15:{record_id}:{literal_index}": (
            "에서" if literal_index == 0 else "의 인망"
        )
        for record_id in DEVELOPMENT_RECORD_IDS
        for literal_index in (0, 4)
    },
    "15:1409:0": "\u00b7",
    "15:1409:1": '의 군 특성 "',
    "15:1409:2": '"이(가) 성장',
    "15:1410:0": "이(가)",
    "15:1410:1": "에서 벌인",
    "15:1410:2": "에 성공",
    "15:1411:0": "우리",
    "15:1412:2": "인가",
    "15:1414:0": "은(는)",
    "15:1414:1": "(이)라 하오\n",
    "15:1415:0": "은(는)",
    "15:1415:1": "(이)라 하오\n",
}
TARGET_RECORD_IDS = DEVELOPMENT_RECORD_IDS + (
    1409,
    1410,
    1411,
    1412,
    1414,
    1415,
)
EXPECTED_ARITY = {
    **{record_id: 5 for record_id in DEVELOPMENT_RECORD_IDS},
    **{
        record_id: 3
        for record_id in (1409, 1410, 1411, 1412, 1414, 1415)
    },
}
PREFILL_COMPANION_COORDINATES = (
    tuple(
        f"15:{record_id}:{literal_index}"
        for record_id in DEVELOPMENT_RECORD_IDS
        for literal_index in (1, 2, 3)
    )
    + (
        "15:1411:1",
        "15:1411:2",
        "15:1412:0",
        "15:1412:1",
        "15:1414:2",
        "15:1415:2",
    )
)
PREFILL_COMPANION_DONOR = {
    **{
        f"15:{record_id}:{literal_index}": f"15:1370:{literal_index}"
        for record_id in DEVELOPMENT_RECORD_IDS
        for literal_index in (1, 2, 3)
    },
    "15:1411:1": "15:1396:1",
    "15:1411:2": "15:1396:2",
    "15:1412:0": "15:1397:0",
    "15:1412:1": "15:1397:1",
    "15:1414:2": "15:346:2",
    "15:1415:2": "15:347:2",
}
EXACT_BASE_DONOR = {
    **{record_id: (15, 1370) for record_id in DEVELOPMENT_RECORD_IDS},
    1409: (15, 1394),
    1410: (15, 1395),
    1411: (15, 1396),
    1412: (15, 1397),
    1414: (15, 1399),
    1415: (15, 1400),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in DEVELOPMENT_RECORD_IDS},
    1409: ((15, 1394),),
    1410: ((15, 1395),),
    1411: (),
    1412: (),
    1414: ((15, 346), (15, 1399), (15, 1417)),
    1415: ((15, 347), (15, 1400), (15, 1418)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{
        record_id: DEVELOPMENT_MATCHES
        for record_id in DEVELOPMENT_RECORD_IDS
    },
    1409: ((15, 1394),),
    1410: ((15, 1395),),
    1411: ((15, 1396),),
    1412: ((15, 1397),),
    1414: ((15, 346), (15, 1399), (15, 1417)),
    1415: ((15, 347), (15, 1400), (15, 1418)),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{
        record_id: ((538, 628, 1, 610), ("029632", "02BE32"))
        for record_id in DEVELOPMENT_RECORD_IDS
    },
    1409: ((), ("029632", "02BE32")),
    1410: ((), ("024633", "029632", "023C")),
    1411: ((1078,), ("02463F",)),
    1412: ((178, 1048, 610), ()),
    1414: ((1, 8), ("024633",)),
    1415: ((1, 8), ("024633",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1367,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1400:0",
    slice_last="15:1416:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(538, 628, 1, 610, 1078, 178, 1048, 8),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1390, 1426)
    ),
    speaker_style=(
        tuple(
            (
                record_id,
                "emphatic_county_development_success",
            )
            for record_id in DEVELOPMENT_RECORD_IDS
        )
        + (
            (1409, "system_county_trait_growth"),
            (1410, "system_county_development_success"),
            (1411, "formal_ronin_employment_proposal"),
            (1412, "formal_frontline_ronin_employment_proposal"),
            (1414, "archaic_ronin_service_declaration"),
            (1415, "archaic_ronin_hegemony_declaration"),
        )
    ),
    terminology_policy=(
        ("county", "군"),
        ("county trait", "군 특성"),
        ("develop", "개척"),
        ("popularity", "인망"),
        ("ronin", "낭인"),
        ("employ", "등용"),
        ("hegemony", "패업"),
        ("warrior", "무사"),
        ("dynamic subject particle", "이(가), 은(는)"),
        ("dynamic object particle", "을(를)"),
        ("project middle dot", "\u00b7"),
        ("project ellipsis", "……"),
        ("project quote", '"'),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B121 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all fifteen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by literal, operand-masked and where available raw source "
        "identity, while the exact donor is fixed explicitly when duplicate "
        "records exist; Base runtime and VM state are never inherited; "
        "counties, county traits, development, popularity, ronin employment, "
        "warrior service and hegemony retain established historical project "
        "wording and formal, archaic or system registers; calls, dynamic "
        "officer, county and faction tokens, protected outer whitespace, "
        "line breaks, middle dots, quotes, ellipses, terminators, complete "
        "record arity, all thirty-seven slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=8,
    pins={
        "expected_queue_universe_sha256": (
            "E0DCC642542229DF2D59AE5B9CF620BF65B79C0C779075E71922EB0C2D1919EA"
        ),
        "expected_queue_slice_sha256": (
            "50CAF4B78FF11390A53EB54E9B519BF8305BBB951F7251B0D704E35647A8CDF6"
        ),
        "expected_prefilled_coordinate_sha256": (
            "1DC8DDE210D047581D0D56BF355B2AF575E5BD1BAA464BBD580D159AEBF0227E"
        ),
        "expected_prefill_slice_context_sha256": (
            "086275E1E3AD94B93163C637BCC127C6DF9A1EE7E8CBAF5C13DF6F28AC311C10"
        ),
        "expected_target_coordinate_sha256": (
            "DCF749B86E08DFC39462301742324AF3E0B072D305363D809D8E91E102F21EDA"
        ),
        "expected_source_target_sha256": (
            "EE62497C0C84682300724A841DA9E40C74C32ABC68C53C3C87C39AF1854AD3F3"
        ),
        "expected_current_target_sha256": (
            "18C34F410DAD6913DEDEB6EB002C98DA65495407321B389A6EE3D104872ABA4C"
        ),
        "expected_context_corpus_sha256": (
            "C910BF86586144338EA332B83DB8FC645C0A85429B0EC5F87253A347DDC58E42"
        ),
        "expected_gap_contract_sha256": (
            "C63D127F1632502629024299E60641BD767AB3E852DEF69D2F7BD32DE948630D"
        ),
        "expected_boundary_sha256": (
            "223C5A16930FEBA84A1A9977E427CBA9A7D021792D796C5E049CB0247043F4BF"
        ),
        "expected_runtime_control_sha256": (
            "203100E162BDFC0B3271B821F731A45B01F872B683033F54EACFDC819E77DA61"
        ),
        "expected_base_search_sha256": (
            "8B9F40E3BABD98FFF8B3672F2BB8CC470F491304FA0409E37C1B14F10EB852C4"
        ),
        "expected_complete_assembly_sha256": (
            "18E012B1768E643C3C88AC6AA09610D53F12C2750A77DB5826AC66EE70A4804A"
        ),
        "expected_call_graph_sha256": (
            "967845FA17D842559DB4805C9A55AD4D7679BCE3CB582D50E15E030F08571AFF"
        ),
        "expected_speaker_style_sha256": (
            "474FADB344FF53C146496A19EE2C8C1C3F254B41C5A0DFCA0342D9E8135C8B88"
        ),
        "expected_terminology_policy_sha256": (
            "773072F1C97FE0F6033FEBF16050A29A606F319375C13E871F5491C5EC08A7EF"
        ),
        "expected_translation_policy_sha256": (
            "6836036785E8A7CE00897E95006429AEDBFB0E5F08C6FC5EB271A459488EC85E"
        ),
        "expected_candidate_sha256": (
            "0769874AC26D48069CAC1C95D1F32A0C705F7BF257184D943747970F54BD210D"
        ),
        "expected_combined_slice_candidate_sha256": (
            "635E0D94DB2088F2ABE016F00BF727384BB20036D839967EB1B20B47FA263E6C"
        ),
        "expected_combined_changed_literal_count": 45,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B121_S1367",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1367.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1368.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1369.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B121",
    "queue_row_count": 67,
    "queue_visible_count": 199,
    "queue_first": "15:1400:0",
    "queue_last": "15:1466:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
