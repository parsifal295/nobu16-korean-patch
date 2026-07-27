#!/usr/bin/env python3
"""Build source-redacted PK B091 segment 1279 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    2633, 2634, 2635, 2636, 2637, 2638, 2639, 2640, 2641, 2642, 2643,
    2644, 2645, 2647, 2648, 2649, 2650, 2652, 2653, 2654, 2655, 2656,
    2657, 2658, 2659, 2660, 2661, 2663,
)
TARGET_COORDINATES = (
    "9:2633:0",
    "9:2634:0",
    "9:2635:0",
    "9:2636:0",
    "9:2637:0",
    "9:2638:0",
    "9:2639:0",
    "9:2640:0",
    "9:2641:0",
    "9:2642:0",
    "9:2643:0",
    "9:2644:0",
    "9:2644:1",
    "9:2645:1",
    "9:2647:1",
    "9:2648:0",
    "9:2649:0",
    "9:2650:1",
    "9:2652:1",
    "9:2653:1",
    "9:2654:1",
    "9:2655:0",
    "9:2656:0",
    "9:2657:1",
    "9:2658:0",
    "9:2658:1",
    "9:2658:2",
    "9:2658:3",
    "9:2659:1",
    "9:2660:1",
    "9:2661:0",
    "9:2661:1",
    "9:2661:2",
    "9:2663:1",
)
TRANSLATIONS = {
    "9:2633:0": "본성에 적군이!\n즉시 요격한다!",
    "9:2634:0": "본성을 잃을 수는 없다\n요격하러 간다!",
    "9:2635:0": "본성을 노리는 군세라고?\n서둘러 쳐부수겠습니다",
    "9:2636:0": "본성을 내줄 성싶으냐!\n",
    "9:2637:0": "본성이 위태로운가\n그리로 향해야겠군",
    "9:2638:0": "본성을 노리다니……\n우리가 요격하러 간다",
    "9:2639:0": "본성을 노리다니 괘씸하구나\n",
    "9:2640:0": "본성이 위험합니다!\n요격하겠습니다!",
    "9:2641:0": "본성에 괴한이 나타났다!\n이 몸―",
    "9:2642:0": "본성을 지켜야 합니다\n적군을 요격하겠습니다",
    "9:2643:0": "본성이 위태롭다\n요격한다!",
    "9:2644:0": "선봉대―",
    "9:2644:1": "이(가) 전투를 시작한다",
    "9:2645:1": "이다!",
    "9:2647:1": "―나아간다!",
    "9:2648:0": "이 몸―",
    "9:2649:0": "은(는)",
    "9:2650:1": "이다!",
    "9:2652:1": "이니라!",
    "9:2653:1": "의 몫입니다!",
    "9:2654:1": "이다!",
    "9:2655:0": "이 몸―",
    "9:2656:0": "이 몸―",
    "9:2657:1": "이다!",
    "9:2658:0": "선두 돌격은―",
    "9:2658:1": "우리 신구당",
    "9:2658:2": "이 맡는다!\n모두, 이 몸―",
    "9:2658:3": "을(를) 따르라!",
    "9:2659:1": "이다!",
    "9:2660:1": "의 나나테구미,\n",
    "9:2661:0": "―",
    "9:2661:1": "오니미노",
    "9:2661:2": "가\n적진에 가장 먼저 돌입한다!",
    "9:2663:1": "(이)로다!",
}
EXPECTED_ARITY = {
    2633: 1,
    2634: 1,
    2635: 1,
    2636: 2,
    2637: 1,
    2638: 1,
    2639: 2,
    2640: 1,
    2641: 2,
    2642: 1,
    2643: 1,
    2644: 2,
    2645: 2,
    2647: 2,
    2648: 2,
    2649: 2,
    2650: 2,
    2652: 2,
    2653: 2,
    2654: 2,
    2655: 2,
    2656: 2,
    2657: 2,
    2658: 4,
    2659: 2,
    2660: 3,
    2661: 3,
    2663: 2,
}
PREFILL_COMPANION_DONOR = {
    "9:2636:1": "9:2537:1",
    "9:2639:1": "9:2540:1",
    "9:2641:1": "9:2542:1",
    "9:2645:0": "9:2546:0",
    "9:2647:0": "9:2548:0",
    "9:2648:1": "9:2549:1",
    "9:2649:1": "9:2550:1",
    "9:2650:0": "9:2551:0",
    "9:2652:0": "9:2553:0",
    "9:2653:0": "9:2554:0",
    "9:2654:0": "9:2555:0",
    "9:2655:1": "9:2556:1",
    "9:2656:1": "9:2557:1",
    "9:2657:0": "9:2558:0",
    "9:2659:0": "9:2560:0",
    "9:2660:0": "9:2561:0",
    "9:2660:2": "9:2561:2",
    "9:2663:0": "9:2564:0",
}
SEMANTIC_BASE_CONTEXT = {
    2633: ("9:2534:0",),
    2634: ("9:2535:0",),
    2635: ("9:2536:0",),
    2636: ("9:2537:0", "9:2537:1"),
    2637: ("9:2538:0",),
    2638: ("9:2539:0",),
    2639: ("9:2540:0", "9:2540:1"),
    2640: ("9:2541:0",),
    2641: ("9:2542:0", "9:2542:1"),
    2642: ("9:2543:0",),
    2643: ("9:2544:0",),
    2644: ("9:2545:0", "9:2545:1"),
    2645: ("9:2546:0", "9:2546:1"),
    2647: ("9:2548:0", "9:2548:1"),
    2648: ("9:2549:0", "9:2549:1"),
    2649: ("9:2550:0", "9:2550:1"),
    2650: ("9:2551:0", "9:2551:1"),
    2652: ("9:2553:0", "9:2553:1"),
    2653: ("9:2554:0", "9:2554:1"),
    2654: ("9:2555:0", "9:2555:1"),
    2655: ("9:2556:0", "9:2556:1"),
    2656: ("9:2557:0", "9:2557:1"),
    2657: ("9:2558:0", "9:2558:1"),
    2658: ("9:2559:0", "9:2559:1"),
    2659: ("9:2560:0", "9:2560:1"),
    2660: ("9:2561:0", "9:2561:1", "9:2561:2"),
    2661: ("9:2562:0",),
    2663: ("9:2564:0", "9:2564:1"),
}
EXACT_BASE_RECORD = {
    2644: 2545,
    2645: 2546,
    2647: 2548,
    2648: 2549,
    2649: 2550,
    2650: 2551,
    2652: 2553,
    2653: 2554,
    2654: 2555,
    2655: 2556,
    2656: 2557,
    2657: 2558,
    2659: 2560,
    2660: 2561,
    2663: 2564,
}
EXPECTED_BASE_MATCHES = {
    record_id: (
        ((9, EXACT_BASE_RECORD[record_id]),)
        if record_id in EXACT_BASE_RECORD
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    2633: ((), ()),
    2634: ((), ()),
    2635: ((), ()),
    2636: ((1,), ()),
    2637: ((), ()),
    2638: ((), ()),
    2639: ((1,), ()),
    2640: ((), ()),
    2641: ((4,), ()),
    2642: ((), ()),
    2643: ((), ()),
    2644: ((), ("02AA32",)),
    2645: ((), ("024633",)),
    2647: ((), ("024633",)),
    2648: ((), ("024633",)),
    2649: ((1,), ("024633",)),
    2650: ((), ("024633",)),
    2652: ((), ("024633",)),
    2653: ((), ("024633",)),
    2654: ((), ("024633",)),
    2655: ((), ("024633",)),
    2656: ((), ("024633",)),
    2657: ((), ("024635",)),
    2658: ((), ("024635",)),
    2659: ((), ("024633",)),
    2660: ((), ("02463E", "024633")),
    2661: ((), ("024634",)),
    2663: ((), ("024633",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1279,
    queue_start=134,
    queue_stop=200,
    slice_first="9:2633:0",
    slice_last="9:2671:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=tuple(PREFILL_COMPANION_DONOR),
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1, 4),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2533, 2673)
    ),
    speaker_style=(
        (2633, "rough_immediate_citadel_interception"),
        (2634, "resolute_citadel_defense"),
        (2635, "polite_citadel_counterattack"),
        (2636, "rough_dynamic_citadel_defense"),
        (2637, "calm_citadel_danger_response"),
        (2638, "collective_citadel_counterattack"),
        (2639, "lordly_dynamic_citadel_counterattack"),
        (2640, "polite_immediate_citadel_interception"),
        (2641, "boastful_dynamic_intruder_punishment"),
        (2642, "polite_citadel_protection"),
        (2643, "blunt_citadel_interception"),
        (2644, "dynamic_vanguard_battle_opening"),
        (2645, "rough_dynamic_first_honor_boast"),
        (2647, "confident_dynamic_first_honor_charge"),
        (2648, "polite_dynamic_first_honor_claim"),
        (2649, "lordly_dynamic_first_honor_claim"),
        (2650, "assertive_dynamic_first_honor_claim"),
        (2652, "elderly_dynamic_first_honor_claim"),
        (2653, "polite_dynamic_first_honor_claim"),
        (2654, "rough_dynamic_first_honor_claim"),
        (2655, "polite_dynamic_first_honor_claim"),
        (2656, "blunt_dynamic_first_honor_claim"),
        (2657, "historical_banner_vanguard_boast"),
        (2658, "historical_group_vanguard_boast"),
        (2659, "historical_red_unit_vanguard_boast"),
        (2660, "historical_group_first_honor_boast"),
        (2661, "historical_nickname_first_entry_boast"),
        (2663, "historical_helmet_vanguard_boast"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("interception", "요격"),
        ("vanguard unit", "선봉대"),
        ("first battlefield honor", "첫 공"),
        ("self reference", "이 몸"),
        ("historical banner name", "지키하치만"),
        ("historical group name", "우리 신구당"),
        ("historical seven squads", "나나테구미"),
        ("historical nickname", "오니미노"),
        ("dynamic Korean particles", "이(가)·은(는)·(이)로다"),
        ("project em dash", "―"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "pristine PK JP is authoritative and complete EN, SC and TC "
        "same-record arrays were manually reviewed as auxiliary evidence; "
        "completed Base records provide semantic wording and historical "
        "terminology only, with exact source matches additionally confirmed "
        "where present and no Base runtime or VM state inherited; the citadel "
        "defense variants preserve each rough, calm, polite, collective and "
        "lordly register, while the vanguard variants consistently use 본성, "
        "요격, 선봉대 and 첫 공 and retain the established historical forms "
        "지키하치만, 신구당, 나나테구미 and 오니미노; dynamic calls, Korean "
        "particles, color-span boundaries, protected newlines, literal arity, "
        "gaps, inline tokens and all approved same-record prefill companions "
        "are guarded; two-run reproduction, tamper rejection, left and mutual "
        "neighbors, reverse overlays, outside-scope identity and Steam "
        "read-only state are also guarded"
    ),
    expected_changed_literal_count=30,
    pins={
        "expected_queue_universe_sha256":
        "F883FCE6B74C91BB99B867D39D3B13E68CD9B7C4A729E9624333101CC44264DA",
        "expected_queue_slice_sha256":
        "ADCA61377AF85A982B41AF262D12EF752C976F2ABF693451736F57D667C9DADF",
        "expected_prefilled_coordinate_sha256":
        "4C09A1D64D72A13E582C67CF28FD7BFC4E17F4F0DC0A94B07B69AD200826CAF6",
        "expected_prefill_slice_context_sha256":
        "5B90FF47B794C98DA228FFDF0F89248BE1C89C277B0384805C2066EAB8BD3FB5",
        "expected_target_coordinate_sha256":
        "BC2C1A14806C3B09285097BBC2A7838BBC77539B66C537F9B754F6DFC73F50DF",
        "expected_source_target_sha256":
        "9BCA5B70C8208FF7049E79A9F33D239221C0508916229187792B116ADA7A81F7",
        "expected_current_target_sha256":
        "D154BEE96411218FFDDB41AD5BE86A4B26961081DDB1CB4FE47F862A020EBDD0",
        "expected_context_corpus_sha256":
        "8ED338F0175EE5F504BFAAE893C65837096124BC13E667B98BDCEB21489109D1",
        "expected_gap_contract_sha256":
        "AD4D5F7EA58BEC23DDE292599A5415A44A48F5FB65687ED84197C974055D26D2",
        "expected_boundary_sha256":
        "1338AB08600A44F419649CE53D923AA94D90C6523EA38CDE058A354745CDB20B",
        "expected_runtime_control_sha256":
        "EDC0D76759666AB8C0192120C80601FB2F412E554E75A524A6B9305ED14A8365",
        "expected_base_search_sha256":
        "98EF48B3800D72E81F1ADCEC7117110948F557379E3CD14B47AB48516041B907",
        "expected_complete_assembly_sha256":
        "45409081C237D0BA07BAB2CC9504BB6D147EE54705A5BE471D76A27F73DD9277",
        "expected_call_graph_sha256":
        "E11C6DE6803FECD269617B7C3FB8CD3134087F6D7F4D3D70A033F24AF300E657",
        "expected_speaker_style_sha256":
        "5E3233D19A9B2FD0AE44424D913F15849692D91B88245E105CA21854010B86B4",
        "expected_terminology_policy_sha256":
        "7C490A03293433EFE3BFAFFEFBEE28CC284D1FC61C61F4E5C39E14B4BDE15BF0",
        "expected_translation_policy_sha256":
        "408DCC0B6C10ACDAF3E22451DF85AC6756016C2D27C90EB36C576EB6FF4C608A",
        "expected_candidate_sha256":
        "D35B67B6ECBFEE7704B85B25F4C0F6FA61CE1895712FADDF69D2E1694F595922",
        "expected_combined_slice_candidate_sha256":
        "47969C502ABE801BBD0C22D307F7C7B0260480A5B9E4266F9B21B08AB8D177D3",
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B091_S1279",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B091_S1279.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B090_S1276.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B091_S1277.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B091_S1278.private.v1.jsonl",
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
