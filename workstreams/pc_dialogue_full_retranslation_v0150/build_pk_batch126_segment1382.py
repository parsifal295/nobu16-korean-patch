#!/usr/bin/env python3
"""Build source-redacted PK B126 segment 1382 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1828:1",
    "15:1833:0",
    "15:1833:1",
    "15:1834:0",
    "15:1835:2",
    "15:1837:0",
    "15:1837:1",
    "15:1837:2",
    "15:1838:2",
    "15:1838:3",
    "15:1842:0",
    "15:1842:1",
    "15:1843:1",
    "15:1844:0",
    "15:1845:0",
    "15:1846:0",
    "15:1847:1",
    "15:1848:1",
    "15:1848:2",
    "15:1848:3",
)
TRANSLATIONS = {
    "15:1828:1": "보고할 사항은",
    "15:1833:0": "우리 가문은",
    "15:1833:1": "의",
    "15:1834:0": "의",
    "15:1835:2": "의",
    "15:1837:0": "우리는",
    "15:1837:1": "의",
    "15:1837:2": "와(과)\n",
    "15:1838:2": "의",
    "15:1838:3": "와(과)의\n",
    "15:1842:0": "우리 가문은",
    "15:1842:1": "의",
    "15:1843:1": "의",
    "15:1844:0": "그",
    "15:1845:0": "그",
    "15:1846:0": "그",
    "15:1847:1": "의",
    "15:1848:1": "의",
    "15:1848:2": "와(과),",
    "15:1848:3": "의",
}
TARGET_RECORD_IDS = (
    1828,
    1833,
    1834,
    1835,
    1837,
    1838,
    1842,
    1843,
    1844,
    1845,
    1846,
    1847,
    1848,
)
EXPECTED_ARITY = {
    1828: 2,
    1833: 4,
    1834: 3,
    1835: 4,
    1837: 4,
    1838: 5,
    1842: 3,
    1843: 3,
    1844: 3,
    1845: 2,
    1846: 2,
    1847: 3,
    1848: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1828:0",
    "15:1833:2",
    "15:1833:3",
    "15:1834:1",
    "15:1834:2",
    "15:1835:0",
    "15:1835:1",
    "15:1835:3",
    "15:1837:3",
    "15:1838:0",
    "15:1838:1",
    "15:1838:4",
    "15:1842:2",
    "15:1843:0",
    "15:1843:2",
    "15:1844:1",
    "15:1844:2",
    "15:1845:1",
    "15:1846:1",
    "15:1847:0",
    "15:1847:2",
    "15:1848:0",
    "15:1848:4",
)
PREFILL_COMPANION_DONOR = {
    "15:1828:0": "15:1798:0",
    "15:1833:2": "15:1803:2",
    "15:1833:3": "15:1803:3",
    "15:1834:1": "15:1804:1",
    "15:1834:2": "15:1804:2",
    "15:1835:0": "15:1805:0",
    "15:1835:1": "15:1805:1",
    "15:1835:3": "15:1805:3",
    "15:1837:3": "15:1807:3",
    "15:1838:0": "15:1808:0",
    "15:1838:1": "15:1808:1",
    "15:1838:4": "15:1808:4",
    "15:1842:2": "15:1812:2",
    "15:1843:0": "15:1813:0",
    "15:1843:2": "15:1813:2",
    "15:1844:1": "15:1814:1",
    "15:1844:2": "15:1814:2",
    "15:1845:1": "15:1815:1",
    "15:1846:1": "15:1816:1",
    "15:1847:0": "15:1817:0",
    "15:1847:2": "15:1817:2",
    "15:1848:0": "15:1818:0",
    "15:1848:4": "15:1818:4",
}
EXACT_BASE_DONOR = {
    1828: (15, 1798),
    1833: (15, 1803),
    1834: (15, 1804),
    1835: (15, 1805),
    1837: (15, 1807),
    1838: (15, 1808),
    1842: (15, 1812),
    1843: (15, 1813),
    1844: (15, 1814),
    1845: (15, 1815),
    1846: (15, 1816),
    1847: (15, 1817),
    1848: (15, 1818),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    1837: ((15, 1807),),
    1845: ((15, 1815),),
    1847: ((15, 1817),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: ((15, EXACT_BASE_DONOR[record_id][1]),)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1828: ((1174, 742), ()),
    1833: ((178, 748), ("023C", "025132")),
    1834: ((178, 424), ("023C", "025132")),
    1835: ((178, 1066), ("023C", "025132")),
    1837: ((178,), ("023C", "025132", "023D")),
    1838: ((82, 610), ("023C", "025132", "023D")),
    1842: ((568,), ("023C", "025132")),
    1843: ((1066,), ("023C", "025132")),
    1844: ((742, 550), ("025132",)),
    1845: ((226,), ("025132",)),
    1846: ((1066,), ("025132",)),
    1847: ((226,), ("023C", "025132")),
    1848: ((610,), ("023C", "025132", "023D", "025232")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1382,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1823:0",
    slice_last="15:1854:0",
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
        1174,
        742,
        178,
        748,
        424,
        1066,
        82,
        610,
        568,
        550,
        226,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1788, 1861)
    ),
    speaker_style=(
        (1828, "formal_no_current_report"),
        (1833, "formal_vassalage_diplomacy_assessment"),
        (1834, "formal_subordinate_reinforcement_assessment"),
        (1835, "formal_multiple_subordinates_assessment"),
        (1837, "system_alliance_status"),
        (1838, "formal_multiple_alliances_assessment"),
        (1842, "formal_hostile_relations_war_warning"),
        (1843, "formal_multiple_enemies_crisis_warning"),
        (1844, "formal_weaker_enemy_caution"),
        (1845, "formal_enemy_intentions_caution"),
        (1846, "formal_stronger_enemy_caution"),
        (1847, "formal_diplomatic_improvement_advice"),
        (1848, "formal_multiple_relationships_advice"),
    ),
    terminology_policy=(
        ("our clan", "우리 가문"),
        ("vassalage", "종속"),
        ("alliance", "동맹"),
        ("reinforcements", "원군"),
        ("force", "세력"),
        ("war", "전쟁"),
        ("enemy", "적"),
        ("territory", "영토"),
        ("diplomacy", "외교"),
        ("dynamic conjunction", "와(과)"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B126 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all thirteen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity with "
        "explicit exact donors; Base runtime and VM state are never "
        "inherited; our clan, vassalage, alliances, reinforcements, forces, "
        "war, enemies, territory and diplomacy retain established historical "
        "project wording and formal advisory, warning or system registers; "
        "calls, inline house, force, relation and duration tokens, protected "
        "outer whitespace, line breaks, conjunctions, ellipses, terminators, "
        "complete record arity, all forty-seven slice prefills, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, outside-"
        "scope identity, optional neighbor decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=6,
    pins={
        "expected_queue_universe_sha256": (
            "FB8F40DA25868E77D6819B3B054CFA5D1866D279CBC04B058E9F750371FD010D"
        ),
        "expected_queue_slice_sha256": (
            "1A1F37187F51AEEBEB96D1804F00570A360D2B317B7AED00220FF1AE3AF1AF01"
        ),
        "expected_prefilled_coordinate_sha256": (
            "628F11F0BFE29913980744DD09695A0327FFF9F5576DD9247AD159F23900E94C"
        ),
        "expected_prefill_slice_context_sha256": (
            "1B59F2ED766CB0B6E98084DB1DCE630C1B9B4629D4776C416F13B1A508202CEB"
        ),
        "expected_target_coordinate_sha256": (
            "D9EC77607588319F8B600CF28CEC375C3FB6BE6C99A1B5A3C3F7BF3D29972A5A"
        ),
        "expected_source_target_sha256": (
            "23E87A3C4B24A0A679C82E335E294A07FFCD9C8333225E61F31EDAA9E7822354"
        ),
        "expected_current_target_sha256": (
            "77FF11650C51EFF3911E13EBB6E721B2D7B396CE2D3CA9F017C070CD82F2E00B"
        ),
        "expected_context_corpus_sha256": (
            "29E672CE13BE217812D12239F072FB502613E5A08DC9C3E0BAE2115330665E76"
        ),
        "expected_gap_contract_sha256": (
            "A2115562984263FE78980AB2B92C2329D6DA48719ECA913162ACF3A62FF91CDA"
        ),
        "expected_boundary_sha256": (
            "06C8BD7559A9280FB6475630936D93E7747D8C61424741B7116D0F970C744875"
        ),
        "expected_runtime_control_sha256": (
            "59D388E85D3464116312D4BCA9CCFA4AF927CB3FFA859AB6C15A1DA573B4A3A8"
        ),
        "expected_base_search_sha256": (
            "1119B0F17B072401ECE7168526E561002F892AD43C1FFADA0626F4FBB3A7CB3D"
        ),
        "expected_complete_assembly_sha256": (
            "6C5B1442D415CF85DA2D05A95DFFC8D1D0AF0343215F7B389741F2C730604C8E"
        ),
        "expected_call_graph_sha256": (
            "AE7E97F0CB5CCCD9B0416F08A870A282A4872682FF29B92B211F1C8CEBD0BDAC"
        ),
        "expected_speaker_style_sha256": (
            "39FA1F0F50CB4DC4240474214C2AB784FFAFB01C0C28BF4C0F6B6A8358CF88C8"
        ),
        "expected_terminology_policy_sha256": (
            "D4D3ED6C4D0CC741D0BF298943A697FE382392245E6B4FE4D5FA06423F1551CD"
        ),
        "expected_translation_policy_sha256": (
            "1F8BC1BD2A8DA03797883F42F8B7B7BF781B32C11586197015B370849A9834C2"
        ),
        "expected_candidate_sha256": (
            "A6BA5B0492DD8DDDF98BBE5C30E1BE17BDB12FC67C247C632CD5479A9A72F6E4"
        ),
        "expected_combined_slice_candidate_sha256": (
            "2E430A3FF51E069514EE5F08FDAD28938DA099CCBEB76CCD19B84FB8C00078B5"
        ),
        "expected_combined_changed_literal_count": 52,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B126_S1382",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1382.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B126_S1383.private.v1.jsonl",
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
