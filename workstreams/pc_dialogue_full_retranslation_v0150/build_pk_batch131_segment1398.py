#!/usr/bin/env python3
"""Build source-redacted PK B131 segment 1398 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2315:1",
    "15:2324:0",
    "15:2324:1",
    "15:2325:0",
    "15:2326:1",
    "15:2328:0",
    "15:2329:0",
    "15:2338:2",
)
TRANSLATIONS = {
    "15:2315:1": "겠습니까?",
    "15:2324:0": "을(를)",
    "15:2324:1": "의",
    "15:2325:0": "의",
    "15:2326:1": "?",
    "15:2328:0": "명심",
    "15:2329:0": "명심",
    "15:2338:2": "?",
}
TARGET_RECORD_IDS = (2315, 2324, 2325, 2326, 2328, 2329, 2338)
EXPECTED_ARITY = {
    2315: 2,
    2324: 3,
    2325: 2,
    2326: 2,
    2328: 2,
    2329: 2,
    2338: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2315:0",
    "15:2324:2",
    "15:2325:1",
    "15:2326:0",
    "15:2328:1",
    "15:2329:1",
    "15:2338:0",
    "15:2338:1",
)
PREFILL_COMPANION_DONOR = {
    "15:2315:0": "15:2284:0",
    "15:2324:2": "15:2293:2",
    "15:2325:1": "15:2294:1",
    "15:2326:0": "15:2295:0",
    "15:2328:1": "15:2297:1",
    "15:2329:1": "15:2298:1",
    "15:2338:0": "15:2307:0",
    "15:2338:1": "15:2307:1",
}
EXACT_BASE_DONOR = {
    record_id: (15, record_id - 31)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    2324: ((15, 2293),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2315: ((1078,), ("024833",)),
    2324: ((), ("024633", "026432", "029632")),
    2325: ((1066,), ("026432",)),
    2326: ((1066,), ()),
    2328: ((538, 322), ()),
    2329: ((538, 322), ()),
    2338: ((742,), ("025A32",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1398,
    queue_start=67,
    queue_stop=134,
    slice_first="15:2315:0",
    slice_last="15:2360:0",
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
    source_call_roots=(1078, 1066, 538, 322, 742),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2275, 2405)
    ),
    speaker_style=(
        (2315, "formal_frontline_assignment_proposal"),
        (2324, "system_land_transfer_notice"),
        (2325, "system_castle_town_expansion_guidance"),
        (2326, "formal_advice_reduction_confirmation"),
        (2328, "formal_instruction_acceptance"),
        (2329, "formal_advice_setting_acceptance"),
        (2338, "formal_corps_support_request"),
    ),
    terminology_policy=(
        ("front line", "전선"),
        ("participate in battle", "참전"),
        ("land transfer", "영지를 옮김"),
        ("castle-town expansion", "증축"),
        ("clan management", "세력 운영"),
        ("advice", "조언"),
        ("army corps", "군단"),
        ("offensive", "공세"),
        ("support", "원호"),
        ("dynamic particles", "을(를), 이(가), (으)로"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B131 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all seven "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity with "
        "explicit exact donors; Base runtime and VM state are never "
        "inherited; front lines, participation in battle, land transfers, "
        "castle-town expansion, clan management, advice, army corps, "
        "offensives and support retain established historical project "
        "wording and formal, system or advisory registers; calls, inline "
        "person, castle, force and corps tokens, protected outer whitespace, "
        "line breaks, particles, punctuation, terminators, complete record "
        "arity, all fifty-nine slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=6,
    pins={
        "expected_queue_universe_sha256": "C98584FBA86F034B3D1EDB74FE505FABF0191EAA9CE21141CCF11AF9D49ECA1C",
        "expected_queue_slice_sha256": "E2B1A36ED999C35E3C8C7D7CA1511B5C06DD31E183360767B3918FD6B056805F",
        "expected_prefilled_coordinate_sha256": "660885AC36102AE2387925A9E991691FC4D7C1031D59EAAF1595B7E240E86E6B",
        "expected_prefill_slice_context_sha256": "CB4B73C1761BF3F92D15CB11441FF4CE5563E10FC83E9CFA967BF5DCFBF36A19",
        "expected_target_coordinate_sha256": "26A6C8EDD9DC2ACDEE0789425CDD6C0C81C28BC1875E8523F97842B6B83753F8",
        "expected_source_target_sha256": "8AA7F45653F94321C3EC9D869442A60C3185C808D1CD9AD4298A985D26547EE5",
        "expected_current_target_sha256": "9A4093476381797D5610643BE8A7F0A35BFB0A2841404B0B423999DE39306C8D",
        "expected_context_corpus_sha256": "C0BD248F6F4B7D220B70CF8AD2606064283CF27DF1E0537B1BFD9B6059DD62FB",
        "expected_gap_contract_sha256": "BCA98AC4CCA0084523A5269F73FF87CD77709A371312BF006BE80E72B65BB2A0",
        "expected_boundary_sha256": "B2B95E1DE05A09E8DF89F89CE68676062172690DF8D357271382569F04EF77AE",
        "expected_runtime_control_sha256": "2B217308E971B02002C809137673466668D8DB5CD3B8E09BBEC5FF152A5C3FB4",
        "expected_base_search_sha256": "2B38A2507B10BD5EFA8175B979C342D00A724D1575C49AAD3C2B7E4BCDF5D181",
        "expected_complete_assembly_sha256": "4A9E6316520F24AEB672E8131757C048424115C8B04948CAE7F8108978891E7E",
        "expected_call_graph_sha256": "234CC1B851EEB6F7A82808B19287A48EA1BD5A9FFAF17041D0487692C6F3A609",
        "expected_speaker_style_sha256": "12C4A8D329DA0F91703CEAE0E9C477C4DD89E79932C89A23829195BDFEF03CA3",
        "expected_terminology_policy_sha256": "3A58ADA0FE9BBA37DABC93CBD7F0711641B6B933FFBBF18CD10979C108796EFE",
        "expected_translation_policy_sha256": "18235DB149BC5C21E732686112AD451BEDD245B7B201D5640B9FFD8049785B46",
        "expected_candidate_sha256": "6F64E4490FACFFFFB09D2432D808CE2300433E182FF88A3B6FB29667FEB57C09",
        "expected_combined_slice_candidate_sha256": "4E02858E8BBEB0C4A281DECD8DCAA30CC2C608C8DCA8300F8146D4641352E24C",
        "expected_combined_changed_literal_count": 65,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B131_S1398",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1398.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1397.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1399.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B131",
    "queue_row_count": 104,
    "queue_visible_count": 199,
    "queue_first": "15:2290:0",
    "queue_last": "15:2395:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
