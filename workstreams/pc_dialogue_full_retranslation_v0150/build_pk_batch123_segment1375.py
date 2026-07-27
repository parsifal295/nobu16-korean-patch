#!/usr/bin/env python3
"""Build source-redacted PK B123 segment 1375 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1583,
    1584,
    1585,
    1592,
    1604,
    1611,
    1613,
)
TARGET_COORDINATES = (
    "15:1583:0",
    "15:1584:0",
    "15:1585:2",
    "15:1592:0",
    "15:1604:0",
    "15:1611:3",
    "15:1613:0",
)
TRANSLATIONS = {
    "15:1583:0": "간자가",
    "15:1584:0": "지금이야말로",
    "15:1585:2": "공략의 호기",
    "15:1592:0": "아군의",
    "15:1604:0": "아군의",
    "15:1611:3": "……",
    "15:1613:0": "이제 여기까지……\n",
}
EXPECTED_ARITY = {
    1583: 2,
    1584: 2,
    1585: 3,
    1592: 3,
    1604: 3,
    1611: 4,
    1613: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1583:1",
    "15:1584:1",
    "15:1585:0",
    "15:1592:1",
    "15:1592:2",
    "15:1604:1",
    "15:1604:2",
    "15:1611:0",
    "15:1611:1",
    "15:1611:2",
    "15:1613:1",
)
PREFILL_COMPANION_DONOR = {
    "15:1583:1": "15:1553:1",
    "15:1584:1": "15:1554:1",
    "15:1585:0": "15:1555:0",
    "15:1592:1": "15:1562:1",
    "15:1592:2": "15:1562:2",
    "15:1604:1": "15:1574:1",
    "15:1604:2": "15:1574:2",
    "15:1611:0": "15:1581:0",
    "15:1611:1": "15:1581:1",
    "15:1611:2": "15:1581:2",
    "15:1613:1": "15:1583:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1585:1",)
EXACT_BASE_DONOR = {
    1583: (15, 1553),
    1584: (15, 1554),
    1592: (15, 1562),
    1604: (15, 1574),
    1611: (15, 1581),
    1613: (15, 1583),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 1585
    },
    1585: (
        "15:1555:0",
        "15:1555:2",
    ),
}
INVASION_LITERAL_MATCHES = (
    (15, 1562),
    (15, 1574),
)
EXPECTED_BASE_RAW_MATCHES = {
    1583: (),
    1584: ((15, 1554),),
    1585: (),
    1592: ((15, 1562),),
    1604: ((15, 1574),),
    1611: (),
    1613: ((15, 1583),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1583: ((15, 1553),),
    1585: ((15, 1555),),
    1592: INVASION_LITERAL_MATCHES,
    1604: INVASION_LITERAL_MATCHES,
    1611: ((15, 1581),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    1592: ((15, 1562),),
    1604: ((15, 1574),),
}
EXPECTED_CONTROLS_BY_RECORD = {
    1583: ((1066,), ("026432",)),
    1584: ((322,), ("026432",)),
    1585: ((634, 550), ("026432",)),
    1592: ((), ("026432", "025032")),
    1604: ((), ("029632", "025032")),
    1611: ((1090, 286), ("026432",)),
    1613: ((226,), ("026432",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1375,
    queue_start=134,
    queue_stop=199,
    slice_first="15:1583:0",
    slice_last="15:1613:1",
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
    source_call_roots=(226, 286, 322, 550, 634, 1066, 1090),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(1570, 1614)
    ),
    speaker_style=(
        (1583, "formal_spy_infiltration_report"),
        (1584, "commanding_attack_opportunity"),
        (1585, "terse_attack_opportunity"),
        (1592, "deliberative_invasion_response"),
        (1604, "deliberative_invasion_response"),
        (1611, "reluctant_attack_abort"),
        (1613, "resigned_attack_withdrawal"),
    ),
    terminology_policy=(
        ("spy", "간자"),
        ("subordinate county", "산하 군"),
        ("soldiers", "병사"),
        ("restraint", "견제"),
        ("attack", "공략"),
        ("sortie", "출진"),
        ("invasion", "침공"),
        ("repulse", "격퇴"),
        ("withdrawal", "철수"),
        ("strategy", "방책"),
        ("friendly force", "아군"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B123 queue ordinals 134 through 198 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; six complete records reuse approved "
        "completed Base Korean assemblies selected by raw, literal and "
        "operand-masked source identity, while the attack-opportunity record "
        "uses the same Base assembly through visible semantic references "
        "because its newline-only fragment has no promoted decision row; "
        "Base runtime and VM state are never inherited; spy, subordinate "
        "county, soldiers, restraint, attack, sortie, invasion, repulse, "
        "withdrawal, strategy, friendly-force wording, ellipsis and each "
        "speaker register retain established project and historical "
        "terminology; direct calls, inline castle and faction tokens, "
        "protected outer whitespace, newlines, gaps, literal arity, "
        "terminators, all eleven same-record prefills, the hidden newline, "
        "all fifty-eight slice prefills, complete assemblies, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1373 and S1374 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=4,
    pins={
        "expected_queue_universe_sha256": (
            "01F2F01C3BD54B4E74BA77C265BF140CBDBA1DF4238130C4E562422C72CE4662"
        ),
        "expected_queue_slice_sha256": (
            "4F2ED3B90AAEB1986FEB6A2CE3AC51AACA5C09EE5EB26890DB2E5AE3EF1F3CCB"
        ),
        "expected_prefilled_coordinate_sha256": (
            "6E4DA5EA2C2CC80066E70A843DF93406B458AD634FBC5EFCB7B3EF6F0CFD3EAF"
        ),
        "expected_prefill_slice_context_sha256": (
            "0AF778F2C6FE832BD5989A280F4F48CCBB4CB1ED89C7A18CD62EB496677D2808"
        ),
        "expected_target_coordinate_sha256": (
            "7199A1369656D5D8FAE6E2D782D71FFCB3532145720D60AACF57F8BB256FE5A9"
        ),
        "expected_source_target_sha256": (
            "480E008E607EA27849C95D91226D17631EB725C483BC6C32CF75523B6B0719D6"
        ),
        "expected_current_target_sha256": (
            "800D0B72C1AE3F3A092DE81BE61C885DF2D3A316001335F6AD789C2D881EAD72"
        ),
        "expected_context_corpus_sha256": (
            "8FB2668DFD7BA3E9C26775EB7540AF41F109D9406FA938F876F803E2392DDAC9"
        ),
        "expected_gap_contract_sha256": (
            "33B38F0BE04507B62B27CE9B09FFFE4D12AB80B61D70965C2BF0818DADE4521C"
        ),
        "expected_boundary_sha256": (
            "CF75A0C03E7ADE8854D76418BA745F927FFA38E9F0F39E8A64B65F51B8DC022C"
        ),
        "expected_runtime_control_sha256": (
            "5874937BE97E74743D42D84656E1888F34FD58DEA1E43D53A640116541914414"
        ),
        "expected_base_search_sha256": (
            "44F7457FF944703987B13C2BD81B05F77D7E758E091FCEB7B55122C5D11927F1"
        ),
        "expected_complete_assembly_sha256": (
            "9376CD9C4467E5CDCD6996A7D50AD2D23B00191086670B3F6CD8C6C2A9D2F3C7"
        ),
        "expected_call_graph_sha256": (
            "AF3064D8272476C98B367B24E8D2DE0812957B3BC95DF6B0F554CB349D60E58E"
        ),
        "expected_speaker_style_sha256": (
            "0AE6CBD804E7A5B32793DA76C66F389A3C44CF4398783313FFA4D5C21273B6F8"
        ),
        "expected_terminology_policy_sha256": (
            "00084BA953938F6A613DE260BA3CDAD65D8151DF1CD7DB1E60215A9CF88253B7"
        ),
        "expected_translation_policy_sha256": (
            "F74C3F6063954A9430B7E9DDBC75B6D9E585B2142EAE7B40693603223D1DB8E6"
        ),
        "expected_candidate_sha256": (
            "B70D29CAC585C1CD686E74F56AEBCC8C4F09A5763642076557EA3D5755400BE2"
        ),
        "expected_combined_slice_candidate_sha256": (
            "887BEBECEC2F6047677FF4DEC51F0887D5869B2A0247FBD5580157F2C43B6A24"
        ),
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B123_S1375",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1375.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1373.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B123_S1374.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B123",
    "queue_row_count": 78,
    "queue_visible_count": 199,
    "queue_first": "15:1536:0",
    "queue_last": "15:1613:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
