#!/usr/bin/env python3
"""Build source-redacted PK B091 segment 1278 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (2593, 2618, 2632)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1278,
    queue_start=67,
    queue_stop=134,
    slice_first="9:2571:0",
    slice_last="9:2632:0",
    target_coordinates=(
        "9:2593:0",
        "9:2593:1",
        "9:2618:0",
        "9:2632:0",
    ),
    translations={
        "9:2593:0": "적군에게―",
        "9:2593:1": "이(가) 협격을 당함",
        "9:2618:0": "설마,",
        "9:2632:0": "본성을 노리는가!\n그렇게는 못 한다!",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        2593: 2,
        2618: 2,
        2632: 1,
    },
    prefill_companion_coordinates=("9:2618:1",),
    prefill_companion_donor={
        "9:2618:1": "9:2531:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        2593: ("9:2506:0", "9:2506:1"),
        2618: ("9:2531:0", "9:2531:1"),
        2632: ("9:2533:0",),
    },
    expected_base_raw_matches={
        2593: ((9, 2506),),
        2618: ((9, 2531),),
        2632: (),
    },
    expected_base_literal_matches={
        2593: ((9, 2506),),
        2618: ((9, 2531),),
        2632: (),
    },
    expected_base_masked_matches={
        2593: ((9, 2506),),
        2618: ((9, 2531),),
        2632: (),
    },
    expected_controls_by_record={
        2593: ((), ("02AC32",)),
        2618: ((1,), ()),
        2632: ((), ()),
    },
    source_call_roots=(1,),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2505, 2634)
    ),
    speaker_style=(
        (2593, "dynamic_pincer_status_notification"),
        (2618, "dynamic_shocked_lure_realization"),
        (2632, "rough_martial_citadel_defiance"),
    ),
    terminology_policy=(
        ("enemy force", "적군"),
        ("pincer attack", "협격"),
        ("lure stratagem", "유인책"),
        ("citadel or inner bailey", "본성"),
        ("rough defiance", "그렇게는 못 한다"),
        ("project em dash", "―"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record context was manually reviewed; two exact completed Base "
        "records supply the pincer-status and lure-realization wording, while "
        "the completed parallel Base retreat-route response supplies only the "
        "rough martial register and defiant sentence pattern for the PK-only "
        "citadel response; Base runtime and VM state are never inherited; "
        "historical siege terminology uses 본성 and tactical terminology uses "
        "협격 and 유인책 consistently; all three complete records preserve "
        "the dynamic force token, direct call, protected newline, punctuation, "
        "literal arity, gaps and the approved same-record prefill companion; "
        "all pins, two-run reproduction, tamper rejection, mutual neighbors, "
        "reverse overlays, outside-scope identity and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=3,
    pins={
        "expected_queue_universe_sha256":
        "F883FCE6B74C91BB99B867D39D3B13E68CD9B7C4A729E9624333101CC44264DA",
        "expected_queue_slice_sha256":
        "498480A914470420D3B2749429B1E06E494714673D2E8E4577546AF9BFC01B61",
        "expected_prefilled_coordinate_sha256":
        "A178A4DC20A0DD15FB68864D4DC543D6A9C9D35CC0C0CFE71AEDC7E43605B58E",
        "expected_prefill_slice_context_sha256":
        "E523EE00D30A33AC52D14AE0FBA52085E6DEAA92A248F099FAB1322EB6C5F717",
        "expected_target_coordinate_sha256":
        "448E46ADA8996ED1DD507A56FC9A9C57F2D30AFFBF7A9CE37A4D0513DC588B63",
        "expected_source_target_sha256":
        "29B81471D1EE238279D2EF482329AB8A0C65AFD3EC1EA4F19AF2F721F429F243",
        "expected_current_target_sha256":
        "3EFD363BAF389640802AC004B65EF97768A0057C6CF8A6FC1EA83F35B2F17641",
        "expected_context_corpus_sha256":
        "8ED338F0175EE5F504BFAAE893C65837096124BC13E667B98BDCEB21489109D1",
        "expected_gap_contract_sha256":
        "4706472C9E1E98D82DC6A881BB3DBDAF4A0006ED2C5AB693E555D9EDDF3BD32D",
        "expected_boundary_sha256":
        "50EBAD1876CF90945BEE4A95AB0D4850B693F1D0D09C30C873B0B46809DDB47F",
        "expected_runtime_control_sha256":
        "554042CB04E39CE8FF9C0D7B1E054CD844BB825CEAF9E041645C5C2E4FC878C2",
        "expected_base_search_sha256":
        "0910ACBD284902E399D835560D81D63B3D8685D74E02ED3203E35414E65BA8AE",
        "expected_complete_assembly_sha256":
        "0949B89ED008A5BBF9ECC827E1CEDE470C75B41AC2C99B08A8E61015C0132710",
        "expected_call_graph_sha256":
        "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD",
        "expected_speaker_style_sha256":
        "48C9CE0A475A942C16E66D287094E770779FCE63E5FB3521C56461D98DD7A52F",
        "expected_terminology_policy_sha256":
        "18063BCC9881A1D7D5AA6DCF0241C1EF5DFE687F753BCFC92100B231CBF45080",
        "expected_translation_policy_sha256":
        "530C469CE1D713FC54C1BC7B706030673C180458C0F212788855B2CD9B48A111",
        "expected_candidate_sha256":
        "37F31102BD383861316BB74B4E00D42AC50B632CC03F5DE83F601E34F23B9175",
        "expected_combined_slice_candidate_sha256":
        "350EC7AC5A358FF77592A7009C1F31A942080526D4C74F7B6B07F15DA31E79F1",
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B091_S1278",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B091_S1278.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B091_S{segment}.private.v1.jsonl"
        for segment in (1277, 1279)
    ),
    "queue_batch_id": "pk_msggame-B091",
    "queue_row_count": 158,
    "queue_visible_count": 200,
    "queue_first": "9:2514:0",
    "queue_last": "9:2671:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
