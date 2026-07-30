#!/usr/bin/env python3
"""Build source-redacted PK B095 segment 1290 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (3396,)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1290,
    queue_start=67,
    queue_stop=134,
    slice_first="9:3331:0",
    slice_last="9:3396:0",
    target_coordinates=("9:3396:0",),
    translations={
        "9:3396:0": (
            "본성이 파괴되었다고!?\n"
            "각오를 굳힐 수밖에 없겠군……"
        ),
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={3396: 1},
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        3396: ("9:3169:0",),
    },
    expected_base_raw_matches={3396: ()},
    expected_base_literal_matches={3396: ()},
    expected_base_masked_matches={3396: ()},
    expected_controls_by_record={3396: ((), ())},
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3329, 3399)
    ),
    speaker_style=(
        (3396, "rough_citadel_loss_final_resolve"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("destroyed", "파괴되다"),
        ("resolve oneself", "각오를 굳히다"),
        ("rough constraint", "수밖에 없겠군"),
        ("project long ellipsis", "……"),
        ("ASCII shock punctuation", "!?"),
    ),
    basis=(
        "pristine PK JP is authoritative and the empty EN, SC and TC arrays "
        "were checked; the complete PK-only citadel-loss record has no Base "
        "raw, literal or operand-masked match, while the completed parallel "
        "Base retreat-route-loss record supplies semantic structure, rough "
        "final-resolve register and punctuation only; Base runtime and VM "
        "state are never inherited; 본성, 파괴되다 and 각오를 굳히다 preserve "
        "the siege context and resolve meaning without softening the rough "
        "ending; the two-line one-literal shape, empty call and inline-token "
        "sets, gap, terminator, all sixty-six slice prefills, pins, two-run "
        "reproduction, tamper rejection, mutual neighbor, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=1,
    pins={
        "expected_queue_universe_sha256":
        "7B3B9B0B06E04011E8B4BBAC53D62B2F68AC2E1D12BD0D834CB019A578EB8533",
        "expected_queue_slice_sha256":
        "BD850297054859C21EC49EC2A46C3896585C3506E58ECE4241341ADFD7A08785",
        "expected_prefilled_coordinate_sha256":
        "197FAE1CE7534B5DB0B4C10153001D012663E15A83DF0660CD2853A88AD78E9B",
        "expected_prefill_slice_context_sha256":
        "D522CAD744346B321D6D574C469627970307CDD7D863451203A14EF6A1520674",
        "expected_target_coordinate_sha256":
        "652CA6EAE3F7575CA43559B0CEC6867C93082A959DA07A66C72693E6E8B14FAF",
        "expected_source_target_sha256":
        "0F96AB02F9758A3BBF1157E7EFFD2C7B058E7F75309F40ECECD686B1027DDF43",
        "expected_current_target_sha256":
        "899E11337B39A8483E68D5626F51EAA3CCA37D784AFF34A902DE54A0FDA2B5E8",
        "expected_context_corpus_sha256":
        "6276BBF2CEF6E50D3E16C284CAB351F31C60FF5CF389E12558568085E0CDA33F",
        "expected_gap_contract_sha256":
        "D92D58F883F0E0B9B06857B1412C6B6818A85088DD00E8F568B8903402B426D1",
        "expected_boundary_sha256":
        "FA0F3B374BDA7044670031A52B9CA09DA89768034AD603A8CC8FCE65E527E1ED",
        "expected_runtime_control_sha256":
        "883EBDEA426ABAF1D0A777C214972BF584582B6A5B8B66ADC194E630C896E952",
        "expected_base_search_sha256":
        "88DBB92E0E7F11CCCEF21FD287630875DF8BD1C14558B02E71FAE423808A2BFF",
        "expected_complete_assembly_sha256":
        "624029AF97E34B608B28356F17DA232F6DFAFF218AC4071CCAA2A46571B4A056",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "B8569557FAB8B9B709EE118A6BE55E881111E2B0F6100F33369B7C0C6B340EFA",
        "expected_terminology_policy_sha256":
        "75E54A237938DA59D9EE39ACE7F135B14D4A356CE44E4113826DCC8C3B698747",
        "expected_translation_policy_sha256":
        "27DED2986B29F34C91630532CD6F3C6F0EE2B3F0D48E390831447A3AF563DE5D",
        "expected_candidate_sha256":
        "B3AC968280656F502983A0A26B72E235467C58E92B8940CBD155844ABDFABDB8",
        "expected_combined_slice_candidate_sha256":
        "8FC0E62553C076D469171B47CBCDA8F0D09F8CA260F6174BE123B46E9E88F4BC",
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B095_S1290",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B095_S1290.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B095_S1291.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B095",
    "queue_row_count": 192,
    "queue_visible_count": 200,
    "queue_first": "9:3264:0",
    "queue_last": "9:3455:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
