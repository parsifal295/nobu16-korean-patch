#!/usr/bin/env python3
"""Build source-redacted PK B126 segment 1383 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1854:1",
    "15:1855:1",
    "15:1858:1",
    "15:1859:1",
    "15:1861:2",
    "15:1868:0",
    "15:1869:1",
    "15:1870:1",
    "15:1875:1",
    "15:1876:1",
    "15:1886:2",
    "15:1887:1",
)
TRANSLATIONS = {
    "15:1854:1": "을(를) 추천",
    "15:1855:1": "\n지금,",
    "15:1858:1": "의",
    "15:1859:1": "의",
    "15:1861:2": "늘 경계해야 합니다",
    "15:1868:0": "의",
    "15:1869:1": "의",
    "15:1870:1": ", 경계해야 할 상대",
    "15:1875:1": "만\n",
    "15:1876:1": "의",
    "15:1886:2": "……",
    "15:1887:1": "만,\n",
}
TARGET_RECORD_IDS = (
    1854,
    1855,
    1858,
    1859,
    1861,
    1868,
    1869,
    1870,
    1875,
    1876,
    1886,
    1887,
)
EXPECTED_ARITY = {
    1854: 3,
    1855: 3,
    1858: 3,
    1859: 3,
    1861: 3,
    1868: 2,
    1869: 3,
    1870: 2,
    1875: 3,
    1876: 3,
    1886: 3,
    1887: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1854:0",
    "15:1854:2",
    "15:1855:0",
    "15:1855:2",
    "15:1858:0",
    "15:1858:2",
    "15:1859:0",
    "15:1859:2",
    "15:1861:0",
    "15:1861:1",
    "15:1868:1",
    "15:1869:0",
    "15:1869:2",
    "15:1870:0",
    "15:1875:0",
    "15:1875:2",
    "15:1876:0",
    "15:1876:2",
    "15:1886:0",
    "15:1886:1",
    "15:1887:0",
    "15:1887:2",
)
PREFILL_COMPANION_DONOR = {
    "15:1854:0": "15:1824:0",
    "15:1854:2": "15:1824:2",
    "15:1855:0": "15:1825:0",
    "15:1855:2": "15:1825:2",
    "15:1858:0": "15:1828:0",
    "15:1858:2": "15:1828:2",
    "15:1859:0": "15:1828:0",
    "15:1859:2": "15:1829:2",
    "15:1861:0": "15:1831:0",
    "15:1861:1": "15:1831:1",
    "15:1868:1": "15:1838:1",
    "15:1869:0": "15:1839:0",
    "15:1869:2": "15:1839:2",
    "15:1870:0": "15:1840:0",
    "15:1875:0": "15:1845:0",
    "15:1875:2": "15:1845:2",
    "15:1876:0": "15:1846:0",
    "15:1876:2": "15:1846:2",
    "15:1886:0": "15:1856:0",
    "15:1886:1": "15:1856:1",
    "15:1887:0": "15:1857:0",
    "15:1887:2": "15:1857:2",
}
EXACT_BASE_DONOR = {
    1854: (15, 1824),
    1855: (15, 1825),
    1858: (15, 1828),
    1859: (15, 1829),
    1861: (15, 1831),
    1868: (15, 1838),
    1869: (15, 1839),
    1870: (15, 1840),
    1875: (15, 1845),
    1876: (15, 1846),
    1886: (15, 1856),
    1887: (15, 1857),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    1854: (),
    1855: ((15, 1825),),
    1858: ((15, 1828),),
    1859: ((15, 1829),),
    1861: (),
    1868: ((15, 1838),),
    1869: (),
    1870: (),
    1875: (),
    1876: ((15, 1846),),
    1886: (),
    1887: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1854: ((1096, 226), ("026432",)),
    1855: ((178, 286), ("026432",)),
    1858: ((178,), ("023C", "025132")),
    1859: ((178,), ("023C", "025132")),
    1861: ((1066, 1174), ()),
    1868: ((), ("023C", "025132")),
    1869: ((1066,), ("023C", "025132")),
    1870: ((748, 568), ("025132",)),
    1875: ((160, 808), ("025132", "024933")),
    1876: ((226,), ("023C", "025132")),
    1886: ((562,), ("024933",)),
    1887: ((160, 1090), ("024933",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1383,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1854:1",
    slice_last="15:1891:0",
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
        1096,
        226,
        178,
        286,
        1066,
        1174,
        748,
        568,
        160,
        808,
        562,
        1090,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1818, 1920)
    ),
    speaker_style=(
        (1854, "formal_target_recommendation"),
        (1855, "formal_invasion_opportunity_assessment"),
        (1858, "formal_active_war_status"),
        (1859, "formal_multiple_wars_status"),
        (1861, "formal_invasion_progress_caution"),
        (1868, "formal_enemy_castle_threat_warning"),
        (1869, "formal_multiple_enemy_threat_warning"),
        (1870, "formal_smaller_enemy_caution"),
        (1875, "formal_enemy_commanders_caution"),
        (1876, "formal_territorial_expansion_target_advice"),
        (1886, "formal_famous_commander_caution"),
        (1887, "formal_enemy_commander_movements_caution"),
    ),
    terminology_policy=(
        ("target", "목표"),
        ("military preparedness", "군비"),
        ("chance of victory", "승산"),
        ("our clan", "우리 가문"),
        ("engagement", "교전"),
        ("invasion", "침공"),
        ("force", "세력"),
        ("castle", "성"),
        ("territory", "영토"),
        ("renowned commander", "명장"),
        ("main-force commanders", "주력 장수"),
        ("vigilance", "경계"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B126 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all twelve "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity with "
        "explicit exact donors; Base runtime and VM state are never "
        "inherited; targets, military preparedness, chances of victory, our "
        "clan, engagements, invasions, forces, castles, territory, renowned "
        "commanders, main-force commanders and vigilance retain established "
        "historical project wording and formal advisory, warning or status "
        "registers; calls, inline house, force, person and target tokens, "
        "protected outer whitespace, line breaks, particles, ellipses, "
        "terminators, complete record arity, the left split record at 1854, "
        "all fifty-five slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=6,
    pins={
        "expected_queue_universe_sha256": (
            "FB8F40DA25868E77D6819B3B054CFA5D1866D279CBC04B058E9F750371FD010D"
        ),
        "expected_queue_slice_sha256": (
            "6A68268B2AAD7C07463F78DDB6ED1E85FB9F266BBB921661881298BF8B013319"
        ),
        "expected_prefilled_coordinate_sha256": (
            "DB65BF8F30FE9172E8A6B4446BFB04765F283B34032653C5F712ABAC1DDBD1C7"
        ),
        "expected_prefill_slice_context_sha256": (
            "FAE3EF62606FAAEF7B2260FA52EB97D98F7B31C49D3F507C4791B792EED1FE8F"
        ),
        "expected_target_coordinate_sha256": (
            "398F0DC8B2F2881EB7C42B4887BBE598C2F3815B952BACB8057E51B678F1A573"
        ),
        "expected_source_target_sha256": (
            "C83635F1D1FBC685D014F83CC87C08146FE2D663A5AF53C688FAD3871DAF3D2B"
        ),
        "expected_current_target_sha256": (
            "2521D5F5A00AFD49B4DBC465F37600B18E44965D19C394717C3D60305F594EB7"
        ),
        "expected_context_corpus_sha256": (
            "29E672CE13BE217812D12239F072FB502613E5A08DC9C3E0BAE2115330665E76"
        ),
        "expected_gap_contract_sha256": (
            "0F89EB2276E69AFABEE5F902E7D31BC48E9ADCA62EC8C84B8C0AF930AE6F4A7C"
        ),
        "expected_boundary_sha256": (
            "284055CFE85FC886D91DB32EDF5A2AFC688648A60A61DD66A229363FE2E3E750"
        ),
        "expected_runtime_control_sha256": (
            "BEABDAFD0F0926BDA717AEA6B67B82E7397979A8D59289C920B0FE4A2D8FE05A"
        ),
        "expected_base_search_sha256": (
            "5446C53D9CF0225BDC97F0219397DC563DDB2BB2802850E581526300EF2D3A16"
        ),
        "expected_complete_assembly_sha256": (
            "C7DA2F3AC1016B4B901C8FC04C4E4258C02F905ECE7D5C576AFB4FC272349A3D"
        ),
        "expected_call_graph_sha256": (
            "8ABD63AD9C4BD76B074894C71C92B75FA8E006396BC1710320C4B31B9C11868B"
        ),
        "expected_speaker_style_sha256": (
            "0922C27B8E8A6556F456B97410833E6737FC9B859D827D735CB32F5233B32A60"
        ),
        "expected_terminology_policy_sha256": (
            "D23094729D3D7C3C9CA32EF7CA5496C8E46E14AAA30939A22EF3A41112E0DD1D"
        ),
        "expected_translation_policy_sha256": (
            "3CA9AFBD148FEAC40B9770C639E38B994050575CD7F5160A496A5D0E1395BB33"
        ),
        "expected_candidate_sha256": (
            "0B9CCCF7BEF88108C66EC7F1FC809722E342A4B4512398D94183B651E5E1DFF4"
        ),
        "expected_combined_slice_candidate_sha256": (
            "D451FE4FCC605F8F15935B0EAF7DF6E6FB6E02F6106A9B7D345337CB6E14ED4A"
        ),
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B126_S1383",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1383.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1382.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1384.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B126",
    "queue_row_count": 102,
    "queue_visible_count": 200,
    "queue_first": "15:1823:0",
    "queue_last": "15:1927:2",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
