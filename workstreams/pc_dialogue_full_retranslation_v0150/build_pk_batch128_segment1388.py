#!/usr/bin/env python3
"""Build source-redacted PK B128 segment 1388 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1999,
    2001,
    2002,
    2003,
    2006,
    2007,
    2009,
    2010,
    2015,
    2017,
    2020,
    2023,
    2024,
    2025,
    2026,
    2027,
    2029,
    2032,
    2033,
)
TARGET_COORDINATES = (
    "15:1999:0",
    "15:2001:1",
    "15:2002:0",
    "15:2003:1",
    "15:2006:0",
    "15:2007:0",
    "15:2009:1",
    "15:2010:0",
    "15:2015:0",
    "15:2017:0",
    "15:2017:2",
    "15:2020:1",
    "15:2023:1",
    "15:2024:0",
    "15:2024:1",
    "15:2025:0",
    "15:2025:1",
    "15:2026:0",
    "15:2026:1",
    "15:2027:0",
    "15:2027:2",
    "15:2029:0",
    "15:2029:1",
    "15:2032:1",
    "15:2033:0",
)
TRANSLATIONS = {
    "15:1999:0": "이때는",
    "15:2001:1": "?",
    "15:2002:0": "을(를) 시행하",
    "15:2003:1": "을(를) 건의",
    "15:2006:0": "이때는",
    "15:2007:0": "지금은",
    "15:2009:1": "만\n",
    "15:2010:0": "지금은",
    "15:2015:0": "이때는",
    "15:2017:0": "전시이지만 건의",
    "15:2017:2": "을(를) 추진하고자 하오",
    "15:2020:1": "을(를) 건의",
    "15:2023:1": "을(를) 추진하고자 하오",
    "15:2024:0": "전장 밖에도 백성이 살아가고 있으니\n",
    "15:2024:1": "을(를) 건의",
    "15:2025:0": "전시이지만 양해해 주시오\n",
    "15:2025:1": "을(를) 추진하고자 하오",
    "15:2026:0": "전장 밖에도 백성이 살아가고 있으니\n",
    "15:2026:1": "을(를) 건의",
    "15:2027:0": "전시이지만 건의",
    "15:2027:2": "을(를) 추진하고자 하오",
    "15:2029:0": "을(를) 공략할 준비를 위해\n",
    "15:2029:1": "의 시행을 건의",
    "15:2032:1": "을(를) 추진하고자 하옵니다",
    "15:2033:0": "이야말로\n",
}
EXPECTED_ARITY = {
    1999: 2,
    2001: 2,
    2002: 2,
    2003: 2,
    2006: 2,
    2007: 2,
    2009: 3,
    2010: 2,
    2015: 2,
    2017: 3,
    2020: 2,
    2023: 2,
    2024: 2,
    2025: 2,
    2026: 2,
    2027: 3,
    2029: 2,
    2032: 2,
    2033: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1999:1",
    "15:2001:0",
    "15:2002:1",
    "15:2003:0",
    "15:2006:1",
    "15:2007:1",
    "15:2009:0",
    "15:2009:2",
    "15:2010:1",
    "15:2015:1",
    "15:2020:0",
    "15:2023:0",
    "15:2032:0",
    "15:2033:1",
)
PREFILL_COMPANION_DONOR = {
    "15:1999:1": "15:1969:1",
    "15:2001:0": "15:1971:0",
    "15:2002:1": "15:1972:1",
    "15:2003:0": "15:1973:0",
    "15:2006:1": "15:1969:1",
    "15:2007:1": "15:1969:1",
    "15:2009:0": "15:1979:0",
    "15:2009:2": "15:1979:2",
    "15:2010:1": "15:1969:1",
    "15:2015:1": "15:1969:1",
    "15:2020:0": "15:1990:0",
    "15:2023:0": "15:1993:0",
    "15:2032:0": "15:2002:0",
    "15:2033:1": "15:2003:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2017:1",
    "15:2027:1",
)
EXACT_BASE_DONOR = {
    1999: (15, 1969),
    2001: (15, 1971),
    2002: (15, 1972),
    2003: (15, 1973),
    2006: (15, 1976),
    2007: (15, 1977),
    2009: (15, 1979),
    2010: (15, 1980),
    2015: (15, 1985),
    2020: (15, 1990),
    2023: (15, 1993),
    2024: (15, 1994),
    2025: (15, 1995),
    2026: (15, 1996),
    2029: (15, 1999),
    2032: (15, 2002),
    2033: (15, 2003),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in {2017, 2027}
    },
    2017: (
        "15:1987:0",
        "15:1987:2",
    ),
    2027: (
        "15:1997:0",
        "15:1997:2",
    ),
}
SAME_TIME_MATCHES = (
    (15, 1969),
    (15, 1976),
    (15, 1985),
)
NOW_MATCHES = (
    (15, 1977),
    (15, 1980),
)
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
    1999: SAME_TIME_MATCHES,
    2001: (),
    2002: (),
    2003: (),
    2006: SAME_TIME_MATCHES,
    2007: NOW_MATCHES,
    2009: (),
    2010: NOW_MATCHES,
    2015: SAME_TIME_MATCHES,
    2017: WARTIME_PROPOSAL_MATCHES,
    2020: BATTLE_APOLOGY_MATCHES,
    2023: BATTLE_RELUCTANCE_MATCHES,
    2024: CIVILIAN_WELFARE_MATCHES,
    2025: WARTIME_PARDON_MATCHES,
    2026: CIVILIAN_WELFARE_MATCHES,
    2027: WARTIME_PROPOSAL_MATCHES,
    2029: (),
    2032: (
        (15, 2002),
        (15, 2086),
    ),
    2033: (
        (15, 2003),
        (15, 2087),
    ),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    2001: ((15, 1971),),
    2002: ((15, 1972),),
    2003: ((15, 1973),),
    2009: ((15, 1979),),
    2029: ATTACK_PREPARATION_MATCHES,
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1999: ((226,), ()),
    2001: ((610,), ()),
    2002: ((1174, 226), ()),
    2003: ((466,), ()),
    2006: ((226,), ()),
    2007: ((226,), ()),
    2009: ((742,), ()),
    2010: ((226,), ()),
    2015: ((226,), ()),
    2017: ((142,), ()),
    2020: ((142,), ()),
    2023: ((), ()),
    2024: ((142,), ()),
    2025: ((), ()),
    2026: ((142,), ()),
    2027: ((142,), ()),
    2029: ((466,), ("026432",)),
    2032: ((), ("026432",)),
    2033: ((), ("026432",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1388,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1999:0",
    slice_last="15:2033:0",
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
        226,
        466,
        610,
        742,
        1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1990, 2034)
    ),
    speaker_style=(
        (1999, "formal_action_timing_proposal"),
        (2001, "consultative_action_proposal"),
        (2002, "deferential_permission_request"),
        (2003, "formal_situation_counsel"),
        (2006, "formal_action_timing_proposal"),
        (2007, "formal_immediate_action_proposal"),
        (2009, "rough_urgent_action_counsel"),
        (2010, "formal_immediate_action_proposal"),
        (2015, "formal_action_timing_proposal"),
        (2017, "wartime_formal_proposal"),
        (2020, "apologetic_wartime_counsel"),
        (2023, "apologetic_wartime_proposal"),
        (2024, "formal_civilian_welfare_counsel"),
        (2025, "deferential_wartime_proposal"),
        (2026, "formal_civilian_welfare_counsel"),
        (2027, "wartime_formal_proposal"),
        (2029, "strategic_attack_preparation_counsel"),
        (2032, "humble_attack_support_proposal"),
        (2033, "humble_best_course_assessment"),
    ),
    terminology_policy=(
        ("execute policy", "시행"),
        ("execute action", "실행"),
        ("advance proposal", "추진"),
        ("counsel", "건의"),
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
        "difference between the first sixty-seven visible B128 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; seventeen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity with "
        "explicit corresponding Base donors, while two wartime proposal "
        "records use their matching Base assemblies through visible "
        "semantic references because their newline-only fragments have no "
        "promoted decision rows; Base runtime and VM state are never "
        "inherited; policy execution, action execution, proposal "
        "advancement, counsel, wartime, battlefield, common people, battle, "
        "attack, preparation, best-course assessment, pardon and each "
        "speaker register retain established project and historical "
        "terminology; direct calls, inline castle tokens, protected outer "
        "whitespace, newlines, gaps, literal arity, terminators, all "
        "fourteen same-record prefills, two hidden newlines, all forty-two "
        "slice prefills, complete assemblies, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional S1389 and S1390 decisions and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=23,
    pins={
        "expected_queue_universe_sha256": (
            "354A482D4069DE0E482F6258A08E16B37D2368C0DA8D1ADA17C9CC39FEC679B9"
        ),
        "expected_queue_slice_sha256": (
            "05A85B3099BC36EA1831C35972C39297228EAF35B332CC869FA233B42D3C0438"
        ),
        "expected_prefilled_coordinate_sha256": (
            "587A995E1C5375C31B3B6F5C2E9D9EF32BD7F45B5B8D526B268AE5ED18701592"
        ),
        "expected_prefill_slice_context_sha256": (
            "4D37F0A07C7B9F713E943FF10CB6E1430EC033AFA98835343CBF359C78FF4436"
        ),
        "expected_target_coordinate_sha256": (
            "606E9D8E6887BBDF1B967DA7A915BFF69732FB0094741D63E8B526CFAF4EE7C8"
        ),
        "expected_source_target_sha256": (
            "51A4F5008812C5CDB16EACF306A3BF46A11B25A94B435C3D2F61F0EBE6C40D32"
        ),
        "expected_current_target_sha256": (
            "58C090F415E90F18EB90CF34144549C7FB1C9972317F2F0F36FB0C46CE2C5B41"
        ),
        "expected_context_corpus_sha256": (
            "4E20716A3F245BABD767D962C2E7918428FC6142F0379F24CAC0F8815B0D9851"
        ),
        "expected_gap_contract_sha256": (
            "19A70DC311E6052679AE3356655FC1FFB8CE496145D5D82DCE9EFCFC932D2DA9"
        ),
        "expected_boundary_sha256": (
            "407C4FCE791D4683AF7D1DEEE1F48DB41998C785F165890E8A57AC18E134B6F9"
        ),
        "expected_runtime_control_sha256": (
            "E49AC066B2BDCFF52D93096CBD3F6A5770DF5221B07694D17FC799A53B27AD87"
        ),
        "expected_base_search_sha256": (
            "BD28D4DD4777D58936A068E039ED0E4827065CFF0E8A867BF65486C25C558B89"
        ),
        "expected_complete_assembly_sha256": (
            "A69E1B030D0F8F9EA20568D561DAD8E7C2E3B5FB66EAAD775B7C5A7FD8A445EC"
        ),
        "expected_call_graph_sha256": (
            "76E795E63FA4B873EB18B61F5997D81FC99C99A1AFACB6232C5E7BB07EFBEC06"
        ),
        "expected_speaker_style_sha256": (
            "6C6B63CFC1B72EFB8F3C1F351D82350E2EC793239F37C52A2647433818C85B70"
        ),
        "expected_terminology_policy_sha256": (
            "33C9452F7552E71A8E632D9D6A25CC77449E8B6B81484C7312434D420CB92BEE"
        ),
        "expected_translation_policy_sha256": (
            "303AC108D9FC1D0678FDAB39D0E99CFABE4BC2D353FC5B2E947A6CCA47412555"
        ),
        "expected_candidate_sha256": (
            "C84E5F2A9DC1C983B33F7EB2E60223FEF9DAA069CD72F7025F941CAEF85DDB64"
        ),
        "expected_combined_slice_candidate_sha256": (
            "F057884E8688BC3D51E87C15C28CAF0BE5EB5326891668629AB12B2EDA03CEBF"
        ),
        "expected_combined_changed_literal_count": 64,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B128_S1388",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1388.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1389.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B128_S1390.private.v1.jsonl",
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
