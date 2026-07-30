#!/usr/bin/env python3
"""Build source-redacted PK B131 segment 1399 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2382:0",
    "15:2383:0",
    "15:2383:1",
    "15:2390:1",
    "15:2391:1",
    "15:2392:1",
    "15:2393:1",
    "15:2395:1",
)
TRANSLATIONS = {
    "15:2382:0": "당분간은",
    "15:2383:0": "우선",
    "15:2383:1": "의",
    "15:2390:1": "\n특히",
    "15:2391:1": "\n특히",
    "15:2392:1": "\n특히",
    "15:2393:1": "\n특히",
    "15:2395:1": "의 수입이\n다른 가문보다 넉넉한 상태",
}
TARGET_RECORD_IDS = (
    2382,
    2383,
    2390,
    2391,
    2392,
    2393,
    2395,
)
EXPECTED_ARITY = {
    2382: 3,
    2383: 3,
    2390: 4,
    2391: 4,
    2392: 4,
    2393: 4,
    2395: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2382:1",
    "15:2382:2",
    "15:2383:2",
    "15:2390:0",
    "15:2390:2",
    "15:2390:3",
    "15:2391:0",
    "15:2391:2",
    "15:2391:3",
    "15:2392:0",
    "15:2392:2",
    "15:2392:3",
    "15:2393:0",
    "15:2393:2",
    "15:2393:3",
    "15:2395:0",
    "15:2395:2",
    "15:2395:3",
)
PREFILL_COMPANION_DONOR = {
    "15:2382:1": "15:2351:1",
    "15:2382:2": "15:2351:2",
    "15:2383:2": "15:2352:2",
    "15:2390:0": "15:2359:0",
    "15:2390:2": "15:2359:2",
    "15:2390:3": "15:2359:3",
    "15:2391:0": "15:2359:0",
    "15:2391:2": "15:2359:2",
    "15:2391:3": "15:2360:3",
    "15:2392:0": "15:2359:0",
    "15:2392:2": "15:2359:2",
    "15:2392:3": "15:2361:3",
    "15:2393:0": "15:2359:0",
    "15:2393:2": "15:2359:2",
    "15:2393:3": "15:2362:3",
    "15:2395:0": "15:2364:0",
    "15:2395:2": "15:2364:2",
    "15:2395:3": "15:2364:3",
}
EXACT_BASE_DONOR = {
    2382: (15, 2351),
    2383: (15, 2352),
    2390: (15, 2359),
    2391: (15, 2360),
    2392: (15, 2361),
    2393: (15, 2362),
    2395: (15, 2364),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    2382: (),
    2383: ((15, 2352),),
    2390: (),
    2391: (),
    2392: (),
    2393: (),
    2395: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2382: ((1066, 1096, 508), ("025132",)),
    2383: ((), ("026433", "026432")),
    2390: ((748, 274, 1096, 1072), ("023C",)),
    2391: ((748, 274, 1096, 1072), ("023C",)),
    2392: ((748, 274, 1096, 1072), ("023C",)),
    2393: ((748, 274, 1096, 1072), ("023C",)),
    2395: ((550, 1078), ("023C",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1399,
    queue_start=134,
    queue_stop=199,
    slice_first="15:2361:0",
    slice_last="15:2395:3",
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
    source_call_roots=(
        274,
        508,
        550,
        748,
        1066,
        1072,
        1078,
        1096,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2290, 2396)
    ),
    speaker_style=(
        (2382, "formal_provisional_attack_policy_notice"),
        (2383, "humble_initial_target_recommendation"),
        (2390, "formal_farm_income_management_advice"),
        (2391, "formal_trade_town_income_management_advice"),
        (2392, "formal_ranch_income_management_advice"),
        (2393, "formal_forge_town_income_management_advice"),
        (2395, "formal_resource_surplus_trade_advice"),
    ),
    terminology_policy=(
        ("target", "목표"),
        ("council", "평정"),
        ("attack policy", "공략 방침"),
        ("our clan", "우리 가문"),
        ("income", "수입"),
        ("other clan", "다른 가문"),
        ("farm", "농촌"),
        ("trade town", "상인 마을"),
        ("ranch", "목장"),
        ("forge town", "대장간 마을"),
        ("county", "군"),
        ("officer", "무장"),
        ("war", "전쟁"),
        ("poor harvest", "흉작"),
        ("trade", "거래"),
        ("particle compatibility", "을(를)"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B131 queue ordinals one hundred "
        "thirty-four through one hundred ninety-eight and the approved Base "
        "prefill; pristine PK JP is authoritative and every populated EN, "
        "SC and TC same-record fragment array was reviewed as auxiliary "
        "context; all seven complete records reuse approved completed Base "
        "Korean assemblies selected by raw, literal and operand-masked "
        "source identity with explicit exact donors; Base runtime and VM "
        "state are never inherited; targets, councils, attack policies, our "
        "clan, income, farms, trade towns, ranches, forge towns, counties, "
        "officers, war, poor harvests and trade retain established "
        "historical project wording and formal or humble advisory "
        "registers; direct calls, inline house, castle and resource tokens, "
        "protected outer whitespace, newlines, gaps, literal arity, "
        "particles, terminators, all eighteen same-record prefills, all "
        "fifty-seven slice prefills, complete assemblies, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1397 and S1398 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=1,
    pins={
        "expected_queue_universe_sha256": (
            "C98584FBA86F034B3D1EDB74FE505FABF0191EAA9CE21141CCF11AF9D49ECA1C"
        ),
        "expected_queue_slice_sha256": (
            "69340B316F8A22F60DA9F3AEB6F218914306A3701B3A0DE788398DBC62B0B954"
        ),
        "expected_prefilled_coordinate_sha256": (
            "26F96F5D2CE7C3C3F4410BB516BF0F4E348AE72F3AD4C069CED7E37A3131B4A7"
        ),
        "expected_prefill_slice_context_sha256": (
            "C26962FA40E6700932CD51F306C91B58D046324B18078707C94751451F4A3581"
        ),
        "expected_target_coordinate_sha256": (
            "38D448D10739143CD7C5AC2A94AE5E232546DD690928B15675E1B482A21B1130"
        ),
        "expected_source_target_sha256": (
            "3A3FF5417A130995620F820E1FA5A608CB034B72529C4EB2699C3FDC9172584F"
        ),
        "expected_current_target_sha256": (
            "9E57CA1CC195A9A4819D5329BA874829F37E83BF6281F32C32C909B120771D16"
        ),
        "expected_context_corpus_sha256": (
            "C0BD248F6F4B7D220B70CF8AD2606064283CF27DF1E0537B1BFD9B6059DD62FB"
        ),
        "expected_gap_contract_sha256": (
            "E1E220402D2FB221D9C66588DBDCB1629A99A6F78A16C2AF1787EBB8EE1ED738"
        ),
        "expected_boundary_sha256": (
            "7093BAE5081E016280640585D125B91D64D8E169A8D59A87A8507B5098E2EE7C"
        ),
        "expected_runtime_control_sha256": (
            "C6444D7EF5F21B55079296189B40836D8574A30E5B29437A504BA2A768435439"
        ),
        "expected_base_search_sha256": (
            "99BDF32EA5E832F53A98B28C64D4EA039C847B679AA4F04111E2ACB970BD8E70"
        ),
        "expected_complete_assembly_sha256": (
            "F7AB1D1C244C6ED8966972B8498C4918528ED5CDD43B031FE8B146A41FE3A2A7"
        ),
        "expected_call_graph_sha256": (
            "B9247EC7EE66EC7A3E5F9FBF659CF1AB896BEBE9A8F38BBFBE26B5E489BAB42A"
        ),
        "expected_speaker_style_sha256": (
            "9ADC1500212EBA99CC0946AC00C087AF914ADABDE370FC915F36DD49B727511A"
        ),
        "expected_terminology_policy_sha256": (
            "17347400D4A61C07B318AC146BF9CBC2C75CB996521A7C971F33C290BAA3C048"
        ),
        "expected_translation_policy_sha256": (
            "DB98B0363217B7F20023655270E299AF2A94666D4DE64F66089BA862E6961C6E"
        ),
        "expected_candidate_sha256": (
            "54558D4D2028C1914AE0439E0F42FCC9E10DE9CD23745C76227F943951114869"
        ),
        "expected_combined_slice_candidate_sha256": (
            "57563576183071688D486AAF1E582C90910B61DE0829A8471AE8FBCEECD73A92"
        ),
        "expected_combined_changed_literal_count": 55,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B131_S1399",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1399.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1397.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1398.private.v1.jsonl",
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
