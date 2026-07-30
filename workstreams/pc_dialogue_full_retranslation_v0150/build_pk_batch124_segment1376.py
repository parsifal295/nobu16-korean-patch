#!/usr/bin/env python3
"""Build source-redacted PK B124 segment 1376 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1614:3",
    "15:1657:2",
)
TRANSLATIONS = {
    "15:1614:3": "……",
    "15:1657:2": "인가",
}
TARGET_RECORD_IDS = (
    1614,
    1657,
)
EXPECTED_ARITY = {
    1614: 4,
    1657: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1614:0",
    "15:1614:1",
    "15:1614:2",
    "15:1657:0",
    "15:1657:1",
)
PREFILL_COMPANION_DONOR = {
    "15:1614:0": "15:1584:0",
    "15:1614:1": "15:1584:1",
    "15:1614:2": "15:1584:2",
    "15:1657:0": "15:1627:0",
    "15:1657:1": "15:1627:1",
}
EXACT_BASE_DONOR = {
    1614: (15, 1584),
    1657: (15, 1627),
}
SEMANTIC_BASE_CONTEXT = {
    1614: (),
    1657: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    1614: ((15, 1584),),
    1657: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    1614: ((15, 1584),),
    1657: ((15, 1627),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1614: ((310, 376, 286), ()),
    1657: ((82, 730, 610), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1376,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1614:0",
    slice_last="15:1657:2",
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
    source_call_roots=(310, 376, 286, 82, 730, 610),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1574, 1669)
    ),
    speaker_style=(
        (1614, "formal_provisions_depleted_retreat_assessment"),
        (1657, "formal_landholder_assignment_proposal"),
    ),
    terminology_policy=(
        ("provisions", "병량"),
        ("retreat", "철수"),
        ("landholder", "영주"),
        ("county", "군"),
        ("development", "발전"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B124 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; both complete "
        "records reuse approved completed Base Korean assemblies selected "
        "by raw, literal and operand-masked source identity with explicit "
        "exact donors; Base runtime and VM state are never inherited; "
        "provisions, retreat, landholders, counties and development retain "
        "established historical project wording and formal advisory "
        "registers; calls, speaker, county and value tokens, protected outer "
        "whitespace, line breaks, ellipses, terminators, complete record "
        "arity, all sixty-five slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=1,
    pins={
        "expected_queue_universe_sha256": (
            "63E6B1C672AAC22BB0D388E2D42C4798C3438D1E7596F9AC5206BAC0B65D92D6"
        ),
        "expected_queue_slice_sha256": (
            "BC20B670C4C3AAE2A0E095F62DB2DB8EC77E924EB214369E2E29883598742F48"
        ),
        "expected_prefilled_coordinate_sha256": (
            "A825C8401B123798008C684C3801D4CACD8A27263FF60F2070214F18CA2E7AA8"
        ),
        "expected_prefill_slice_context_sha256": (
            "8F6DC80B9A1F7C41CF5D8C092EBA92959F0208A5BD18A2C530D356CFD5376382"
        ),
        "expected_target_coordinate_sha256": (
            "B0706E3EB4495721B8B6644F20B0F332E510A8FED3E94AB9BF675B7A03643977"
        ),
        "expected_source_target_sha256": (
            "EEB6588BFA6C486A25163B587A7CC6EAE95C918CA929C184A83E3E773EE33A7C"
        ),
        "expected_current_target_sha256": (
            "95AC98D0AEFECB0911E3B1A7B1A67E1B20FCAB42FEB568D12BFACD7AC2721E84"
        ),
        "expected_context_corpus_sha256": (
            "33B7FDBFBD37767D8A0BBE73026893FECDF65D1AC3D40DB9FF560AC8BB98D667"
        ),
        "expected_gap_contract_sha256": (
            "C999A67A6C593BA8C8ED3845C09700904184F864F38E40C89A60423CBD7396ED"
        ),
        "expected_boundary_sha256": (
            "71296DBAAB86E06037339E6CC136FB4147B0D6E9701E47D23504AC269B84DB7C"
        ),
        "expected_runtime_control_sha256": (
            "D8E2AB5EB79A257CD5AF8DAB522563FC6EA424395661AD61460B4385F6F48E66"
        ),
        "expected_base_search_sha256": (
            "86669FF10D643E0DDD06CAA6C77A7E7F283F38A82FBE5125992D078A120804A6"
        ),
        "expected_complete_assembly_sha256": (
            "52E3867013566B17ED632578DF836E5AB522650D7DF0B5C6BE9D1A70346DF3A3"
        ),
        "expected_call_graph_sha256": (
            "38C84A36037B217816181719DEC6229DC8B670095D9E1C8AB6CBC378B8F89F60"
        ),
        "expected_speaker_style_sha256": (
            "11CDB2DF547BB711FF788ADB194E7A2DA4AE515F260568B064F052D501983BD5"
        ),
        "expected_terminology_policy_sha256": (
            "715787C4520AB6725A97576D7A7A65E9D4B9479FA2D885087346C81C295F9706"
        ),
        "expected_translation_policy_sha256": (
            "3417CEAE23EC6440BA7A39B9505B1A42A10ADF27DC1ED3F305A2646B860BFC62"
        ),
        "expected_candidate_sha256": (
            "8B68EE11DF5887B23963839C6FC2F198834B8477717A8088AAB6648F0DBE8F8D"
        ),
        "expected_combined_slice_candidate_sha256": (
            "4EB25CA457991E221C8B1812FD2E16500274AC38C850008C685A9DC25617848D"
        ),
        "expected_combined_changed_literal_count": 57,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B124_S1376",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1376.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1377.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1378.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B124",
    "queue_row_count": 101,
    "queue_visible_count": 200,
    "queue_first": "15:1614:0",
    "queue_last": "15:1714:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
