#!/usr/bin/env python3
"""Build source-redacted PK B128 segment 1390 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2067:2",
    "15:2073:0",
    "15:2077:0",
    "15:2077:2",
    "15:2080:1",
    "15:2083:1",
    "15:2084:0",
    "15:2084:1",
    "15:2085:0",
    "15:2085:1",
    "15:2086:0",
    "15:2086:1",
    "15:2087:0",
    "15:2087:2",
    "15:2088:0",
    "15:2088:2",
    "15:2088:3",
    "15:2090:0",
    "15:2090:3",
    "15:2091:2",
    "15:2093:2",
    "15:2094:3",
)
TRANSLATIONS = {
    "15:2067:2": "의 시행을 허락해 주시기를 청하옵니다",
    "15:2073:0": "의 시행을 허락해 주시기를 바라오\n",
    "15:2077:0": "전시 중이나 건의",
    "15:2077:2": "을(를) 추진하고자 하오",
    "15:2080:1": "을(를) 건의",
    "15:2083:1": "을(를) 추진하고자 하오",
    "15:2084:0": "전장 밖에도 백성이 있사오니\n",
    "15:2084:1": "을(를) 건의",
    "15:2085:0": "전시 중이오나 양해해 주시오\n",
    "15:2085:1": "을(를) 추진하고자 하오",
    "15:2086:0": "전장 밖에도 백성이 있사오니\n",
    "15:2086:1": "을(를) 건의",
    "15:2087:0": "전시 중이나 건의",
    "15:2087:2": "을(를) 추진하고자 하오",
    "15:2088:0": "적은",
    "15:2088:2": "이라도 시행",
    "15:2088:3": "?",
    "15:2090:0": "적은",
    "15:2090:3": "?",
    "15:2091:2": "을(를) 시행할까……",
    "15:2093:2": "(이)라도……",
    "15:2094:3": ".",
}
TARGET_RECORD_IDS = (
    2067,
    2073,
    2077,
    2080,
    2083,
    2084,
    2085,
    2086,
    2087,
    2088,
    2090,
    2091,
    2093,
    2094,
)
EXPECTED_ARITY = {
    2067: 3,
    2073: 2,
    2077: 3,
    2080: 2,
    2083: 2,
    2084: 2,
    2085: 2,
    2086: 2,
    2087: 3,
    2088: 4,
    2090: 4,
    2091: 3,
    2093: 3,
    2094: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2067:0",
    "15:2067:1",
    "15:2073:1",
    "15:2080:0",
    "15:2083:0",
    "15:2088:1",
    "15:2090:1",
    "15:2090:2",
    "15:2091:0",
    "15:2091:1",
    "15:2093:0",
    "15:2093:1",
    "15:2094:0",
    "15:2094:1",
    "15:2094:2",
)
PREFILL_COMPANION_DONOR = {
    "15:2067:0": "15:2037:0",
    "15:2067:1": "15:2037:1",
    "15:2073:1": "15:2043:1",
    "15:2080:0": "15:1990:0",
    "15:2083:0": "15:1993:0",
    "15:2088:1": "15:2058:1",
    "15:2090:1": "15:2060:1",
    "15:2090:2": "15:2060:2",
    "15:2091:0": "15:2061:0",
    "15:2091:1": "15:2061:1",
    "15:2093:0": "15:2063:0",
    "15:2093:1": "15:2063:1",
    "15:2094:0": "15:2064:0",
    "15:2094:1": "15:2064:1",
    "15:2094:2": "15:2064:2",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2077:1",
    "15:2087:1",
)
EXACT_BASE_DONOR = {
    2067: (15, 2037),
    2073: (15, 2043),
    2080: (15, 1990),
    2083: (15, 1993),
    2084: (15, 2054),
    2085: (15, 2055),
    2086: (15, 2056),
    2088: (15, 2058),
    2090: (15, 2060),
    2091: (15, 2061),
    2093: (15, 2063),
    2094: (15, 2064),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in {2077, 2087}
    },
    2077: (
        "15:2047:0",
        "15:2047:2",
    ),
    2087: (
        "15:2057:0",
        "15:2057:2",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    2067: ((15, 2037), (15, 2121)),
    2073: ((15, 2043), (15, 2127)),
    2077: (
        (15, 1987),
        (15, 1997),
        (15, 2047),
        (15, 2057),
        (15, 2071),
        (15, 2081),
    ),
    2080: ((15, 1990), (15, 2050), (15, 2074)),
    2083: ((15, 1993), (15, 2053), (15, 2077)),
    2084: (
        (15, 1994),
        (15, 1996),
        (15, 2054),
        (15, 2056),
        (15, 2078),
        (15, 2080),
    ),
    2085: ((15, 1995), (15, 2055), (15, 2079)),
    2086: (
        (15, 1994),
        (15, 1996),
        (15, 2054),
        (15, 2056),
        (15, 2078),
        (15, 2080),
    ),
    2087: (
        (15, 1987),
        (15, 1997),
        (15, 2047),
        (15, 2057),
        (15, 2071),
        (15, 2081),
    ),
    2088: (),
    2090: (),
    2091: (),
    2093: (),
    2094: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{
        record_id: matches
        for record_id, matches in EXPECTED_BASE_RAW_MATCHES.items()
        if matches
    },
    2088: ((15, 2058),),
    2090: ((15, 2060),),
    2091: ((15, 2061),),
    2093: ((15, 2063),),
    2094: ((15, 2064),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2067: ((), ("025032",)),
    2073: ((), ("026432",)),
    2077: ((142,), ()),
    2080: ((142,), ()),
    2083: ((), ()),
    2084: ((142,), ()),
    2085: ((), ()),
    2086: ((142,), ()),
    2087: ((142,), ()),
    2088: ((466,), ("025032",)),
    2090: ((1096,), ("025032",)),
    2091: ((898,), ("025032",)),
    2093: ((598,), ("025032",)),
    2094: ((160, 1096), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1390,
    queue_start=134,
    queue_stop=199,
    slice_first="15:2067:0",
    slice_last="15:2094:3",
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
    source_call_roots=(
        142,
        160,
        466,
        598,
        898,
        1096,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1990, 2095)
    ),
    speaker_style=(
        (2067, "humble_unrelated_attack_permission_petition"),
        (2073, "formal_unrelated_siege_permission_petition"),
        (2077, "formal_wartime_proposal"),
        (2080, "formal_battle_interruption_proposal"),
        (2083, "apologetic_battle_progress_proposal"),
        (2084, "archaic_civilian_welfare_proposal"),
        (2085, "formal_wartime_pardon_proposal"),
        (2086, "archaic_civilian_welfare_proposal"),
        (2087, "formal_wartime_proposal"),
        (2088, "strategic_targetless_policy_deliberation"),
        (2090, "strategic_targetless_policy_test_proposal"),
        (2091, "formal_attack_target_priority_proposal"),
        (2093, "casual_target_selection_deliberation"),
        (2094, "casual_targetless_policy_test_proposal"),
    ),
    terminology_policy=(
        ("guideline", "지침"),
        ("attack", "공격"),
        ("siege", "공략"),
        ("petition", "건의"),
        ("carry forward", "추진"),
        ("wartime", "전시"),
        ("battlefield", "전장"),
        ("commoners", "백성"),
        ("controlled castle", "성"),
        ("attack target", "공략 목표"),
        ("execute policy", "시행"),
        ("request permission", "허락해 주시기를 청하옵니다"),
        ("project ellipsis", "……"),
        ("particle compatibility", "을(를)\u00b7(이)가"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B128 queue ordinals one hundred "
        "thirty-four through one hundred ninety-eight and the approved Base "
        "prefill; pristine PK JP is authoritative and every populated EN, "
        "SC and TC same-record fragment array was reviewed as auxiliary "
        "context; twelve complete records reuse approved completed Base "
        "Korean assemblies selected by raw, literal and operand-masked "
        "source identity with explicit exact donors, preferring the "
        "corresponding record thirty positions earlier when duplicate "
        "source assemblies exist, while two wartime-proposal records reuse "
        "the matching Base visible assembly through semantic references "
        "because each newline-only fragment has no promoted decision row; "
        "Base runtime and VM state are never inherited; guidelines, "
        "attacks, sieges, petitions, wartime, battlefields, commoners, "
        "castles, attack targets and policy execution retain established "
        "historical project wording and each formal, humble, archaic or "
        "casual speaker register; direct calls, inline force and policy "
        "tokens, colour tags, protected outer whitespace, newlines, gaps, "
        "literal arity, particles, ellipses, terminators, all fifteen "
        "same-record prefills, two hidden newlines, all forty-three slice "
        "prefills, complete assemblies, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, reciprocal "
        "S1388 and S1389 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=20,
    pins={
        "expected_queue_universe_sha256": (
            "354A482D4069DE0E482F6258A08E16B37D2368C0DA8D1ADA17C9CC39FEC679B9"
        ),
        "expected_queue_slice_sha256": (
            "D6094E426C08277D4AC813E3AB68CCF84EE42C447CB21CA5CF54C0C41439A198"
        ),
        "expected_prefilled_coordinate_sha256": (
            "C017CF75F6E29C427F8C3E1BD88C847417A9728269DA520ADE8AC4D52F070A25"
        ),
        "expected_prefill_slice_context_sha256": (
            "4F4CEE3F961B1DA30263DCB98B2053A6D738B3C3F160659E845E6EE7BC7C30B8"
        ),
        "expected_target_coordinate_sha256": (
            "0DF88143BB4DAAA59943B0D164152FE940A31E0DFBC2CBD74081A390E05F5712"
        ),
        "expected_source_target_sha256": (
            "47E9D9F2F3CF528E603BAB685B5553051BB89294A51E527E574FE638384E0A64"
        ),
        "expected_current_target_sha256": (
            "139023496E92050AB87970E29C57B5E9805B3157920814D97BB89CB90EAE787D"
        ),
        "expected_context_corpus_sha256": (
            "4E20716A3F245BABD767D962C2E7918428FC6142F0379F24CAC0F8815B0D9851"
        ),
        "expected_gap_contract_sha256": (
            "31AA7F77AF450B66F513FD2A0FE839939175897AC4E43D2C4E0CBC94E653659B"
        ),
        "expected_boundary_sha256": (
            "585F38010B8D2ACC76E125B7337D93C5612E4560D83AE4072D7F93D26C7D816F"
        ),
        "expected_runtime_control_sha256": (
            "2978158979BF953BA11ABDC9DF820408B96A286B67F8C2DCF93FE3783244E1EB"
        ),
        "expected_base_search_sha256": (
            "4140E37F9385AB686BA65729FA70A8F6D702BF4645F82C466E66D77D50177097"
        ),
        "expected_complete_assembly_sha256": (
            "B953B6EF6E20C888E4B5E5DA3E74A09AD49F3D764957F878FEED66543562CDAD"
        ),
        "expected_call_graph_sha256": (
            "C3594D056E7A98CBBCD179A163DB034D859E11EE89FD8E71B0D1CDDC16F6A189"
        ),
        "expected_speaker_style_sha256": (
            "5D6BDF98B1ED9C54B15C09B1FBC25CEA09C530A0B3BFE9240467D87766632763"
        ),
        "expected_terminology_policy_sha256": (
            "33DBE1A9483FC0F86D24AE223677142A5922733AF9250FCC80C441211F851422"
        ),
        "expected_translation_policy_sha256": (
            "F93D56046DCF97B77B4C9393C646E8E974A90D0118CCC5520CE4E414CC1DD283"
        ),
        "expected_candidate_sha256": (
            "34B58E5BFEE3CD658363730BBEB62D18C8504D65E52A606F802E9293D1D723B0"
        ),
        "expected_combined_slice_candidate_sha256": (
            "CC4B90D991A10FAC91F1D318BB2C0B23AF80D675FBF2BCDC907376B2E7347129"
        ),
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B128_S1390",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1390.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1388.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1389.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B128",
    "queue_row_count": 96,
    "queue_visible_count": 199,
    "queue_first": "15:1999:0",
    "queue_last": "15:2094:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
