#!/usr/bin/env python3
"""Build source-redacted PK B092 segment 1281 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (2740, 2743, 2751)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1281,
    queue_start=67,
    queue_stop=134,
    slice_first="9:2737:0",
    slice_last="9:2799:0",
    target_coordinates=(
        "9:2740:0",
        "9:2743:0",
        "9:2751:1",
    ),
    translations={
        "9:2740:0": "첫 공은―",
        "9:2743:0": "첫 공은―",
        "9:2751:1": "을(를) 따르라!",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        2740: 2,
        2743: 2,
        2751: 2,
    },
    prefill_companion_coordinates=(
        "9:2740:1",
        "9:2743:1",
        "9:2751:0",
    ),
    prefill_companion_donor={
        "9:2740:1": "9:2641:1",
        "9:2743:1": "9:2644:1",
        "9:2751:0": "9:2652:0",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        2740: ("9:2641:0", "9:2641:1"),
        2743: ("9:2644:0", "9:2644:1"),
        2751: ("9:2652:0", "9:2652:1"),
    },
    expected_base_raw_matches={
        2740: ((9, 2641),),
        2743: ((9, 2644),),
        2751: ((9, 2652),),
    },
    expected_base_literal_matches={
        2740: ((9, 2641),),
        2743: ((9, 2644),),
        2751: ((9, 2652),),
    },
    expected_base_masked_matches={
        2740: ((9, 2641),),
        2743: ((9, 2644),),
        2751: ((9, 2652),),
    },
    expected_controls_by_record={
        2740: ((1,), ()),
        2743: ((1,), ()),
        2751: ((1,), ()),
    },
    source_call_roots=(1,),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2640, 2801)
    ),
    speaker_style=(
        (2740, "rough_dynamic_first_honor_charge"),
        (2743, "commanding_dynamic_first_honor_claim"),
        (2751, "martial_dynamic_follow_order"),
    ),
    terminology_policy=(
        ("first battlefield honor", "첫 공"),
        ("dynamic nominative particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("charge order", "돌격하라"),
        ("follow order", "따르라"),
        ("project em dash", "―"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record context was manually reviewed; all three records are "
        "raw-exact matches to completed Base records, whose translations "
        "supply semantic wording, historical first-battlefield-honor "
        "terminology, punctuation and speaker register only; Base runtime and "
        "VM state are never inherited; the historical battlefield distinction "
        "is consistently rendered 첫 공 rather than the unrelated commander "
        "title 선봉장; all three complete dynamic records preserve the speaker "
        "call, protected newline, particles, literal arity, gaps and approved "
        "same-record prefill companions; all pins, two-run reproduction, "
        "tamper rejection, mutual neighbors, reverse overlays, outside-scope "
        "identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256":
        "D112DC2DD9E7B7D75A0C48FA78A3D1B8EF53DFC4D238705DF9DD3EE01F7967CE",
        "expected_queue_slice_sha256":
        "61459D52C974840F7FAD7872086B36F20EF6913A20B6371F56F82F4DB4EB7987",
        "expected_prefilled_coordinate_sha256":
        "16E46CEFAEFF6B15E65B10039ED866D51C4A22234EDC089B335B96703E6800A6",
        "expected_prefill_slice_context_sha256":
        "84A802F27C2BBAD14825A5A9B0AF6871C139D59613E1A5F4E9D38873AE382ADC",
        "expected_target_coordinate_sha256":
        "2ADDCD3848FDE220B110777A8141B57CF9842D5F45D6237735D4AAE93808D331",
        "expected_source_target_sha256":
        "8A91F7D0DA8863E8CBD0B509D64E0A412C72A5419C1E8D41C5B381FB2ACB994E",
        "expected_current_target_sha256":
        "6E86C6C090CB14305C0447ADFF29FDFF9C8D835C96B19778D15019B3AF3F758C",
        "expected_context_corpus_sha256":
        "E227A8FF6FFDF454C180D92D717DD81741701AA85FDC41E8829BA5EA214C0821",
        "expected_gap_contract_sha256":
        "982AE10290EF1C60F06E29F43B497515818E45FA347B730E04B8D57017ECFA85",
        "expected_boundary_sha256":
        "A95FC0D333CFF964265387EA3891EFD1E63979CCA421CF1C93D8D61F673FE845",
        "expected_runtime_control_sha256":
        "299963A3DB01F752963491CABC4DA5A22AA919DFCC0CA4B96CCD7E0F8B383B44",
        "expected_base_search_sha256":
        "057C8F2C72DE3E6D279C7BE2C257F9CF76BA9A0DDDED5BDC5701F32192CD48C6",
        "expected_complete_assembly_sha256":
        "E4232AA76D8CD0AE234E7C1786E2A5280EF5E3D28A43010AF8A798D6C06D1E57",
        "expected_call_graph_sha256":
        "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD",
        "expected_speaker_style_sha256":
        "BBFE554E3EB7A036B77E93C3F1E8BD18D9D544D66B85F45804D0A74A38E5281A",
        "expected_terminology_policy_sha256":
        "337422D7CB405B0C8A11C5A827CF5DB67FEDD09908E24492390082258F89EA63",
        "expected_translation_policy_sha256":
        "CDA0EE8F2C22577D5949A8B03B9DFD6D306E3D22C228073DA78F3AAADA5F9A30",
        "expected_candidate_sha256":
        "E832CF229E209BE8094A926ADDC2440D8C529FE5D304B904B819BAF7953288DF",
        "expected_combined_slice_candidate_sha256":
        "A5FC81C66DB971D13392C28C000FF86D57B60AD413AC05ABEF840CBB0426218F",
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B092_S1281",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B092_S1281.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B092_S{segment}.private.v1.jsonl"
        for segment in (1280, 1282)
    ),
    "queue_batch_id": "pk_msggame-B092",
    "queue_row_count": 194,
    "queue_visible_count": 200,
    "queue_first": "9:2672:0",
    "queue_last": "9:2865:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
