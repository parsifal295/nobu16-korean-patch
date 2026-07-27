#!/usr/bin/env python3
"""Build source-redacted PK B122 segment 1372 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1514,
    1515,
    1516,
    1518,
    1519,
    1520,
    1522,
    1523,
    1524,
    1525,
    1526,
    1528,
)
TARGET_COORDINATES = (
    "15:1514:4",
    "15:1515:2",
    "15:1515:4",
    "15:1515:5",
    "15:1516:5",
    "15:1518:4",
    "15:1519:5",
    "15:1520:0",
    "15:1522:2",
    "15:1523:0",
    "15:1523:1",
    "15:1524:2",
    "15:1525:2",
    "15:1526:0",
    "15:1526:1",
    "15:1526:2",
    "15:1528:1",
    "15:1528:2",
    "15:1528:3",
)
TRANSLATIONS = {
    "15:1514:4": "?",
    "15:1515:2": "\n어디,",
    "15:1515:4": "\n상관없",
    "15:1515:5": "일까?",
    "15:1516:5": "?",
    "15:1518:4": "?",
    "15:1519:5": "?",
    "15:1520:0": "최근,",
    "15:1522:2": "인가?",
    "15:1523:0": "을(를) 비롯한",
    "15:1523:1": "명이",
    "15:1524:2": "증가",
    "15:1525:2": "증가",
    "15:1526:0": "의",
    "15:1526:1": "에",
    "15:1526:2": "을(를) 건설",
    "15:1528:1": "회복(",
    "15:1528:2": "→",
    "15:1528:3": ")",
}
EXPECTED_ARITY = {
    1514: 5,
    1515: 6,
    1516: 6,
    1518: 5,
    1519: 6,
    1520: 3,
    1522: 3,
    1523: 3,
    1524: 3,
    1525: 3,
    1526: 3,
    1528: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1514:0",
    "15:1514:1",
    "15:1514:2",
    "15:1514:3",
    "15:1515:0",
    "15:1515:1",
    "15:1515:3",
    "15:1516:0",
    "15:1516:1",
    "15:1516:3",
    "15:1516:4",
    "15:1518:0",
    "15:1518:1",
    "15:1518:3",
    "15:1519:0",
    "15:1519:1",
    "15:1519:3",
    "15:1519:4",
    "15:1520:1",
    "15:1520:2",
    "15:1522:0",
    "15:1522:1",
    "15:1523:2",
    "15:1524:0",
    "15:1524:1",
    "15:1525:0",
    "15:1525:1",
    "15:1528:0",
)
PREFILL_COMPANION_DONOR = {
    "15:1514:0": "15:1499:0",
    "15:1514:1": "15:1498:1",
    "15:1514:2": "15:1499:2",
    "15:1514:3": "15:1499:3",
    "15:1515:0": "15:1500:0",
    "15:1515:1": "15:1495:1",
    "15:1515:3": "15:1500:3",
    "15:1516:0": "15:1501:0",
    "15:1516:1": "15:1495:1",
    "15:1516:3": "15:1495:3",
    "15:1516:4": "15:1495:4",
    "15:1518:0": "15:1503:0",
    "15:1518:1": "15:1498:1",
    "15:1518:3": "15:1503:3",
    "15:1519:0": "15:1501:0",
    "15:1519:1": "15:1495:1",
    "15:1519:3": "15:1504:3",
    "15:1519:4": "15:1495:4",
    "15:1520:1": "15:1505:1",
    "15:1520:2": "15:1505:2",
    "15:1522:0": "15:1507:0",
    "15:1522:1": "15:1507:1",
    "15:1523:2": "15:1508:2",
    "15:1524:0": "15:1509:0",
    "15:1524:1": "15:1509:1",
    "15:1525:0": "15:1510:0",
    "15:1525:1": "15:1510:1",
    "15:1528:0": "15:1089:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:1516:2",
    "15:1518:2",
    "15:1519:2",
)
EXACT_BASE_DONOR = {
    1514: (15, 1499),
    1515: (15, 1500),
    1520: (15, 1505),
    1522: (15, 1507),
    1523: (15, 1508),
    1524: (15, 1509),
    1525: (15, 1510),
    1526: (15, 1511),
    1528: (15, 1089),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in (1516, 1518, 1519)
    },
    1516: (
        "15:1501:0",
        "15:1501:1",
        "15:1501:3",
        "15:1501:4",
        "15:1501:5",
    ),
    1518: (
        "15:1503:0",
        "15:1503:1",
        "15:1503:3",
        "15:1503:4",
    ),
    1519: (
        "15:1504:0",
        "15:1504:1",
        "15:1504:3",
        "15:1504:4",
        "15:1504:5",
    ),
}
DURABILITY_RECOVERY_MATCHES = (
    (15, 1089),
    (15, 1513),
)
EXPECTED_BASE_RAW_MATCHES = {
    1514: (),
    1515: (),
    1516: (),
    1518: (),
    1519: (),
    1520: (),
    1522: (),
    1523: ((15, 1508),),
    1524: ((15, 1509),),
    1525: ((15, 1510),),
    1526: ((15, 1511),),
    1528: DURABILITY_RECOVERY_MATCHES,
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1514: ((15, 1499),),
    1515: ((15, 1500),),
    1516: ((15, 1501),),
    1518: ((15, 1503),),
    1519: ((15, 1504),),
    1520: ((15, 1505),),
    1522: ((15, 1507),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    1514: ((844, 1, 292), ("023C",)),
    1515: ((844, 1, 1066, 1138), ("023C",)),
    1516: ((844, 1, 148, 292), ("023C",)),
    1518: ((844, 1, 292), ("023C",)),
    1519: ((844, 1, 148, 292), ("023C",)),
    1520: ((1, 1096), ()),
    1522: ((610,), ("02463F",)),
    1523: ((), ("024633", "0232", "023C")),
    1524: ((), ("026432", "0233")),
    1525: ((), ("026432", "0233")),
    1526: ((), ("026432", "029632", "023C")),
    1528: ((), ("026432", "0232", "0233", "0234")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1372,
    queue_start=134,
    queue_stop=199,
    slice_first="15:1514:2",
    slice_last="15:1535:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1, 148, 292, 610, 844, 1066, 1096, 1138),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(1498, 1536)
    ),
    speaker_style=(
        (1514, "confident_mentor_proposal"),
        (1515, "casual_mentor_proposal"),
        (1516, "formal_mentor_proposal"),
        (1518, "polite_mentor_proposal"),
        (1519, "formal_mentor_proposal"),
        (1520, "polite_bandit_suppression_training_proposal"),
        (1522, "deliberative_bandit_suppression_training_proposal"),
        (1523, "system_officer_promotion"),
        (1524, "system_farm_control_gain"),
        (1525, "system_market_control_gain"),
        (1526, "system_facility_construction"),
        (1528, "system_durability_recovery"),
    ),
    terminology_policy=(
        ("unit leader", "조두"),
        ("military merit", "무공"),
        ("bandit", "도적"),
        ("suppression", "토벌"),
        ("promotion", "승진"),
        ("yield", "석고"),
        ("commerce", "상업"),
        ("construction", "건설"),
        ("durability", "내구"),
        ("recovery", "회복"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic grouped officer", "을(를) 비롯한"),
        ("project question mark", "?"),
        ("project change arrow", "→"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B122 queue ordinals 134 through 198 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; nine complete records reuse approved "
        "completed Base Korean assemblies selected by raw, literal and "
        "operand-masked source identity, while three mentor records use the "
        "same Base assemblies through visible semantic references because "
        "their newline-only fragments have no promoted decision rows; Base "
        "runtime and VM state are never inherited; unit-leader, "
        "military-merit, bandit, suppression, "
        "promotion, yield, commerce, construction, durability, recovery, "
        "dynamic particles, grouped-officer wording, question marks, change "
        "arrows and each speaker register retain established project and "
        "historical terminology; direct calls, inline person, castle, "
        "facility, count, rank and numeric tokens, protected outer "
        "whitespace, newlines, gaps, literal arity, terminators, all "
        "twenty-eight same-record prefills, three hidden newline companions, "
        "all forty-six slice prefills, complete assemblies, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1370 and S1371 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=6,
    pins={
        "expected_queue_universe_sha256": (
            "681287EB7B080C5886E75BAC2DFCF0131969FF940310C498FEFB86748B5D8244"
        ),
        "expected_queue_slice_sha256": (
            "37EC05B442D5596DDA77A15CC47E206D9E32639254F95168F7183A7610AFE1A0"
        ),
        "expected_prefilled_coordinate_sha256": (
            "5A41D6290A3E903182C7D6D3646B0FB4D3633E07217E7B056F0B2E402BB9559C"
        ),
        "expected_prefill_slice_context_sha256": (
            "0AE1715448354720AEF3D6847EF5C075609BA1EA505A4E8D64E7EB55E93619D0"
        ),
        "expected_target_coordinate_sha256": (
            "51B3961FF11CABDEB8DA8246D9ECE30C702BA0724F0AF0BCD5B6C4639A8CADE6"
        ),
        "expected_source_target_sha256": (
            "0632570C5DFD4AED76B78D634F4591C42A053810CDED4E3FED831508838B2855"
        ),
        "expected_current_target_sha256": (
            "2C7EC9B435AF1126071EDA07DEFC0D6DE6F08A70E9518A938EB85F1D221EAA8F"
        ),
        "expected_context_corpus_sha256": (
            "11432A15C4EE5D21CE9924C01FB10A2BE8B8C482F0F7149C0F63A727520B20DB"
        ),
        "expected_gap_contract_sha256": (
            "3E55695EBD4DF5B41805821DFC8BC75AE466F76B09F7F2F513513D7CD6091B92"
        ),
        "expected_boundary_sha256": (
            "37D9F2BAF1556342BF912FAEEC0C6EB0A136DDE3D7D9F47086658ABC0A484737"
        ),
        "expected_runtime_control_sha256": (
            "F06EC016D1D82FDA7451F0688C347F132F33399650D4D975911198058D1E1134"
        ),
        "expected_base_search_sha256": (
            "8F72842A92B28DFCCBAC2CCBA8EF6249366DC26BBEC263DF8F41C38F5A320D26"
        ),
        "expected_complete_assembly_sha256": (
            "20BD57F6DAB0706FDAFB2F896118C304E7CE03E82AD13A95AB728F7A433AA137"
        ),
        "expected_call_graph_sha256": (
            "F4679C216C99E9FC2A3CDE3C7F6933DD568F7EED26EB58BD1240EF6A82AF3984"
        ),
        "expected_speaker_style_sha256": (
            "9D40CF13227696146FD0D09D179747CF467D313D0607D2D3558BC58DD423D010"
        ),
        "expected_terminology_policy_sha256": (
            "315771F196180C2B28FF8794828F1C3C9827A11E3E946FF0447A93C402E8D597"
        ),
        "expected_translation_policy_sha256": (
            "B643A8D3F6B7E0C72494086C111E18A8AFE2BDCDDAB50FF161EF45B19FB004AB"
        ),
        "expected_candidate_sha256": (
            "E633B66610B3405CA93C3B773727442F610E08992B2DFC4F0621A27A2BE44825"
        ),
        "expected_combined_slice_candidate_sha256": (
            "06F2086CCB16196A729A9EDF5416C83EC936D2225336B22E2D5F25B8DFBE16CE"
        ),
        "expected_combined_changed_literal_count": 41,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B122_S1372",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1372.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1370.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1371.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B122",
    "queue_row_count": 69,
    "queue_visible_count": 199,
    "queue_first": "15:1467:0",
    "queue_last": "15:1535:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
