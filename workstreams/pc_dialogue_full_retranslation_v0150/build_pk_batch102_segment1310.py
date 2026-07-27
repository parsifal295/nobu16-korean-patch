#!/usr/bin/env python3
"""Build source-redacted PK B102 segment 1310 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (100, 105, 120, 123)
TARGET_COORDINATES = (
    "13:100:0",
    "13:105:1",
    "13:120:0",
    "13:123:0",
)
TRANSLATIONS = {
    "13:100:0": "외람된 말씀이오나 이",
    "13:105:1": "\"에게\n",
    "13:120:0": "영토의 발전을 생각하신다면\n정무에 능한 \"",
    "13:123:0": "외람되오나 이",
}
EXPECTED_ARITY = {
    100: 2,
    105: 4,
    120: 2,
    123: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "13:100:1",
    "13:105:0",
    "13:105:2",
    "13:105:3",
    "13:120:1",
    "13:123:1",
    "13:123:2",
)
PREFILL_COMPANION_DONOR = {
    "13:100:1": "13:100:1",
    "13:105:0": "13:105:0",
    "13:105:2": "13:105:2",
    "13:105:3": "13:105:3",
    "13:120:1": "13:120:1",
    "13:123:1": "13:123:1",
    "13:123:2": "13:112:2",
}
SEMANTIC_BASE_CONTEXT = {
    100: (),
    105: (),
    120: (),
    123: ("13:123:0", "13:123:1", "13:112:2"),
}
EXPECTED_BASE_RAW_MATCHES = {
    100: ((13, 100),),
    105: ((13, 105),),
    120: ((13, 120),),
    123: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    100: ((13, 100),),
    105: ((13, 105),),
    120: ((13, 120),),
    123: ((13, 123),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    100: ((), ("024635",)),
    105: ((94,), ("024833",)),
    120: ((), ("024833",)),
    123: ((1078, 322), ("024635",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1310,
    queue_start=0,
    queue_stop=67,
    slice_first="13:99:0",
    slice_last="13:131:0",
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
    source_call_roots=(94, 322, 1078),
    boundary_record_keys=tuple(
        (13, record_id) for record_id in range(97, 135)
    ),
    speaker_style=(
        (100, "humble_self_military_leadership_recommendation"),
        (105, "formal_retainer_trait_recommendation"),
        (120, "formal_domestic_affairs_recommendation"),
        (123, "humble_self_leadership_recommendation"),
    ),
    terminology_policy=(
        ("humble preface", "외람된 말씀이오나·외람되오나"),
        ("military leadership", "병사를 지휘하는 기량·통솔력"),
        ("house", "우리 가문"),
        ("vassal", "가신"),
        ("trait", "특성"),
        ("territory", "영토"),
        ("administration", "정무·내정"),
        ("dynamic honorific", "님"),
        ("dynamic particles", "에게"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were reviewed as auxiliary evidence; records "
        "100, 105 and 120 are byte-exact with their completed Base donors "
        "and therefore reproduce the verified complete Korean assemblies, "
        "while record 123 uses three individually approved completed Base "
        "semantic fragments without inheriting Base runtime or VM state; "
        "humble self-recommendation and formal retainer-recommendation "
        "registers remain distinct; military leadership, house, vassal, "
        "trait, territory, administration, honorific and dynamic-particle "
        "terminology follows the project glossary and completed corpus; "
        "quotes around dynamic names and traits, calls 94, 322 and 1078, "
        "inline tokens, protected newlines, gaps, terminators, complete "
        "record arity, all sixty-three slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=3,
    pins={
        "expected_queue_universe_sha256":
        "304DE44FD56B7FE14C31772C0E044FC7EF552CBC10AB796C446205949EA1D982",
        "expected_queue_slice_sha256":
        "B9D01AEEDB15E12AB160EE8887C43E2D907A936E906650C9C77ADC06C2F3958E",
        "expected_prefilled_coordinate_sha256":
        "EC9CB545D158F9C650E29255697FB11A2F45B32A4E72C3F2942A0955C0B6B7CD",
        "expected_prefill_slice_context_sha256":
        "711815FEE3595F3794415DEBF57A53C7350E98DB1C98EBE698F69D85F0DD8858",
        "expected_target_coordinate_sha256":
        "592FAA5171635595FD43B3263AF54F31D8A3F1C7427181286F9C10BDC3B5E3D1",
        "expected_source_target_sha256":
        "6584C0B0E0E7B20DA1140EDC5DED72FEB13575B0CE9F6F394318D08FBB1074E6",
        "expected_current_target_sha256":
        "AE96570509326845F04051D8095F7BDD4EEDF77B0C764B1B411CCCC8D499CB6C",
        "expected_context_corpus_sha256":
        "8EB4E732C0CA08CB38F28FA8629BC0766EBAF3C622CABF592B068BEB21062D3A",
        "expected_gap_contract_sha256":
        "73F4580AE98F67378676A5B5A99F53B0D1199E34E3492A7C2B4F509C58321439",
        "expected_boundary_sha256":
        "EBE65A18C24CEA1BD2A30D8D66E70A2D8528BD4DE2D2A03BCFCD6FFA789BD012",
        "expected_runtime_control_sha256":
        "03AD0E759388A464752C3836E9E7E24785F5FD6D488F9F04173A719F9DA4279A",
        "expected_base_search_sha256":
        "62EC88FC85D0ED323D33F978FCE10D80C7B2C68D08BE173A36AB13F2F2C00B10",
        "expected_complete_assembly_sha256":
        "FF127D518F47853807C8B41201A69989CD4AB68EA50A7EBA770F4F60D18B8C49",
        "expected_call_graph_sha256":
        "EAE35272EBFB490791ACACE83D840C9234ACB92314B66C3E48DFE4A8D07C8FBD",
        "expected_speaker_style_sha256":
        "70CA6D91978F2584D3D852D9BD64346212959F7CB1999DD9DD3B7226B26FA473",
        "expected_terminology_policy_sha256":
        "E004316BB3B0EDEB6FBBE2CE7E7F0F7486842877FEF85A5FA681ED2A58DF1310",
        "expected_translation_policy_sha256":
        "94A986F07401A7A4B4C0EDA6456298B42C95F5ACEE19125F302854D94FDF1F27",
        "expected_candidate_sha256":
        "D7177A6D77632546F988DFB803338EB3BE2BF2CF31206380196284EA3A096598",
        "expected_combined_slice_candidate_sha256":
        "55E94116B54FB61DF38B18BA66662FC94310DE91AB5BBFFBC67CF8AF89DC86E0",
        "expected_combined_changed_literal_count": 63,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B102_S1310",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B102_S1310.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B101_S1309.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B102_S1311.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B102",
    "queue_row_count": 155,
    "queue_visible_count": 200,
    "queue_first": "13:99:0",
    "queue_last": "13:253:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 13)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            100: (13, 100),
            105: (13, 105),
            120: (13, 120),
        },
    )


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
