#!/usr/bin/env python3
"""Build source-redacted PK B117 segment 1355 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    985,
    986,
    987,
)
TARGET_COORDINATES = (
    "15:985:1",
    "15:985:2",
    "15:986:1",
    "15:986:2",
    "15:987:0",
    "15:987:1",
    "15:987:2",
)
TRANSLATIONS = {
    "15:985:1": "→",
    "15:985:2": "로",
    "15:986:1": "→",
    "15:986:2": "으로(로)",
    "15:987:0": "에서",
    "15:987:1": "이(가) 벌인",
    "15:987:2": "을(를) 저지",
}
EXPECTED_ARITY = {
    record_id: 3
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    "15:985:0",
    "15:986:0",
)
PREFILL_COMPANION_DONOR = {
    "15:985:0": "15:978:0",
    "15:986:0": "15:716:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ()
EXACT_BASE_DONOR = {
    985: (15, 978),
    986: (15, 716),
    987: (15, 811),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_RAW_MATCHES = {
    985: ((15, 978),),
    986: ((15, 716), (15, 979), (15, 1453)),
    987: (
        (15, 811),
        (15, 980),
        (15, 1286),
        (15, 1362),
        (15, 1454),
    ),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    986: (
        (15, 716),
        (15, 979),
        (15, 1337),
        (15, 1338),
        (15, 1453),
    ),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    985: ((), ("026432", "0232", "0233")),
    986: ((), ("026432", "0232", "0233")),
    987: ((), ("026432", "025032", "023C")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1355,
    queue_start=0,
    queue_stop=67,
    slice_first="15:985:0",
    slice_last="15:1028:1",
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
    source_call_roots=(),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(970, 1036)
    ),
    speaker_style=(
        (985, "system_castle_durability_change"),
        (986, "system_castle_troop_change"),
        (987, "system_operation_prevention"),
    ),
    terminology_policy=(
        ("castle durability", "내구"),
        ("castle troops", "병력"),
        ("numeric change arrow", "→"),
        ("numeric destination particle", "으로(로)"),
        ("operation location", "에서"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("operation prevention", "저지"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B117 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all three "
        "complete records reuse approved byte-identical Base Korean "
        "assemblies, selecting the established durability, troop and "
        "operation-prevention variants from duplicate matches; Base runtime "
        "and VM state are never inherited; durability, troops, numeric "
        "change arrows, directional and dynamic particles and prevention "
        "terminology retain established project wording; inline castle, "
        "faction, operation and old or new number tokens, protected outer "
        "whitespace, gaps, literal arity, terminators, both same-record "
        "prefills, all sixty slice prefills, complete assemblies, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=4,
    pins={
        "expected_queue_universe_sha256": (
            "6178B2BC5D4B62D163E7C89A3D7BCBB80D5797E1E57C34FFFD1BA1B718D17558"
        ),
        "expected_queue_slice_sha256": (
            "90A18682DB17F89336AB5EE56B5FC57F949D7DDF6A50185D3C72448FDE0376DF"
        ),
        "expected_prefilled_coordinate_sha256": (
            "4CAEDFF6E2173D693C6A5D8627B56CF579824611152351A13B95598FA172E547"
        ),
        "expected_prefill_slice_context_sha256": (
            "841A46ACE251971C26EC9ED2EF7A3E54683B6B8025AE25A6CD291C433E74AD8B"
        ),
        "expected_target_coordinate_sha256": (
            "51900734DF64AB31EF1F9970079A00F356C8649C50B4E6664D836C3C181A721F"
        ),
        "expected_source_target_sha256": (
            "78D896A4D53DB090C66411EBF49D4CE9DD6F2C029A3AD968D545CA285B22B66B"
        ),
        "expected_current_target_sha256": (
            "A8B2D59157525E417F97147B079322DB5289CFA50231986862BB71FA24956FF5"
        ),
        "expected_context_corpus_sha256": (
            "D020BE9FCDAD08931F7FB9B3649273964303C7207D776E53561B29097BE3E246"
        ),
        "expected_gap_contract_sha256": (
            "034696587FE8B0052F8DAE3743C8E18F1222412373353A80C364841B858A5D51"
        ),
        "expected_boundary_sha256": (
            "AE532086164E7A910E2039B23C9056B2D4C6DC289AB0C5970A035B7ACEF55C2A"
        ),
        "expected_runtime_control_sha256": (
            "D5591D6C139254E9614CB2E47C0A3F9894DA09344DA74B36392A321BCD9E390F"
        ),
        "expected_base_search_sha256": (
            "5F2BC95D0BF88C5DFEBF6995F55941FFD1D9640C639891A30093FF4007B16C0C"
        ),
        "expected_complete_assembly_sha256": (
            "3F8A994137C451EEF75065D72CC23A464F32E147A71B77851C8A0ED68C076111"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "78BA046540B7094689AB388C384F82BF40708C44B813AF9BE9BCC0F97D9648A8"
        ),
        "expected_terminology_policy_sha256": (
            "D922BD3D611A4F858E8AAC8FB2B83E93815CF679A436A7A693DE81911A784DF5"
        ),
        "expected_translation_policy_sha256": (
            "1CF276E02EDD9C8EABDE655A01373270EA98238938D0576BAAF2CB301792DF66"
        ),
        "expected_candidate_sha256": (
            "FD4478F8EF033B197CB93692DADE24C89B834C0244BBC9665AFF76CDAC55E65F"
        ),
        "expected_combined_slice_candidate_sha256": (
            "9C800D7B2F282B52E18E894EAAF269730F3EE9A1275EC3A77FA743AD6153D827"
        ),
        "expected_combined_changed_literal_count": 49,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B117_S1355",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1355.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1356.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1357.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B117",
    "queue_row_count": 121,
    "queue_visible_count": 198,
    "queue_first": "15:985:0",
    "queue_last": "15:1105:2",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
