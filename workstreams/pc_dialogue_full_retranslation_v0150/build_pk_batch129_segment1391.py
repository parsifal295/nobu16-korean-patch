#!/usr/bin/env python3
"""Build source-redacted PK B129 segment 1391 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    2095,
    2098,
    2101,
    2104,
    2107,
    2108,
    2109,
    2110,
    2111,
    2113,
    2116,
    2117,
    2118,
    2123,
)
TARGET_COORDINATES = (
    "15:2095:0",
    "15:2095:3",
    "15:2098:0",
    "15:2101:0",
    "15:2101:2",
    "15:2104:1",
    "15:2107:1",
    "15:2108:0",
    "15:2108:1",
    "15:2109:0",
    "15:2109:1",
    "15:2110:0",
    "15:2110:1",
    "15:2111:0",
    "15:2111:2",
    "15:2113:0",
    "15:2113:1",
    "15:2116:1",
    "15:2117:0",
    "15:2118:1",
    "15:2123:0",
    "15:2123:1",
)
TRANSLATIONS = {
    "15:2095:0": "자,",
    "15:2095:3": ".",
    "15:2098:0": "적은",
    "15:2101:0": "전시 중이나 건의",
    "15:2101:2": "을(를) 추진하고자 하오",
    "15:2104:1": "을(를) 건의",
    "15:2107:1": "을(를) 추진하고자 하오",
    "15:2108:0": "전장 밖에도 백성이 있사오니\n",
    "15:2108:1": "을(를) 건의",
    "15:2109:0": "전시 중이오나 양해해 주시오\n",
    "15:2109:1": "을(를) 추진하고자 하오",
    "15:2110:0": "전장 밖에도 백성이 있사오니\n",
    "15:2110:1": "을(를) 건의",
    "15:2111:0": "전시 중이나 건의",
    "15:2111:2": "을(를) 추진하고자 하오",
    "15:2113:0": "공략 준비를 위해\n",
    "15:2113:1": "의 실행을 건의",
    "15:2116:1": "을(를) 추진하고자 하옵니다",
    "15:2117:0": "이야말로\n",
    "15:2118:1": "을(를) 건의",
    "15:2123:0": "공략 준비를 위해\n",
    "15:2123:1": "의 실행을 건의",
}
EXPECTED_ARITY = {
    2095: 4,
    2098: 3,
    2101: 3,
    2104: 2,
    2107: 2,
    2108: 2,
    2109: 2,
    2110: 2,
    2111: 3,
    2113: 2,
    2116: 2,
    2117: 2,
    2118: 2,
    2123: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2095:1",
    "15:2095:2",
    "15:2098:1",
    "15:2098:2",
    "15:2104:0",
    "15:2107:0",
    "15:2116:0",
    "15:2117:1",
    "15:2118:0",
)
PREFILL_COMPANION_DONOR = {
    "15:2095:1": "15:2065:1",
    "15:2095:2": "15:2065:2",
    "15:2098:1": "15:2068:1",
    "15:2098:2": "15:2068:2",
    "15:2104:0": "15:1990:0",
    "15:2107:0": "15:1993:0",
    "15:2116:0": "15:2002:0",
    "15:2117:1": "15:2003:1",
    "15:2118:0": "15:2004:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2101:1",
    "15:2111:1",
)
EXACT_BASE_DONOR = {
    2095: (15, 2065),
    2098: (15, 2068),
    2104: (15, 2074),
    2107: (15, 2077),
    2108: (15, 2078),
    2109: (15, 2079),
    2110: (15, 2080),
    2113: (15, 2083),
    2116: (15, 2086),
    2117: (15, 2087),
    2118: (15, 2088),
    2123: (15, 2093),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in {2101, 2111}
    },
    2101: (
        "15:2071:0",
        "15:2071:2",
    ),
    2111: (
        "15:2081:0",
        "15:2081:2",
    ),
}
WARTIME_PROPOSAL_MATCHES = (
    (15, 1987),
    (15, 1997),
    (15, 2047),
    (15, 2057),
    (15, 2071),
    (15, 2081),
)
BATTLE_APOLOGY_MATCHES = (
    (15, 1990),
    (15, 2050),
    (15, 2074),
)
BATTLE_RELUCTANCE_MATCHES = (
    (15, 1993),
    (15, 2053),
    (15, 2077),
)
CIVILIAN_WELFARE_MATCHES = (
    (15, 1994),
    (15, 1996),
    (15, 2054),
    (15, 2056),
    (15, 2078),
    (15, 2080),
)
WARTIME_PARDON_MATCHES = (
    (15, 1995),
    (15, 2055),
    (15, 2079),
)
ATTACK_PREPARATION_MATCHES = (
    (15, 1999),
    (15, 2009),
    (15, 2083),
    (15, 2093),
)
EXPECTED_BASE_RAW_MATCHES = {
    2095: (),
    2098: ((15, 2068),),
    2101: WARTIME_PROPOSAL_MATCHES,
    2104: BATTLE_APOLOGY_MATCHES,
    2107: BATTLE_RELUCTANCE_MATCHES,
    2108: CIVILIAN_WELFARE_MATCHES,
    2109: WARTIME_PARDON_MATCHES,
    2110: CIVILIAN_WELFARE_MATCHES,
    2111: WARTIME_PROPOSAL_MATCHES,
    2113: (),
    2116: (
        (15, 2002),
        (15, 2086),
    ),
    2117: (
        (15, 2003),
        (15, 2087),
    ),
    2118: (
        (15, 2004),
        (15, 2088),
    ),
    2123: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    2095: ((15, 2065),),
    2113: ATTACK_PREPARATION_MATCHES,
    2123: ATTACK_PREPARATION_MATCHES,
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2095: ((1066,), ("025032",)),
    2098: ((), ("025032",)),
    2101: ((142,), ()),
    2104: ((142,), ()),
    2107: ((), ()),
    2108: ((142,), ()),
    2109: ((), ()),
    2110: ((142,), ()),
    2111: ((142,), ()),
    2113: ((466,), ("026432",)),
    2116: ((), ("026432",)),
    2117: ((), ("026432",)),
    2118: ((142,), ("026432",)),
    2123: ((466,), ("026432",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1391,
    queue_start=0,
    queue_stop=67,
    slice_first="15:2095:0",
    slice_last="15:2126:0",
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
        466,
        1066,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2085, 2127)
    ),
    speaker_style=(
        (2095, "seasoned_battlefield_scouting_counsel"),
        (2098, "formal_enemy_approach_counsel"),
        (2101, "wartime_formal_proposal"),
        (2104, "apologetic_wartime_counsel"),
        (2107, "apologetic_wartime_proposal"),
        (2108, "formal_civilian_welfare_counsel"),
        (2109, "deferential_wartime_proposal"),
        (2110, "formal_civilian_welfare_counsel"),
        (2111, "wartime_formal_proposal"),
        (2113, "strategic_attack_preparation_counsel"),
        (2116, "humble_attack_support_proposal"),
        (2117, "humble_best_course_assessment"),
        (2118, "formal_attack_preparation_counsel"),
        (2123, "strategic_attack_preparation_counsel"),
    ),
    terminology_policy=(
        ("enemy", "적"),
        ("observe", "상황을 살펴보다"),
        ("counsel", "건의"),
        ("advance proposal", "추진"),
        ("wartime", "전시"),
        ("battlefield", "전장"),
        ("common people", "백성"),
        ("battle", "싸움"),
        ("attack", "공략"),
        ("preparation", "준비"),
        ("best course", "최선책"),
        ("humble assessment", "사료되옵니다"),
        ("pardon request", "양해"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B129 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; twelve complete "
        "records reuse approved completed Base Korean assemblies selected "
        "by raw, literal and operand-masked source identity with explicit "
        "corresponding Base donors, while two wartime proposal records use "
        "their matching later-register Base assemblies through visible "
        "semantic references because their newline-only fragments have no "
        "promoted decision rows; Base runtime and VM state are never "
        "inherited; enemy, observation, counsel, proposal advancement, "
        "wartime, battlefield, common people, battle, attack, preparation, "
        "best-course assessment, pardon and each later speaker register "
        "retain established project and historical terminology; direct "
        "calls, inline faction and castle tokens, protected outer "
        "whitespace, newlines, gaps, literal arity, terminators, all nine "
        "same-record prefills, two hidden newlines, all forty-five slice "
        "prefills, complete assemblies, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "S1392 and S1393 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256": (
            "F5127697934EECF67CA96B604FB9F3850C0D9CFECE475F6E739976A7AD94C82F"
        ),
        "expected_queue_slice_sha256": (
            "C54261D53BA0122DEB2B8C6F3321535C44CC1AACD94AE7731B2A7096F45E9381"
        ),
        "expected_prefilled_coordinate_sha256": (
            "9BD7A622A0C375DB35563AD449357551C9475F46AABA100CB2F098EDEEFB1DA4"
        ),
        "expected_prefill_slice_context_sha256": (
            "1675EFA3B433F620C2A858DE9ED19F0E4BC2326B3BA49DA54450F1AD9B27E918"
        ),
        "expected_target_coordinate_sha256": (
            "E578A93558D3E101B5197AF72B6887C808FBB5A74AFEF09B540603E3629A769C"
        ),
        "expected_source_target_sha256": (
            "3BD0BE45B1A7DF88650E5FBBED38F771B565A2859662CE63D7901BBA90BC3B4B"
        ),
        "expected_current_target_sha256": (
            "D5BFB2E2BAE8AF7734C4EC74E0C60F9727AB030A01D3EED2F07C67C184650CFD"
        ),
        "expected_context_corpus_sha256": (
            "E23067481BCC46DA87141359397BC4FB74DA070BE265688336D50FFA1A9E30B8"
        ),
        "expected_gap_contract_sha256": (
            "7B64EC8C293FC3DD56193511F5925013C32B88CC551336521DBBEE8BEE04399D"
        ),
        "expected_boundary_sha256": (
            "A2556D40A69E3FADA850965C572185C0137EC092F82A6F086230404793B5842C"
        ),
        "expected_runtime_control_sha256": (
            "082F67E36412E0E7B8B8A91675098D0E796CF604EB06673F7E9928AD9DB60BB2"
        ),
        "expected_base_search_sha256": (
            "4F289D101385BE7B15630E9FBFB66854E2C02924A49DA72736FA1A22C3BD36FE"
        ),
        "expected_complete_assembly_sha256": (
            "658037184DDDB3841A9BD2641899960F76BF10B74003FBA3A8D13B27C382E34C"
        ),
        "expected_call_graph_sha256": (
            "D2B7131DB7F483787F005167CB64E6CEF9FE842A99DDB549B0A199975C3F7A05"
        ),
        "expected_speaker_style_sha256": (
            "9ADFB810A65BB688FC3759EFD958D855286A9ABB6657ABE0C8E31890ACAF7E01"
        ),
        "expected_terminology_policy_sha256": (
            "793718840CD9BB9D3829BC745745CEC60842CB815C4DB3EB33E12DB975417B46"
        ),
        "expected_translation_policy_sha256": (
            "8B66C8B49D09E3DEA9D1D358D072AA66BD6D5359996FB26E9960F08E4000138E"
        ),
        "expected_candidate_sha256": (
            "6940637B0666544A43FA0024D7C542A776DA1236BC53BAA27E1BAFED0EF2775D"
        ),
        "expected_combined_slice_candidate_sha256": (
            "C9A4655D1E4EBC5DAFEE0FC1B62AF07D274D3040BC052E943FA99EFE1DCFF15A"
        ),
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B129_S1391",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1391.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B129_S1392.private.v1.jsonl",
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
