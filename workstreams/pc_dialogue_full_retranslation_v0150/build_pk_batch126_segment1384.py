#!/usr/bin/env python3
"""Build source-redacted PK B126 segment 1384 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1893:0",
    "15:1893:2",
    "15:1894:0",
    "15:1894:2",
    "15:1895:0",
    "15:1910:0",
)
TRANSLATIONS = {
    "15:1893:0": "의",
    "15:1893:2": "\n당주인",
    "15:1894:0": "의",
    "15:1894:2": "\n당주인",
    "15:1895:0": "의",
    "15:1910:0": "정책\u00b7",
}
TARGET_RECORD_IDS = (
    1893,
    1894,
    1895,
    1910,
)
EXPECTED_ARITY = {
    1893: 4,
    1894: 4,
    1895: 2,
    1910: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1893:1",
    "15:1893:3",
    "15:1894:1",
    "15:1894:3",
    "15:1895:1",
    "15:1910:1",
)
PREFILL_COMPANION_DONOR = {
    "15:1893:1": "15:1863:1",
    "15:1893:3": "15:1863:3",
    "15:1894:1": "15:1863:1",
    "15:1894:3": "15:1863:3",
    "15:1895:1": "15:1865:1",
    "15:1910:1": "15:1880:1",
}
EXACT_BASE_DONOR = {
    1893: (15, 1863),
    1894: (15, 1864),
    1895: (15, 1865),
    1910: (15, 1880),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    1893: (),
    1894: (),
    1895: (),
    1910: ((15, 1880),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    1893: ((15, 1863), (15, 1864)),
    1894: ((15, 1863), (15, 1864)),
    1895: ((15, 1865),),
    1910: ((15, 1880),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1893: ((1126,), ("023C", "028C32", "024833")),
    1894: ((1126,), ("023C", "028C32", "024833")),
    1895: ((1126,), ("023C", "028C32")),
    1910: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1384,
    queue_start=134,
    queue_stop=200,
    slice_first="15:1892:0",
    slice_last="15:1927:2",
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
    source_call_roots=(1126,),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1853, 1939)
    ),
    speaker_style=(
        (1893, "formal_allied_house_military_assessment"),
        (1894, "formal_allied_house_military_assessment"),
        (1895, "formal_allied_house_reinforcement_assessment"),
        (1910, "formal_policy_improvement_proposal"),
    ),
    terminology_policy=(
        ("our clan", "우리 가문"),
        ("friendship", "우의"),
        ("wartime", "전시"),
        ("reinforcements", "원군"),
        ("house lord", "당주"),
        ("battle skill", "싸움에 능함"),
        ("policy", "정책"),
        ("benefit", "혜택"),
        ("project middle dot", "\u00b7"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B126 queue ordinals one hundred "
        "thirty-four through one hundred ninety-nine and the approved Base "
        "prefill; pristine PK JP is authoritative and every populated EN, "
        "SC and TC same-record fragment array was reviewed as auxiliary "
        "context; all four complete records reuse approved completed Base "
        "Korean assemblies selected by raw, literal and operand-masked "
        "source identity with explicit exact donors; S1382 and S1383 "
        "neighbor decisions are validated reciprocally when present so the "
        "three B126 slices remain disjoint and their complete assemblies "
        "stay compatible; Base runtime and VM state are never inherited; "
        "our clan, friendship, wartime, reinforcements, house lords, battle "
        "skill, policies and benefits retain established historical project "
        "wording and formal advisory registers; calls, inline house, force, "
        "officer and policy tokens, protected outer whitespace, line breaks, "
        "middle dots, ellipses, terminators, complete record arity, all "
        "sixty slice prefills, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, neighbor decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256": (
            "FB8F40DA25868E77D6819B3B054CFA5D1866D279CBC04B058E9F750371FD010D"
        ),
        "expected_queue_slice_sha256": (
            "3AE5BF37A6116C59101FEDE2752A38EE8CEFCF95E49F0CBC130C31C14258F019"
        ),
        "expected_prefilled_coordinate_sha256": (
            "40972C277930137AA07044268CD9B073849D23C4664F9505CF0145BE602C6C8D"
        ),
        "expected_prefill_slice_context_sha256": (
            "F8DCB319B845D250B8394142B02C7B1B43CDB4B572F99877AE0DACCE2C52F8B6"
        ),
        "expected_target_coordinate_sha256": (
            "878F772FA95F218DFBF75DD2F4F36844967FC9ACE4A39881C19183BE15F8B065"
        ),
        "expected_source_target_sha256": (
            "0D7E2970CD58F8025D1ED5A31CE40FC66347B9165F4CAAECCDF49FEE70CD7A69"
        ),
        "expected_current_target_sha256": (
            "F3D1D68D04D2D175B58DE8653EBF447D085BCA9BCA019E80EE41EDA6788997BE"
        ),
        "expected_context_corpus_sha256": (
            "29E672CE13BE217812D12239F072FB502613E5A08DC9C3E0BAE2115330665E76"
        ),
        "expected_gap_contract_sha256": (
            "12C7043A9B7A658687FEBB38DC0388BE624E209B855BB8A9FAFB8B5E4E2BE41E"
        ),
        "expected_boundary_sha256": (
            "77EBD633548C97AD1CE8475FA9A1B9AF91AD38F9BDF9BF0C186B420FC7590416"
        ),
        "expected_runtime_control_sha256": (
            "84EC7EB64B7B38B266B1925B4B4319D04ADB6A46DAA60020D7CEF946EDA6A88A"
        ),
        "expected_base_search_sha256": (
            "5172A6440D4393E6077C20174468B80F3218D0B17BC0414934BEDE47A090FF3B"
        ),
        "expected_complete_assembly_sha256": (
            "E7F06AF702F909A972FEA30D76621E0D4BF59B2922994CAE25847AC5B3C1773F"
        ),
        "expected_call_graph_sha256": (
            "AECD2F5280C58D817C62690FB8EBF06965533008FCFC18B8B2CE138ECA5653B0"
        ),
        "expected_speaker_style_sha256": (
            "DE586358553B0D80D77E951124E59E25AF2C3B70A8380ECE33C683C3057A5D8D"
        ),
        "expected_terminology_policy_sha256": (
            "B669E11A66249C96DA1B422446DB51A7C451FCCC4B81B0FA9C7EF820A298267B"
        ),
        "expected_translation_policy_sha256": (
            "46418D73BC79869FAAEFCB970DC85CFBF7C3FCF2E96E9F3AD3B119FDA7EFEC9E"
        ),
        "expected_candidate_sha256": (
            "C14EE4682457B3BCB2D500EF9AA42E4FDA789FB432336E0CA7CC362FE63C3D63"
        ),
        "expected_combined_slice_candidate_sha256": (
            "03D2A1937235E16822A27E98D12DCA7C72DAF37FC4205F50A90AA0AEFB99172E"
        ),
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B126_S1384",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1384.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1382.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1383.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B126",
    "queue_row_count": 102,
    "queue_visible_count": 200,
    "queue_first": "15:1823:0",
    "queue_last": "15:1927:2",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
