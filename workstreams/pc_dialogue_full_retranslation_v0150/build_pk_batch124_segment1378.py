#!/usr/bin/env python3
"""Build source-redacted PK B124 segment 1378 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1701,
    1702,
    1707,
    1708,
    1709,
)
TARGET_COORDINATES = (
    "15:1701:1",
    "15:1702:2",
    "15:1707:0",
    "15:1707:1",
    "15:1708:0",
    "15:1708:2",
    "15:1709:1",
    "15:1709:2",
    "15:1709:3",
)
TRANSLATIONS = {
    "15:1701:1": "인가",
    "15:1702:2": "에",
    "15:1707:0": "님,",
    "15:1707:1": "합전",
    "15:1708:0": "합전",
    "15:1708:2": "!\n",
    "15:1709:1": "합전",
    "15:1709:2": "을 지휘",
    "15:1709:3": "인가?\n",
}
EXPECTED_ARITY = {
    1701: 2,
    1702: 4,
    1707: 3,
    1708: 4,
    1709: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1701:0",
    "15:1702:0",
    "15:1702:1",
    "15:1702:3",
    "15:1707:2",
    "15:1708:1",
    "15:1708:3",
    "15:1709:4",
)
PREFILL_COMPANION_DONOR = {
    "15:1701:0": "15:1671:0",
    "15:1702:0": "15:1672:0",
    "15:1702:1": "15:1672:1",
    "15:1702:3": "15:1672:3",
    "15:1707:2": "15:1677:2",
    "15:1708:1": "15:1678:1",
    "15:1708:3": "15:1678:3",
    "15:1709:4": "15:1679:4",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1709:0",)
EXACT_BASE_DONOR = {
    1701: (15, 1671),
    1702: (15, 1672),
    1707: (15, 1677),
    1708: (15, 1678),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 1709
    },
    1709: (
        "15:1679:1",
        "15:1679:2",
        "15:1679:3",
        "15:1679:4",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    1701: ((15, 1671),),
    1702: ((15, 1672),),
    1707: ((15, 1677),),
    1708: ((15, 1678),),
    1709: ((15, 1679),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1701: ((700, 616), ("026432",)),
    1702: ((1168, 1168, 892), ()),
    1707: ((8, 1066), ()),
    1708: ((550, 1168, 322), ()),
    1709: ((466, 8), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1378,
    queue_start=134,
    queue_stop=200,
    slice_first="15:1687:0",
    slice_last="15:1714:1",
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
    source_call_roots=(
        8,
        322,
        466,
        550,
        616,
        700,
        892,
        1066,
        1168,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1670, 1715)
    ),
    speaker_style=(
        (1701, "formal_attack_target_military_preparations_proposal"),
        (1702, "polite_honor_commendation_appearance_request"),
        (1707, "formal_direct_battle_command_request"),
        (1708, "energetic_battle_command_opportunity"),
        (1709, "deferential_battle_command_proposal"),
    ),
    terminology_policy=(
        ("our house", "우리 가문"),
        ("attack target", "공략 목표"),
        ("castle", "성"),
        ("military preparations", "군비"),
        ("honor commendation", "논공행상"),
        ("promotion", "승진"),
        ("battle", "합전"),
        ("command", "지휘"),
        ("swift resolution", "단기 결착"),
        ("friendly force", "아군"),
        ("victory", "승리"),
        ("soldiers", "병사"),
        ("full of courage", "용기백배"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B124 queue ordinals 134 through 199 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; four complete records reuse "
        "approved completed Base Korean assemblies selected by literal and "
        "operand-masked source identity with explicit exact donors, while "
        "the fifth uses the matching Base assembly through its four visible "
        "semantic references because its empty first literal has no "
        "promoted decision row; Base runtime and VM state are never "
        "inherited; "
        "our house, attack target, castles, military preparations, honor "
        "commendation, promotion, battle, command, swift resolution, "
        "friendly forces, victory, soldiers and full-of-courage wording "
        "retain established historical project terminology and each "
        "speaker register; direct calls, inline person and castle tokens, "
        "protected outer whitespace, newlines, gaps, literal arity, "
        "terminators, all eight same-record prefills, the hidden empty "
        "literal, all fifty-seven slice prefills, complete assemblies, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, reciprocal S1376 and S1377 decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=3,
    pins={
        "expected_queue_universe_sha256": (
            "63E6B1C672AAC22BB0D388E2D42C4798C3438D1E7596F9AC5206BAC0B65D92D6"
        ),
        "expected_queue_slice_sha256": (
            "90D521EB040701D68C11A2E495BBC19BC0031BED8ADAB0817AEED11A32259210"
        ),
        "expected_prefilled_coordinate_sha256": (
            "AAB55BB04A579896C0CCA9A6ABEBC1B2194429E96D1FE962DF94CE205BBF5B77"
        ),
        "expected_prefill_slice_context_sha256": (
            "6C8B866871A519B2B5CE01D21A45074389E77570B4FD6A516AADFA7B004A1F23"
        ),
        "expected_target_coordinate_sha256": (
            "6205B310EF1E88C91B978A90F3AE201CE46E27A52186181F1BAB09EC6DA789B9"
        ),
        "expected_source_target_sha256": (
            "A19FCBAE2639CF041AF92A55CA53ED4225B685787AC3591E5B071D546DF5411C"
        ),
        "expected_current_target_sha256": (
            "1A576C35A64BF138907A3AF30CE401267BB4033431069796A7E3BC9EB9ACF51A"
        ),
        "expected_context_corpus_sha256": (
            "33B7FDBFBD37767D8A0BBE73026893FECDF65D1AC3D40DB9FF560AC8BB98D667"
        ),
        "expected_gap_contract_sha256": (
            "1E1BDB149C7FB3423EDEF6219509DE4D68EDB0D8B7EDAB8BB67D23FA4245E072"
        ),
        "expected_boundary_sha256": (
            "20A2CA045E891A5B2F55DBBA46A4FC8C68DE5227F0B065CA65BA0CDF0E2D623F"
        ),
        "expected_runtime_control_sha256": (
            "592A09586DE37503BDF6976A49B2EA16B09F22904B262C36211C6F0C35AEC853"
        ),
        "expected_base_search_sha256": (
            "8523E809E37D5253C0D144BF5939C8F0796B7C8B2A513BDE931986FE129F45B6"
        ),
        "expected_complete_assembly_sha256": (
            "1B65BF2D7289F84196CED4CD19FEB05CF41040EEDDCF0EFE25CD090854BC707D"
        ),
        "expected_call_graph_sha256": (
            "530FF00AE41EE0A9E4AFB9F4D8E418917003245776F27146F5FC1917BF6D4410"
        ),
        "expected_speaker_style_sha256": (
            "189EB37CFB2D8E8BFE9CFAEB7019EC60DE570EF7596373AED4DFC41843231C49"
        ),
        "expected_terminology_policy_sha256": (
            "E2C3C1856D516E4B7711F0451D5A478530CD5B79CECE524B4A0ECAFF63714CCC"
        ),
        "expected_translation_policy_sha256": (
            "B05A95D4043133DB34C4D930F06E58DF0006AE8154918E1B57414ABCC5C0E19A"
        ),
        "expected_candidate_sha256": (
            "FAA9EBCFD717F6CA43EEB7EE287F4495BB9C70B3824A9C10CEC58070C855A2A1"
        ),
        "expected_combined_slice_candidate_sha256": (
            "8308E26B43F246B25662CB376F41BEADF487FD7BE9940E7A8A1DF419F83253CF"
        ),
        "expected_combined_changed_literal_count": 44,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B124_S1378",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1378.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1376.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B124_S1377.private.v1.jsonl",
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
