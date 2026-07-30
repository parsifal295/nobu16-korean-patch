#!/usr/bin/env python3
"""Build source-redacted PK B118 segment 1359 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1128,
    1129,
    1130,
    1131,
    1132,
    1133,
    1134,
    1135,
    1136,
    1137,
    1141,
)
TARGET_COORDINATES = (
    "15:1128:1",
    "15:1129:1",
    "15:1129:2",
    "15:1130:0",
    "15:1130:3",
    "15:1131:0",
    "15:1131:1",
    "15:1132:0",
    "15:1133:1",
    "15:1133:2",
    "15:1134:1",
    "15:1134:2",
    "15:1135:1",
    "15:1136:1",
    "15:1136:2",
    "15:1137:2",
    "15:1141:0",
)
TRANSLATIONS = {
    "15:1128:1": "와(과)",
    "15:1129:1": "와(과)",
    "15:1129:2": "이(가) 단교",
    "15:1130:0": "·",
    "15:1130:3": "→",
    "15:1131:0": "와(과)",
    "15:1131:1": "사이에",
    "15:1132:0": "와(과)",
    "15:1133:1": '"→"',
    "15:1133:2": '"(으)로 변경',
    "15:1134:1": '"→"',
    "15:1134:2": '"(으)로 변경',
    "15:1135:1": "인가",
    "15:1136:1": "의",
    "15:1136:2": "……",
    "15:1137:2": "이(가) 벌인",
    "15:1141:0": (
        "은(는) 공격로가 제한되어 있어\n"
        "그 때문에 견고한 성이라는 평판"
    ),
}
EXPECTED_ARITY = {
    1128: 3,
    1129: 3,
    1130: 4,
    1131: 3,
    1132: 2,
    1133: 3,
    1134: 3,
    1135: 2,
    1136: 3,
    1137: 4,
    1141: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1128:0",
    "15:1128:2",
    "15:1129:0",
    "15:1130:1",
    "15:1130:2",
    "15:1131:2",
    "15:1132:1",
    "15:1133:0",
    "15:1134:0",
    "15:1135:0",
    "15:1136:0",
    "15:1137:0",
    "15:1137:3",
    "15:1141:1",
)
PREFILL_COMPANION_DONOR = {
    "15:1128:0": "15:1109:0",
    "15:1128:2": "15:1109:2",
    "15:1129:0": "15:1121:0",
    "15:1130:1": "15:1122:1",
    "15:1130:2": "15:1122:2",
    "15:1131:2": "15:1123:2",
    "15:1132:1": "15:1124:1",
    "15:1133:0": "15:1125:0",
    "15:1134:0": "15:1125:0",
    "15:1135:0": "15:1127:0",
    "15:1136:0": "15:1128:0",
    "15:1137:0": "15:1129:0",
    "15:1137:3": "15:1129:3",
    "15:1141:1": "15:1133:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1137:1",)
EXACT_BASE_DONOR = {
    1128: (15, 1109),
    1129: (15, 1121),
    1130: (15, 1122),
    1131: (15, 1123),
    1132: (15, 1124),
    1133: (15, 1125),
    1134: (15, 1125),
    1135: (15, 1127),
    1136: (15, 1128),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in (1137, 1141)
    },
    1137: (
        "15:1129:0",
        "15:1129:2",
        "15:1129:3",
    ),
    1141: (
        "15:1133:0",
        "15:1133:1",
    ),
}
ESTRANGEMENT_FAILURE_MATCHES = tuple(
    (15, record_id)
    for record_id in range(1109, 1121)
)
EXPECTED_BASE_RAW_MATCHES = {
    1128: ESTRANGEMENT_FAILURE_MATCHES,
    1129: ((15, 1121),),
    1130: ((15, 1122),),
    1131: ((15, 1123),),
    1132: ((15, 1124),),
    1133: ((15, 1125), (15, 1126)),
    1134: ((15, 1125), (15, 1126)),
    1135: (),
    1136: (),
    1137: (),
    1141: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1135: ((15, 1127),),
    1136: ((15, 1128),),
    1137: ((15, 1129),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    1128: ((), ("025032", "025132")),
    1129: ((), ("025032", "025132")),
    1130: ((), ("025032", "025132", "0232")),
    1131: ((), ("025132", "025032", "023C")),
    1132: ((), ("025032", "025132")),
    1133: ((), ("025032", "023C", "023D")),
    1134: ((), ("025032", "023C", "023D")),
    1135: ((1078,), ("025033",)),
    1136: (
        (616, 730),
        ("025132", "025032", "023C0143680200000143DA020000"),
    ),
    1137: ((538, 592), ("025032", "023C")),
    1141: ((568,), ("026532",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1359,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1128:1",
    slice_last="15:1169:0",
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
    source_call_roots=(538, 568, 592, 616, 730, 1078),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(1118, 1182)
    ),
    speaker_style=(
        (1128, "apologetic_formal_estrangement_failure_report"),
        (1129, "system_diplomatic_break"),
        (1130, "system_estrangement_effect_summary"),
        (1131, "system_negotiation_lockout"),
        (1132, "system_estrangement_failure"),
        (1133, "system_diplomatic_stance_change"),
        (1134, "system_diplomatic_stance_change"),
        (1135, "suspicious_informal_reflection"),
        (1136, "formal_diplomatic_rejection_report"),
        (1137, "informal_counterintelligence_report"),
        (1141, "confident_castle_route_proposal"),
    ),
    terminology_policy=(
        ("estrangement operation", "이간 공작"),
        ("diplomatic stance", "외교 자세"),
        ("friendship", "우호도"),
        ("notoriety", "악명"),
        ("spy", "간자"),
        ("castle", "성"),
        ("attack route", "공격로"),
        ("dynamic conjunction", "와(과)"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic topic particle", "은(는)"),
        ("project ellipsis", "……"),
        ("project double quote", '"'),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B118 queue ordinals 67 through 133 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; nine complete records reuse approved "
        "completed Base Korean assemblies selected by raw, literal and "
        "operand-masked source identity; the counterintelligence record uses "
        "the same completed Base assembly through visible semantic "
        "references because its newline-only fragment has no promoted "
        "decision row, and the PK-specific limited-route castle wording "
        "reuses the approved semantically corresponding Base assembly; Base "
        "runtime and VM state are never inherited; estrangement, diplomatic "
        "stance, friendship, notoriety, spy, castle and attack-route terms, "
        "dynamic particles, ellipsis, quotes and each speaker register retain "
        "established project and historical wording; direct calls, inline "
        "person, faction, castle, duration and old or new value tokens, "
        "protected outer whitespace, newlines, gaps, literal arity, "
        "terminators, all fourteen same-record prefills, the hidden newline "
        "companion, all fifty slice prefills, complete assemblies, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, reciprocal neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=13,
    pins={
        "expected_queue_universe_sha256": (
            "1207015E2B3B81B1D053FA00F35628E780A874C0D44CFB013764244FF33CAAC3"
        ),
        "expected_queue_slice_sha256": (
            "CB0969BEE9A5ACD669AEF1F117B24C6A8F5F6A28B17C8F06E8FA797CE0392834"
        ),
        "expected_prefilled_coordinate_sha256": (
            "D3B23843A74D7A1C403546EDBD0A63339733E4888CBBC901E6D27E34FF100AEF"
        ),
        "expected_prefill_slice_context_sha256": (
            "2D2D83CEF04B8096AD09270451A4946F2C892E2B5D7E43FF8E8AA33940AD001D"
        ),
        "expected_target_coordinate_sha256": (
            "02FD9EFB9BD70F6386D9DF707B0AF2C8B4FD1A432B44D0995EF7622E8016B9FB"
        ),
        "expected_source_target_sha256": (
            "DC25C1A51B59CFFF84A0C2197596F16A3F82688A2EDFCC5414FBE5A3ACCF26AA"
        ),
        "expected_current_target_sha256": (
            "2469E3C94771C414BDF2B1956B724E765D8195AAF73074113834D3FED2D88D22"
        ),
        "expected_context_corpus_sha256": (
            "01132F26EE8C33E41493AAE3EC7099BA97DC2F1DFB38E6B5FD215321136F9F4A"
        ),
        "expected_gap_contract_sha256": (
            "31ACD0AF21C275FAAAC53A98F54D43F095FB779003E3A7CF29ECACE121285E73"
        ),
        "expected_boundary_sha256": (
            "74E7204ACC3872ADA3EEE72F3C72320228FE5406114D8BA4C1837DDEC628545C"
        ),
        "expected_runtime_control_sha256": (
            "0687F56235DA0856AFB30BB48357B7530EEA4AE0FDFCB2EFC090E9F14AA62632"
        ),
        "expected_base_search_sha256": (
            "19281D1F8F4F65003AA1943DC142AD11E322FCEF67A9D18E250F262E1DD3B597"
        ),
        "expected_complete_assembly_sha256": (
            "43456C403F23A53F57C41568DBC2905A685D2990C9F8F7A8F3B0A40C4EB95748"
        ),
        "expected_call_graph_sha256": (
            "02DE2128EA4D05350E238B9BC21C53DDDF56388AEF3F176864EFED42D10D8ADE"
        ),
        "expected_speaker_style_sha256": (
            "AC4260F1AD2CA5F0F26A8D1678A54E00C0F0B266F400C73E0D0F0AA4BE0BD20B"
        ),
        "expected_terminology_policy_sha256": (
            "D41E75BDF7A5CDA6EED53788157CB6BC48D5EB6B5DD689E45D334BA44116EAF1"
        ),
        "expected_translation_policy_sha256": (
            "B01A10D3C0234F0828BC0D9D69E862E1CE4D7015E5A7221DC59D36852106DE25"
        ),
        "expected_candidate_sha256": (
            "DE4DA14A2146C1C64E6E0D5F786C37E83871EC1F9D4E9F6473B1571C89ECA3BE"
        ),
        "expected_combined_slice_candidate_sha256": (
            "DAE81246B1F7557BBCDDBEBA24188D227CC8DD3592FE284CFDD9CBBB5CC8503D"
        ),
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B118_S1359",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1359.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1358.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1360.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B118",
    "queue_row_count": 111,
    "queue_visible_count": 200,
    "queue_first": "15:1106:0",
    "queue_last": "15:1216:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
