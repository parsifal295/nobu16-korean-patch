#!/usr/bin/env python3
"""Build source-redacted PK B090 segment 1274 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    2359, 2361, 2362, 2363, 2366, 2367,
    2382, 2386, 2389, 2391, 2396, 2398,
)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1274,
    queue_start=0,
    queue_stop=67,
    slice_first="9:2344:0",
    slice_last="9:2400:1",
    target_coordinates=(
        "9:2359:0",
        "9:2361:0",
        "9:2362:0",
        "9:2363:0",
        "9:2366:1",
        "9:2367:0",
        "9:2382:0",
        "9:2386:0",
        "9:2389:0",
        "9:2391:0",
        "9:2396:0",
        "9:2398:0",
    ),
    translations={
        "9:2359:0": "훗―",
        "9:2361:0": "후후―",
        "9:2362:0": "도\n",
        "9:2363:0": "글쎄―",
        "9:2366:1": "?",
        "9:2367:0": "!\n",
        "9:2382:0": "본성이 위험하다고?\n서둘러 돌아가자!",
        "9:2386:0": "본성을 노린다고?\n돌아가서 기다렸다가 치자",
        "9:2389:0": "본성이!?\n서둘러 돌아가야 한다!",
        "9:2391:0": "본성이 위험하다!\n돌아가자!",
        "9:2396:0": "좋아, 본성을 지켜\n공을 세우겠다!",
        "9:2398:0": "우리에게―",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        2359: 2,
        2361: 2,
        2362: 2,
        2363: 2,
        2366: 2,
        2367: 2,
        2382: 1,
        2386: 1,
        2389: 1,
        2391: 1,
        2396: 1,
        2398: 2,
    },
    prefill_companion_coordinates=(
        "9:2359:1",
        "9:2361:1",
        "9:2362:1",
        "9:2363:1",
        "9:2366:0",
        "9:2367:1",
        "9:2398:1",
    ),
    prefill_companion_donor={
        "9:2359:1": "9:2279:1",
        "9:2361:1": "9:2281:1",
        "9:2362:1": "9:2282:1",
        "9:2363:1": "9:2283:1",
        "9:2366:0": "9:2286:0",
        "9:2367:1": "9:2287:1",
        "9:2398:1": "9:2313:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        2359: ("9:2279:0", "9:2279:1"),
        2361: ("9:2281:0", "9:2281:1"),
        2362: ("9:2282:0", "9:2282:1"),
        2363: ("9:2283:0", "9:2283:1"),
        2366: ("9:2286:0", "9:2286:1"),
        2367: ("9:2287:0", "9:2287:1"),
        2382: ("9:2301:0",),
        2386: ("9:2304:0",),
        2389: ("9:2306:0",),
        2391: ("9:2307:0",),
        2396: ("9:2311:0",),
        2398: ("9:2313:0", "9:2313:1"),
    },
    expected_base_raw_matches={
        2359: ((9, 2279),),
        2361: ((9, 2281),),
        2362: ((9, 2282),),
        2363: ((9, 2283),),
        2366: ((9, 2286),),
        2367: ((9, 2287),),
        2382: (),
        2386: (),
        2389: (),
        2391: (),
        2396: (),
        2398: ((9, 2313),),
    },
    expected_base_literal_matches={
        2359: ((9, 2279),),
        2361: ((9, 2281),),
        2362: ((9, 2282),),
        2363: ((9, 2283),),
        2366: ((9, 2286),),
        2367: ((9, 2287),),
        2382: (),
        2386: (),
        2389: (),
        2391: (),
        2396: (),
        2398: ((9, 2313),),
    },
    expected_base_masked_matches={
        2359: ((9, 2279),),
        2361: ((9, 2281),),
        2362: ((9, 2282),),
        2363: ((9, 2283),),
        2366: ((9, 2286),),
        2367: ((9, 2287),),
        2382: (),
        2386: (),
        2389: (),
        2391: (),
        2396: (),
        2398: ((9, 2313),),
    },
    expected_controls_by_record={
        2359: ((), ("023C",)),
        2361: ((), ("023C",)),
        2362: ((1,), ("023C",)),
        2363: ((), ("023C",)),
        2366: ((17,), ()),
        2367: ((17, 1), ()),
        2382: ((), ()),
        2386: ((), ()),
        2389: ((), ()),
        2391: ((), ()),
        2396: ((), ()),
        2398: ((), ("023C",)),
    },
    source_call_roots=(1, 17),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2278, 2402)
    ),
    speaker_style=(
        (2359, "calm_tactic_failure_taunt"),
        (2361, "confident_tactic_resistance_taunt"),
        (2362, "defiant_dynamic_tactic_resistance"),
        (2363, "elderly_dismissive_tactic_taunt"),
        (2366, "critical_dynamic_strategy_assessment"),
        (2367, "triumphant_dynamic_strategy_rebuke"),
        (2382, "urgent_citadel_defense_order"),
        (2386, "calm_citadel_counterattack_order"),
        (2389, "shocked_citadel_defense_order"),
        (2391, "elderly_urgent_citadel_defense_order"),
        (2396, "ambitious_citadel_defense_boast"),
        (2398, "confident_dynamic_tactic_resistance"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("stratagem", "책략·계책"),
        ("merit", "공"),
        ("return to defend", "돌아가다"),
        ("dynamic subject particle", "이(가)"),
        ("project em dash", "―"),
        ("ASCII exclamation and question", "!·?"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "context was manually reviewed; seven exact completed Base records "
        "and five corresponding completed Base retreat-route defense records "
        "supply semantic, historical terminology, punctuation and speaker-"
        "register evidence only, with no Base runtime or VM state inherited; "
        "PK-specific inner-bailey wording consistently uses project term 본성 "
        "while "
        "the matching defense registers are contextually adapted; all twelve "
        "complete records preserve strategy tokens, dynamic speakers, subject "
        "particles, calls, inline 023C, protected whitespace, gaps and "
        "same-record prefills; all pins, two-run reproduction, tamper "
        "rejection, mutual neighbors, reverse overlays, outside-scope identity "
        "and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=9,
    pins={
        "expected_queue_universe_sha256":
        "18308D8C4224CA5E375A6D0FE7E1A809E45624F22B116F715AF2E1F30EF1F412",
        "expected_queue_slice_sha256":
        "D99221040C3409144589ADB6EC31665BDE871E9A31BD399FA85AFA451D6828E0",
        "expected_prefilled_coordinate_sha256":
        "D883E40D7C899B61F11FC81355109E6F3B20211B3ECD97DB968EF463C710F13E",
        "expected_prefill_slice_context_sha256":
        "F3AA29505CCC8D9BB982D2D58BBB1DC993B03422AEDF57EC55564EF350507F2A",
        "expected_target_coordinate_sha256":
        "69CFFB7AF9B001F58F0AECB7EC28FDFDB2DB0E03FF7327C120C914DE139FF1C5",
        "expected_source_target_sha256":
        "D5DBE36E4DBA1C89D28163AB71D4BB553BDE315846DB8C37D66ADF392B85F73E",
        "expected_current_target_sha256":
        "9E254EB2ACA02ADD92978D94FB1CD7734365E22E93D7AF9C7DE597F3F5E71009",
        "expected_context_corpus_sha256":
        "583B09AFD66AA81C069E2B5CF164513B6304C949F52A007FC568B67D319950A0",
        "expected_gap_contract_sha256":
        "A70AFAB8A36334BA58946E170AF092514EC82FDE1C607E03C5BB8C3DFA7C9E0F",
        "expected_boundary_sha256":
        "9E0558FA7D401626DDA667922408D5DB8594E816B3DFBD0E512662AACE67B13D",
        "expected_runtime_control_sha256":
        "80E5F90F231FB0B038150B9ABBA6A129D3D17F6CBFE5FEFE8A129CCD5AD5FB8F",
        "expected_base_search_sha256":
        "12E9380D5B3CE97CA89707737344B1AB876DEEFA829B345B9F28D290381A5165",
        "expected_complete_assembly_sha256":
        "6B01D76F1B68F6C6A4F327DCD03AB8E6C2A6B05F7ED16FB555911181447F00D6",
        "expected_call_graph_sha256":
        "C7DBD145766FFF7C493178FEDA26F095CDE94E8FAADAF52AC5742CD7AF2670A1",
        "expected_speaker_style_sha256":
        "DBD3FDD2BEAEE29B1240E7CEA828C757A76D78C7BC4E2F117F0659C2F99D7C86",
        "expected_terminology_policy_sha256":
        "3C9188B5DC22E7E6FBC38BD3C4B6F6CA99E8408C94079386DC16BFF82DF0C9D3",
        "expected_translation_policy_sha256":
        "FB9581E2B95126BAAC0189B891D7A1ADC4E5601E6E06185E31136E691C0E76F0",
        "expected_candidate_sha256":
        "831451CBD1BBD2B2920042DC41DAFB2EC5AFA65CCD81B866210A777B606B4A3F",
        "expected_combined_slice_candidate_sha256":
        "5461DC261ED7A7CDD9815F31EAA2ECACE256E847B4FA57971143D6BB5CDE5DB6",
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B090_S1274",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B090_S1274.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B090_S{segment}.private.v1.jsonl"
        for segment in (1275, 1276)
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
