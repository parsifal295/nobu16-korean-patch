#!/usr/bin/env python3
"""Build source-redacted PK B090 segment 1276 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (2471, 2475, 2480, 2482)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1276,
    queue_start=134,
    queue_stop=200,
    slice_first="9:2458:0",
    slice_last="9:2513:0",
    target_coordinates=(
        "9:2471:1",
        "9:2475:1",
        "9:2480:0",
        "9:2482:0",
    ),
    translations={
        "9:2471:1": "의 부대와 교대한다!",
        "9:2475:1": "의 부대와 교대다!",
        "9:2480:0": "진군하라!\n",
        "9:2482:0": "나아가라!\n",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={record_id: 2 for record_id in TARGET_RECORD_IDS},
    prefill_companion_coordinates=(
        "9:2471:0",
        "9:2475:0",
        "9:2480:1",
        "9:2482:1",
    ),
    prefill_companion_donor={
        "9:2471:0": "9:2384:0",
        "9:2475:0": "9:2388:0",
        "9:2480:1": "9:2390:1",
        "9:2482:1": "9:2395:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        2471: ("9:2384:0", "9:2384:1"),
        2475: ("9:2388:0", "9:2388:1"),
        2480: ("9:2393:0", "9:2393:1"),
        2482: ("9:2395:0", "9:2395:1"),
    },
    expected_base_raw_matches={
        2471: ((9, 2384),),
        2475: ((9, 2388),),
        2480: ((9, 2393),),
        2482: ((9, 2395),),
    },
    expected_base_literal_matches={
        2471: ((9, 2384),),
        2475: ((9, 2388),),
        2480: ((9, 2393),),
        2482: ((9, 2395),),
    },
    expected_base_masked_matches={
        2471: ((9, 2384),),
        2475: ((9, 2388),),
        2480: ((9, 2393),),
        2482: ((9, 2395),),
    },
    expected_controls_by_record={
        2471: ((29,), ()),
        2475: ((29,), ()),
        2480: ((29,), ()),
        2482: ((29,), ()),
    },
    source_call_roots=(29,),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2383, 2515)
    ),
    speaker_style=(
        (2471, "assertive_dynamic_unit_replacement_order"),
        (2475, "elderly_dynamic_unit_replacement_order"),
        (2480, "resolute_dynamic_unit_replacement_order"),
        (2482, "elderly_dynamic_unit_replacement_order"),
    ),
    terminology_policy=(
        ("advance", "진군하다·나아가다"),
        ("military unit", "부대"),
        ("replace or relieve", "교대하다"),
        ("dynamic genitive", "의"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "context was manually reviewed; all four exact completed Base records "
        "supply semantic, military terminology, punctuation and speaker-"
        "register evidence only, with no Base runtime or VM state inherited; "
        "dynamic officer names use the stable genitive-unit construction 의 "
        "부대와 before 교대하다, while the distinct advance registers remain "
        "진군하라 and 나아가라; every complete record preserves the officer "
        "call, protected newline, gap and approved same-record prefill; all "
        "pins, two-run reproduction, tamper rejection, mutual neighbors, "
        "reverse overlays, outside-scope identity and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=3,
    pins={
        "expected_queue_universe_sha256":
        "18308D8C4224CA5E375A6D0FE7E1A809E45624F22B116F715AF2E1F30EF1F412",
        "expected_queue_slice_sha256":
        "10A6F36ABC165489EEFF08232FBCF88BF1786ED3A6361DA3E2B054320F2783D2",
        "expected_prefilled_coordinate_sha256":
        "782584D00B1A86BE01DE577C775A16AC6E2727836A723C093ED043D1A3D55ADC",
        "expected_prefill_slice_context_sha256":
        "F3A9F0861B30EC9F14070FFA477F3D00E3A8D88EA10DA1262697707BBFE04A76",
        "expected_target_coordinate_sha256":
        "76645D3F3A4EEED7C2CE505AAF7062364DD56AACD578D8ADC7B940680025BCD1",
        "expected_source_target_sha256":
        "BE35F34CCFD4282BBED8E12B3E8CF4A43E866EF7DA453D581F0C51D3D13DD6F6",
        "expected_current_target_sha256":
        "F28D6AF6E87394F995F107857DA702387B9B4991BD976E50828317118C193596",
        "expected_context_corpus_sha256":
        "583B09AFD66AA81C069E2B5CF164513B6304C949F52A007FC568B67D319950A0",
        "expected_gap_contract_sha256":
        "72378446DDC845952DC4F21FEF69085B61A4CD782432F2EF98A4CEA182005FF6",
        "expected_boundary_sha256":
        "FD0EB8B0ECF10C80B8A7E8687AD6C5764DE5222530E875CC2C3006DDA9947396",
        "expected_runtime_control_sha256":
        "5A0AE6F376A2B7C27B76981A53B4B3B5A4A4293C994F5E344F947B445782AE4D",
        "expected_base_search_sha256":
        "BFC4412F20CE009CBF498FB3AC2DCFE7BA96798B200CC41AB9D2AC24FA6BA135",
        "expected_complete_assembly_sha256":
        "450DA9190AF42C5C13DBEA69C267B2D0242BE78DA355880464FFD8A393FE9BB1",
        "expected_call_graph_sha256":
        "3E08433FC9F8D91314F1B1B3CD107876F56C0D766E283E9EA513A83AB63F7914",
        "expected_speaker_style_sha256":
        "20362F01729F95AAD6237E4D113F6626BA336F26843BFF4E87BE1E13AB3B46B5",
        "expected_terminology_policy_sha256":
        "B3F7FC8ACBB6A20E7C8E3D65CC87D9CB962BF6844047F4A3F35029BD980BCBF3",
        "expected_translation_policy_sha256":
        "272637B1938AA8DA109BBDD8A46021A88EA167E8875BCB4CAA07E2053AC4E130",
        "expected_candidate_sha256":
        "40B390C77D7D29C3B0C2D6642A40FFEEE421A26744DB3551EB402ECCF87E227A",
        "expected_combined_slice_candidate_sha256":
        "7B5FD89D8ACFF64F834C2BC9C53C6E539B043270A6878800B7B898A83037B4F8",
        "expected_combined_changed_literal_count": 57,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B090_S1276",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B090_S1276.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B090_S{segment}.private.v1.jsonl"
        for segment in (1274, 1275)
    ),
    "queue_batch_id": "pk_msggame-B090",
    "queue_row_count": 170,
    "queue_visible_count": 200,
    "queue_first": "9:2344:0",
    "queue_last": "9:2513:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
