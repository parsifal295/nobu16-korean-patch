#!/usr/bin/env python3
"""Build source-redacted PK B129 segment 1393 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2162:1",
    "15:2163:2",
    "15:2169:1",
    "15:2175:3",
    "15:2176:2",
    "15:2180:2",
    "15:2182:0",
    "15:2184:2",
)
TRANSLATIONS = {
    "15:2162:1": "을(를) 건의",
    "15:2163:2": "고려해 주시길 바라고",
    "15:2169:1": "을(를) 추진하고자 하오",
    "15:2175:3": "?",
    "15:2176:2": "?",
    "15:2180:2": "?",
    "15:2182:0": "소문에 따르면,",
    "15:2184:2": "?",
}
TARGET_RECORD_IDS = (
    2162,
    2163,
    2169,
    2175,
    2176,
    2180,
    2182,
    2184,
)
EXPECTED_ARITY = {
    2162: 2,
    2163: 3,
    2169: 2,
    2175: 4,
    2176: 3,
    2180: 3,
    2182: 2,
    2184: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2162:0",
    "15:2163:0",
    "15:2163:1",
    "15:2169:0",
    "15:2175:0",
    "15:2175:1",
    "15:2175:2",
    "15:2176:0",
    "15:2176:1",
    "15:2180:0",
    "15:2180:1",
    "15:2182:1",
    "15:2184:0",
    "15:2184:1",
)
PREFILL_COMPANION_DONOR = {
    "15:2162:0": "15:2132:0",
    "15:2163:0": "15:2133:0",
    "15:2163:1": "15:2133:1",
    "15:2169:0": "15:2139:0",
    "15:2175:0": "15:2145:0",
    "15:2175:1": "15:2145:1",
    "15:2175:2": "15:2145:2",
    "15:2176:0": "15:2146:0",
    "15:2176:1": "15:2146:1",
    "15:2180:0": "15:2150:0",
    "15:2180:1": "15:2150:1",
    "15:2182:1": "15:2152:1",
    "15:2184:0": "15:2154:0",
    "15:2184:1": "15:2154:1",
}
EXACT_BASE_DONOR = {
    2162: (15, 2132),
    2163: (15, 2133),
    2169: (15, 2139),
    2175: (15, 2145),
    2176: (15, 2146),
    2180: (15, 2150),
    2182: (15, 2152),
    2184: (15, 2154),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    2162: (),
    2163: (),
    2169: ((15, 2139),),
    2175: (),
    2176: (),
    2180: (),
    2182: ((15, 2152),),
    2184: ((15, 2154),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2162: ((466,), ("025032",)),
    2163: ((1174, 190), ("026432",)),
    2169: ((), ("026432",)),
    2175: ((526, 148), ("025032",)),
    2176: ((8, 1090), ("025032",)),
    2180: ((628, 1090), ("025032",)),
    2182: ((), ("025032",)),
    2184: ((376, 148), ("025032",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1393,
    queue_start=134,
    queue_stop=198,
    slice_first="15:2159:1",
    slice_last="15:2192:0",
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
    source_call_roots=(
        8,
        148,
        190,
        376,
        466,
        526,
        628,
        1090,
        1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2095, 2193)
    ),
    speaker_style=(
        (2162, "formal_postwar_outlook_proposal"),
        (2163, "formal_parallel_siege_consideration"),
        (2169, "formal_unassigned_siege_proposal"),
        (2175, "formal_incident_details_report_offer"),
        (2176, "humble_house_incident_report_offer"),
        (2180, "formal_disturbance_investigation_report_offer"),
        (2182, "polite_rumor_introduction"),
        (2184, "formal_hearsay_incident_report_offer"),
    ),
    terminology_policy=(
        ("battle", "싸움"),
        ("siege", "공략"),
        ("petition", "건의"),
        ("carry forward", "추진"),
        ("incident", "사건"),
        ("circumstances", "경위"),
        ("disturbance", "소동"),
        ("our clan", "우리 가문"),
        ("rumor", "소문"),
        ("hearsay", "풍문"),
        ("report", "보고"),
        ("project ellipsis", "……"),
        ("particle compatibility", "을(를)"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B129 queue ordinals one hundred "
        "thirty-four through one hundred ninety-seven and the approved Base "
        "prefill; pristine PK JP is authoritative and every populated EN, "
        "SC and TC same-record fragment array was reviewed as auxiliary "
        "context; all eight complete records reuse approved completed Base "
        "Korean assemblies selected by raw, literal and operand-masked "
        "source identity with explicit exact donors exactly thirty record "
        "positions earlier; Base runtime and VM state are never inherited; "
        "battles, sieges, petitions, proposals, incidents, circumstances, "
        "disturbances, our clan, rumors, hearsay and reports retain "
        "established historical project wording and each formal, humble or "
        "polite speaker register; direct calls, inline force, siege subject "
        "and incident tokens, colour tags, protected outer whitespace, "
        "newlines, gaps, literal arity, particles, ellipses, terminators, "
        "all fourteen same-record prefills, all fifty-six slice prefills, "
        "complete assemblies, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, reciprocal S1391 and "
        "S1392 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=8,
    pins={
        "expected_queue_universe_sha256": (
            "F5127697934EECF67CA96B604FB9F3850C0D9CFECE475F6E739976A7AD94C82F"
        ),
        "expected_queue_slice_sha256": (
            "C0F8C98575EA6769C10658C9B60B12BD001348B792356AE366E9DD55391611B5"
        ),
        "expected_prefilled_coordinate_sha256": (
            "5D783E594CD9255A42B04C8687746BACF4234D80248E3C3859FB306519304E55"
        ),
        "expected_prefill_slice_context_sha256": (
            "5CC4C5C35C3711B1EADEC81866B296CC5B84A48B376D9E9CD3B275EC04F6C25F"
        ),
        "expected_target_coordinate_sha256": (
            "B5739D5D1FDE9E91CDC1493A186B1A339E65C6D94340DEC1251E2B8EC1ADBBB7"
        ),
        "expected_source_target_sha256": (
            "962396C0F995B169CA35259957145C99C76EEA46AE9AB6F68499DA4EFEFE11C4"
        ),
        "expected_current_target_sha256": (
            "B9F9D52753B54D2F7729A0C9B0095884B34A76893230905B3A08D3F0176A9062"
        ),
        "expected_context_corpus_sha256": (
            "E23067481BCC46DA87141359397BC4FB74DA070BE265688336D50FFA1A9E30B8"
        ),
        "expected_gap_contract_sha256": (
            "D7E2367CC4ECEF5D0ADA574D50B4C5E06E5E1138E7F7668723A3DAE3E2E264FB"
        ),
        "expected_boundary_sha256": (
            "684E72028B7D0492A2A9B0BD85CFAD1A3F6156F426BFECD3D5C0989F81B09928"
        ),
        "expected_runtime_control_sha256": (
            "A65ABE2FCCD8E7B8A06380B44DD5D4A705EAA01CCF7C3E8BF89D5CA506F6DCAF"
        ),
        "expected_base_search_sha256": (
            "48215D362FB06CFD50C3F87CF2E8FE1A2CA7A50C00606E74E7F78F4FAE7807CB"
        ),
        "expected_complete_assembly_sha256": (
            "934ECCFA46CEA8F8A0A8F58156A34CFC50FCBBF380F21ABA0D38B3DB4CD1953D"
        ),
        "expected_call_graph_sha256": (
            "303AD6F09F49E5993F859C3867F8940B03AC1881F3AC74F8315F2BB66255F0CB"
        ),
        "expected_speaker_style_sha256": (
            "5FF67B0D8E896D7CAA82B9BA2C4305EBA7FF2DD0DF8EFB589845D8C8C2EC1239"
        ),
        "expected_terminology_policy_sha256": (
            "AF97F93A4A493ACB092A9C123B7C3826663F8E32D5E3E682404A1916720CF5ED"
        ),
        "expected_translation_policy_sha256": (
            "0BCFD2DD7D684895CB5C4B6E69BBB199A6B9069578B899AA929298BC7C8F84A2"
        ),
        "expected_candidate_sha256": (
            "32D1CA5F48C184E585BEBDFDCF21C15A96A795BBED9BE9DD43433AD285FA1AD8"
        ),
        "expected_combined_slice_candidate_sha256": (
            "2A439D81B1C60AFE155542657A1ED3BEB776431C24A0ED8310CA0E31BCFFF56F"
        ),
        "expected_combined_changed_literal_count": 61,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B129_S1393",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1393.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1391.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1392.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B129",
    "queue_row_count": 98,
    "queue_visible_count": 198,
    "queue_first": "15:2095:0",
    "queue_last": "15:2192:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
