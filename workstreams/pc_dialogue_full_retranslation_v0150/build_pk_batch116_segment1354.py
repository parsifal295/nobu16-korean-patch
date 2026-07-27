#!/usr/bin/env python3
"""Build source-redacted PK B116 segment 1354 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:976:0",
    "15:976:2",
    "15:976:4",
    "15:977:0",
    "15:978:0",
    "15:979:1",
    "15:979:3",
    "15:979:5",
    "15:980:2",
    "15:981:0",
    "15:982:1",
    "15:984:0",
)
TRANSLATIONS = {
    "15:976:0": "·",
    "15:976:2": "감소\n·",
    "15:976:4": "감소",
    "15:977:0": "·",
    "15:978:0": "·",
    "15:979:1": "을(를) 받아\n",
    "15:979:3": "\n병력에",
    "15:979:5": "……",
    "15:980:2": "이(가) 벌인",
    "15:981:0": "이(가)",
    "15:982:1": "이(가) 부상",
    "15:984:0": "이(가)",
}
TARGET_RECORD_IDS = (
    976,
    977,
    978,
    979,
    980,
    981,
    982,
    984,
)
EXPECTED_ARITY = {
    976: 5,
    977: 2,
    978: 2,
    979: 6,
    980: 4,
    981: 2,
    982: 2,
    984: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:976:1",
    "15:976:3",
    "15:977:1",
    "15:978:1",
    "15:979:0",
    "15:979:2",
    "15:979:4",
    "15:980:0",
    "15:980:3",
    "15:981:1",
    "15:982:0",
    "15:984:1",
)
PREFILL_COMPANION_DONOR = {
    "15:976:1": "15:969:1",
    "15:976:3": "15:969:3",
    "15:977:1": "15:970:1",
    "15:978:1": "15:970:1",
    "15:979:0": "15:972:0",
    "15:979:2": "15:972:2",
    "15:979:4": "15:972:4",
    "15:980:0": "15:973:0",
    "15:980:3": "15:973:3",
    "15:981:1": "15:974:1",
    "15:982:0": "15:975:0",
    "15:984:1": "15:977:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:980:1",)
EXACT_BASE_DONOR = {
    976: (15, 969),
    977: (15, 970),
    978: (15, 970),
    979: (15, 972),
    981: (15, 974),
    982: (15, 975),
    984: (15, 977),
}
SEMANTIC_BASE_CONTEXT = {
    976: (),
    977: (),
    978: (),
    979: (),
    980: ("15:973:0", "15:973:2", "15:973:3"),
    981: (),
    982: (),
    984: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    976: ((15, 969),),
    977: ((15, 970), (15, 971)),
    978: ((15, 970), (15, 971)),
    979: (),
    980: (),
    981: ((15, 974),),
    982: ((15, 975),),
    984: ((15, 977),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    979: ((15, 972),),
    980: (
        (15, 907),
        (15, 973),
        (15, 1276),
        (15, 1365),
        (15, 1444),
        (15, 1485),
    ),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    980: (
        (15, 973),
        (15, 1276),
        (15, 1365),
        (15, 1444),
        (15, 1485),
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    976: ((), ("026432", "0232", "026432", "0233")),
    977: ((), ("026432",)),
    978: ((), ("026432",)),
    979: (
        (538,),
        ("025032", "023C", "026432", "0232", "0233"),
    ),
    980: ((538, 586), ("026432", "025032", "023C")),
    981: ((), ("024633", "026432")),
    982: ((), ("026432", "024633")),
    984: ((), ("026432", "025032")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1354,
    queue_start=134,
    queue_stop=199,
    slice_first="15:937:1",
    slice_last="15:984:1",
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
    source_call_roots=(538, 586),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(960, 996)
    ),
    speaker_style=(
        (976, "system_stratagem_damage_summary"),
        (977, "system_stratagem_failure_bullet"),
        (978, "system_stratagem_failure_bullet"),
        (979, "detailed_spy_damage_report"),
        (980, "male_spy_capture_report"),
        (981, "system_stratagem_success"),
        (982, "system_stratagem_injury_failure"),
        (984, "system_stratagem_damage_result"),
    ),
    terminology_policy=(
        ("durability", "내구"),
        ("troops", "병력"),
        ("spy", "간자"),
        ("stratagem", "공작"),
        ("damage", "피해"),
        ("injury", "부상"),
        ("secret order", "밀명"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("project middle dot", "·"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; "
        "seven complete records reuse approved completed Base Korean "
        "assemblies, while the spy-capture record uses the same completed "
        "Base visible wording semantically and preserves its source-identical "
        "hidden newline; Base runtime and VM state are never inherited; "
        "dynamic castle, clan, stratagem, spy, officer, durability, troop and "
        "damage-value calls retain their source ordering, subject and object "
        "particles remain explicit, and durability, troops, spies, "
        "stratagems, damage, injury and secret-order terminology follows the "
        "historical project glossary and each system or speaker register; "
        "the queue and prefill difference independently derives and pins all "
        "twelve residual coordinates; calls, inline tokens, one hidden "
        "newline, protected outer whitespace, line breaks, middle dots, "
        "project ellipses, terminators, complete record arity, all fifty-"
        "three slice prefills, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=5,
    pins={
        "expected_queue_universe_sha256": (
            "C6ADAF56AFF67E1F3846197DC22BF265DE81ABFFABFA5D87F3E976F29F3D76D9"
        ),
        "expected_queue_slice_sha256": (
            "F9BEC4DE7D19AC905398EE3F88B685FDA5585B99F1B8EA78D76EB98B3C535044"
        ),
        "expected_prefilled_coordinate_sha256": (
            "1280423AEDF803030B722C2A3107A832C8453B4368C52D1595AF53CCA688AE31"
        ),
        "expected_prefill_slice_context_sha256": (
            "967EECD3AB2CD4E7FF88207CB6A4F063CA1A0CC0BC340E10005EA0C95E645FEC"
        ),
        "expected_target_coordinate_sha256": (
            "0C6A0198BDA0565D8102E76F05DFD3F942F22736F1541FE5D678CB7AB46C1FE9"
        ),
        "expected_source_target_sha256": (
            "150E1BB55CEBEA2127B12D658668FB61AC3FB9D035CF977A80CEACC53B4D1F84"
        ),
        "expected_current_target_sha256": (
            "830D9080E1178FDDC6C8461FF6AC92BA184CA36253B23A8448FA38AE02557A00"
        ),
        "expected_context_corpus_sha256": (
            "8930F43DFB214781CF143FAC6A98B068B6446B0436C164F75DCBCF1E51E7F8D9"
        ),
        "expected_gap_contract_sha256": (
            "8FCEBFFBF0FEA19BB1305BD961B1B2BADC15C426F0A4AFFDCDAF2F1612519C57"
        ),
        "expected_boundary_sha256": (
            "F983A9705540C1FFA3C8F3E1724E5700551621785404EF9B738363FE3E027497"
        ),
        "expected_runtime_control_sha256": (
            "F7F969A53FB4A1AEF924962A14C94434EB73529992FCCD2E1FEA00CE67CB1368"
        ),
        "expected_base_search_sha256": (
            "47B2FDF2830C19BFF9CCAD0A71EE4B27C0DF1979BFEA0C5F055CB9F9A1A48034"
        ),
        "expected_complete_assembly_sha256": (
            "EB953234DDE0CEC9441C764F53845BA4FC5CD464CF8D399CB3508B5C18412AAA"
        ),
        "expected_call_graph_sha256": (
            "8895B4245946AA419D1D108F043FA973ED2F1465DD8CA0B36F16622C4CEB2806"
        ),
        "expected_speaker_style_sha256": (
            "D4A933CFCAC6A21E2222787AFCFDC34AC0E686B5CBDA9A3065F4530D8F38F6DF"
        ),
        "expected_terminology_policy_sha256": (
            "39858CDE381193FBB126167C24BEDD3DA3B3121CCA8B1CC5565D6BD73B262413"
        ),
        "expected_translation_policy_sha256": (
            "0881C6632D4E26C81FD99890D36886F60FB841B80530D81E47362C79E315F3E1"
        ),
        "expected_candidate_sha256": (
            "E344CEBA39C466AE04B743944E6FF56B10B7D23014E0896F6FB6FCF3B925FE3B"
        ),
        "expected_combined_slice_candidate_sha256": (
            "ECAFB3CEB53E672379F76404E387026E9959F7A6B7F6228F2CD0B3AB5C9FEB7D"
        ),
        "expected_combined_changed_literal_count": 53,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B116_S1354",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1354.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1352.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1353.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B116",
    "queue_row_count": 118,
    "queue_visible_count": 199,
    "queue_first": "15:867:0",
    "queue_last": "15:984:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
