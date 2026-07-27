#!/usr/bin/env python3
"""Build source-redacted PK B129 segment 1392 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2137:1",
    "15:2138:1",
    "15:2146:1",
    "15:2149:1",
    "15:2151:2",
    "15:2157:0",
)
TRANSLATIONS = {
    "15:2137:1": "을(를) 건의",
    "15:2138:1": "의 실행을 허락해 주시옵소서\n",
    "15:2146:1": "의 실행을 허락해 주시오",
    "15:2149:1": "을(를) 추진하고자 하오",
    "15:2151:2": "의 시행을 허락해 주시기를 청하옵니다",
    "15:2157:0": "의 시행을 허락해 주시기를 바라오\n",
}
TARGET_RECORD_IDS = (
    2137,
    2138,
    2146,
    2149,
    2151,
    2157,
)
EXPECTED_ARITY = {
    2137: 2,
    2138: 3,
    2146: 2,
    2149: 2,
    2151: 3,
    2157: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2137:0",
    "15:2138:2",
    "15:2146:0",
    "15:2149:0",
    "15:2151:0",
    "15:2151:1",
    "15:2157:1",
)
PREFILL_COMPANION_DONOR = {
    "15:2137:0": "15:2023:0",
    "15:2138:2": "15:2024:2",
    "15:2146:0": "15:2032:0",
    "15:2149:0": "15:2035:0",
    "15:2151:0": "15:2037:0",
    "15:2151:1": "15:2037:1",
    "15:2157:1": "15:2043:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2138:0",
)
EXACT_BASE_DONOR = {
    2137: (15, 2023),
    2146: (15, 2032),
    2149: (15, 2035),
    2151: (15, 2037),
    2157: (15, 2043),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in EXACT_BASE_DONOR
    },
    2138: ("15:2024:1", "15:2024:2"),
}
EXPECTED_BASE_RAW_MATCHES = {
    2137: (),
    2138: ((15, 2024), (15, 2108)),
    2146: ((15, 2032), (15, 2116)),
    2149: ((15, 2035), (15, 2119)),
    2151: ((15, 2037), (15, 2121)),
    2157: ((15, 2043), (15, 2127)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    2137: ((15, 2023), (15, 2107)),
    2138: ((15, 2024), (15, 2108)),
    2146: ((15, 2032), (15, 2116)),
    2149: ((15, 2035), (15, 2119)),
    2151: ((15, 2037), (15, 2121)),
    2157: ((15, 2043), (15, 2127)),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2137: ((466,), ("025032",)),
    2138: ((), ("025032",)),
    2146: ((), ()),
    2149: ((), ()),
    2151: ((), ("025032",)),
    2157: ((), ("026432",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1392,
    queue_start=67,
    queue_stop=134,
    slice_first="15:2126:1",
    slice_last="15:2159:0",
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
    source_call_roots=(466,),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2085, 2200)
    ),
    speaker_style=(
        (2137, "formal_war_preparation_recommendation"),
        (2138, "formal_war_support_authorization_request"),
        (2146, "formal_unavoidable_war_measure_authorization"),
        (2149, "formal_off_policy_measure_proposal"),
        (2151, "formal_unrelated_measure_authorization_request"),
        (2157, "formal_unrelated_siege_measure_authorization"),
    ),
    terminology_policy=(
        ("war preparation", "싸움에 대비"),
        ("recommendation", "건의"),
        ("execution", "실행, 시행"),
        ("authorization", "허락"),
        ("our clan", "우리 가문"),
        ("guideline", "지침"),
        ("advance measure", "추진"),
        ("siege", "공략"),
        ("dynamic object particle", "을(를)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B129 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; five complete "
        "records reuse approved completed Base Korean assemblies selected "
        "by raw, literal and operand-masked source identity with explicit "
        "exact donors; the source-identical authorization record uses its "
        "two populated completed Base rows as semantic context because its "
        "leading empty literal has no translatable Base decision row, while "
        "that hidden empty literal remains source-identical and participates "
        "in complete-record assembly; Base runtime and VM state are never "
        "inherited; war preparation, recommendations, execution, "
        "authorization, our clan, guidelines, advancing measures and sieges "
        "retain established historical project wording and formal advisory "
        "registers; calls, inline measure, force and target tokens, protected "
        "outer whitespace, line breaks, particles, ellipses, terminators, "
        "complete record arity, all sixty-one slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=6,
    pins={
        "expected_queue_universe_sha256": "F5127697934EECF67CA96B604FB9F3850C0D9CFECE475F6E739976A7AD94C82F",
        "expected_queue_slice_sha256": "D6C0EC552578B3F2E0565537174849C6FFB189FFC4D7BC373A8EF220199A149A",
        "expected_prefilled_coordinate_sha256": "854CDE6B319C7902CBA164C30C0BAB16A64661F5CAB24DA74F87E1C68DCA354B",
        "expected_prefill_slice_context_sha256": "1C8F53D5066909CAAB68787382C1759BD1FED7537F99073B3E062FABD6BCC74E",
        "expected_target_coordinate_sha256": "518CE5749CAA941463F6DC1A3F363583FA0209F2AC54E12CBDC5E30F0036F24B",
        "expected_source_target_sha256": "F76860F4D60132D391D4FCB22CC4D1659E72F3F3DA34CC95467FC417868C7B2A",
        "expected_current_target_sha256": "27FEACCC43C64BDCC42E9F92A5D8A21E4E3ED5E35D83A32811DE106BFCD52C1B",
        "expected_context_corpus_sha256": "E23067481BCC46DA87141359397BC4FB74DA070BE265688336D50FFA1A9E30B8",
        "expected_gap_contract_sha256": "DACB830EEDA7B943F28FAE7A87383594DE876126888CE46ECFA6EA74086DE80D",
        "expected_boundary_sha256": "5889FF84B96D8197F9EE2D3F57BE28DADAA714ED8339B5A854BA12174DB378C8",
        "expected_runtime_control_sha256": "6F92E169EF469C1F94E84B513697DC5BDCC7DFB9F493CEF28855CC3B2DD1878E",
        "expected_base_search_sha256": "B3CEB48E53A49EEA3E69201A05F346E04CC4A5C75C83C9FDC2F9EB44D628F502",
        "expected_complete_assembly_sha256": "C34FA817BFFB2347AA3B430D4DC29C988C161E4887994BD82809A845D71B46DF",
        "expected_call_graph_sha256": "60FDE594827B33F3EE975063BF1A375FDF52D7395CA43F000D557C0806EE2BBE",
        "expected_speaker_style_sha256": "B0E778B6F0233C961C970BB0BB16A81FAFB17181F80BDE833E51303578DDA4EC",
        "expected_terminology_policy_sha256": "0805440877909098E9166A5EB36239D6BD0379D59FDC101B49C2BD418EBB833C",
        "expected_translation_policy_sha256": "F6036D7E1DC199AA45272979D32A474C8F3AD342E289538488818A38F4D45466",
        "expected_candidate_sha256": "3B2860B3332F24491C8ED33ED3E7964FF3DFEE985C7CF2AC7D090493B168FCF3",
        "expected_combined_slice_candidate_sha256": "03DB92409808E1298BC18279CD39C4AE5CD9A557705D7A87576691BEB56C6725",
        "expected_combined_changed_literal_count": 61,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B129_S1392",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1392.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1391.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1393.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B129",
    "queue_row_count": 98,
    "queue_visible_count": 198,
    "queue_first": "15:2095:0",
    "queue_last": "15:2192:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
