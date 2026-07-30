#!/usr/bin/env python3
"""Build source-redacted PK B115 segment 1349 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:751:0",
    "15:751:1",
    "15:751:2",
    "15:752:0",
    "15:752:2",
    "15:753:0",
    "15:753:2",
    "15:754:0",
    "15:754:1",
    "15:756:0",
    "15:756:2",
    "15:756:3",
    "15:757:1",
    "15:757:2",
    "15:758:0",
    "15:758:1",
    "15:758:2",
    "15:758:3",
    "15:759:0",
    "15:760:0",
    "15:760:2",
    "15:763:1",
    "15:764:1",
)
TRANSLATIONS = {
    "15:751:0": "서둘러 병사를 모은",
    "15:751:1": "다!\n",
    "15:751:2": (
        "에 몰려오는 적을\n"
        "맞아 싸우기에는 병력이 부족하다"
    ),
    "15:752:0": (
        "급작스럽사오나 무리해서라도 병사를 모으시지요"
    ),
    "15:752:2": (
        "으로(로) 적이 진군하는 지금\n"
        "맞아 싸울 병사는 아무리 많아도 지나치지 않사옵니다"
    ),
    "15:753:0": "곧바로 병사를 소집하자",
    "15:753:2": (
        "을(를) 확실히 지켜 내려면\n"
        "병사는 많으면 많을수록 좋다"
    ),
    "15:754:0": (
        "에 적이 진군 중이옵니다……\n"
        "서둘러 병사를 모아야 하옵니다"
    ),
    "15:754:1": (
        "\n이대로는 맞아 싸울 병력이 부족하옵니다"
    ),
    "15:756:0": "마을마다 병사를 모아야 하옵니다",
    "15:756:2": "에 적이 다가오고 있사옵니다",
    "15:756:3": (
        "\n무리를 무릅쓰고라도 성을 지켜야 하옵니다……"
    ),
    "15:757:1": (
        "에 다가오는 적을\n"
        "막아 내야 하옵니다"
    ),
    "15:757:2": "!",
    "15:758:0": "어서 병사를 모아야 한다",
    "15:758:1": "!\n이대로는",
    "15:758:2": (
        "에 다가오는 적을\n"
        "맞아 싸울 수 없다"
    ),
    "15:758:3": "!",
    "15:759:0": "서둘러 병사를 모으시지요",
    "15:760:0": (
        "급작스럽사오나 무리해서라도 병사를 모으시지요"
    ),
    "15:760:2": (
        "으로(로) 적이 진군하는 지금\n"
        "맞아 싸울 병사는 아무리 많아도 지나치지 않사옵니다"
    ),
    "15:763:1": "지만\n",
    "15:764:1": "명을 모으",
}
TARGET_RECORD_IDS = (
    751,
    752,
    753,
    754,
    756,
    757,
    758,
    759,
    760,
    763,
    764,
)
EXPECTED_ARITY = {
    751: 3,
    752: 3,
    753: 3,
    754: 2,
    756: 4,
    757: 3,
    758: 4,
    759: 3,
    760: 3,
    763: 3,
    764: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:757:0",
    "15:759:2",
    "15:763:0",
    "15:763:2",
    "15:764:0",
)
PREFILL_COMPANION_DONOR = {
    "15:757:0": "15:750:0",
    "15:759:2": "15:752:1",
    "15:763:0": "15:756:0",
    "15:763:2": "15:756:2",
    "15:764:0": "15:757:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:752:1",
    "15:753:1",
    "15:756:1",
    "15:759:1",
    "15:760:1",
)
EXACT_BASE_DONOR = {
    763: (15, 756),
    764: (15, 757),
}
SEMANTIC_BASE_CONTEXT = {
    751: (
        "15:742:0",
        "15:742:1",
        "15:744:0",
        "15:744:1",
    ),
    752: ("15:745:0", "15:745:1"),
    753: ("15:746:0", "15:746:1"),
    754: ("15:747:0", "15:747:1"),
    756: ("15:748:0", "15:748:1"),
    757: ("15:750:0", "15:750:1"),
    758: ("15:751:0", "15:751:1"),
    759: ("15:752:0", "15:752:1"),
    760: ("15:745:0", "15:745:1"),
    763: (),
    764: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    763: ((15, 756),),
    764: ((15, 757),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    751: ((1066, 1078), ("026432",)),
    752: ((1066, 1078), ("026432",)),
    753: ((1162, 610), ("026432",)),
    754: ((610, 1078), ("026432",)),
    756: ((610, 1090), ("026432",)),
    757: ((1078,), ("026432",)),
    758: ((1066, 748), ("026432",)),
    759: ((1066,), ("026432",)),
    760: ((1066, 1078), ("026432",)),
    763: ((1090, 466), ("026432",)),
    764: ((538,), ("026432", "0232")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1349,
    queue_start=0,
    queue_stop=67,
    slice_first="15:731:0",
    slice_last="15:773:0",
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
        466,
        538,
        610,
        748,
        1066,
        1078,
        1090,
        1162,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(740, 781)
    ),
    speaker_style=(
        (751, "forceful_commander_urgent_recruitment"),
        (752, "formal_emergency_recruitment_advice"),
        (753, "decisive_commander_recruitment"),
        (754, "formal_defensive_advice"),
        (756, "formal_castle_defense_advice"),
        (757, "formal_urgent_defense_advice"),
        (758, "forceful_urgent_defense"),
        (759, "formal_emergency_defense_advice"),
        (760, "formal_emergency_recruitment_advice"),
        (763, "formal_emergency_conscription_advice"),
        (764, "concise_emergency_conscription_result"),
    ),
    terminology_policy=(
        ("soldiers", "병사"),
        ("troops", "병력"),
        ("emergency conscription", "긴급 징병"),
        ("popular support", "민심"),
        ("war", "전란"),
        ("castle", "성"),
        ("meet in battle", "맞아 싸우다"),
        ("defend", "막아 내다"),
        ("force through", "무리를 무릅쓰고 강행하다"),
        ("dynamic castle particle", "에 또는 으로(로)"),
        ("project ellipsis", "……"),
        ("project exclamation mark", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; two "
        "complete emergency-conscription records use approved completed Base "
        "literal-and-masked-call exact donors, while the nine PK-only urgent "
        "castle-defense records are freshly reviewed against completed Base "
        "emergency recruitment, defense and conscription wording; Base "
        "runtime and VM state are never inherited; dynamic castle, force, "
        "speaker and soldier-count calls retain their source ordering, castle "
        "particles remain explicit, and soldiers, troops, emergency "
        "conscription, popular support, war, castle defense and forced-action "
        "terminology follows the historical project glossary and each "
        "speaker's formal or forceful register; the queue and prefill "
        "difference independently derives and pins all twenty-three residual "
        "coordinates; calls, inline tokens, five source-identical hidden "
        "newlines, protected outer whitespace, line breaks, ASCII "
        "exclamation marks, terminators, complete record arity, all forty-"
        "four slice prefills, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=22,
    pins={
        "expected_queue_universe_sha256": (
            "D9F766CAA805AA167D8C09773CD0A666B92E68767EAD94B3AA2EC0B9284AE4AD"
        ),
        "expected_queue_slice_sha256": (
            "217ACB9DD8707DCAED8421C90B8E3AB664F4FE8DFC414750E1658BA1413A4429"
        ),
        "expected_prefilled_coordinate_sha256": (
            "4644B6FA46648721171DA1F23C840E9A6F8CC6C2C1CBF12F583EB803F817BC8F"
        ),
        "expected_prefill_slice_context_sha256": (
            "7D5695387D740C9E4D711957670459C9A66B57761F49B3B136DABBB12727C49E"
        ),
        "expected_target_coordinate_sha256": (
            "0E17CAE4653EF7467DCA3E73331036BC5D30B2B2F5F2660B1EE4547940008C27"
        ),
        "expected_source_target_sha256": (
            "DFB206B0F40DB697BB8B3B8EB4F2D75E654B13C06476AB9499925907F29B5A6F"
        ),
        "expected_current_target_sha256": (
            "150E578976F1F5FCBD94604A8602A086C795B203C8849C8748EEF47C5610A368"
        ),
        "expected_context_corpus_sha256": (
            "772FD0363F937E84A0616D73BFBFA06C5A93975F5B62740B948226EAF9D84722"
        ),
        "expected_gap_contract_sha256": (
            "F124421BC1ED3526B487A574988A066C3FCCC93D36896483BECC0EE6A71E2F17"
        ),
        "expected_boundary_sha256": (
            "3E2239F563C802DEDD38AD46EAF50ECB23A65A86812273020E38A76ABCA3F661"
        ),
        "expected_runtime_control_sha256": (
            "CBA3FB726A24152458D69142E012B62EB886300F0CBC6A6CEC869D687A9AE0F3"
        ),
        "expected_base_search_sha256": (
            "9A060CF3076FD9809D2F10919258B19EADA45CCF1716D3C163720FA0D9A6D429"
        ),
        "expected_complete_assembly_sha256": (
            "B7F3E751C62FF9F72E369392693D6944498571621455678B3E1FDE150C7493E1"
        ),
        "expected_call_graph_sha256": (
            "16B842ACAD9DAA8C0E0EB1EB012683F83969408B791772E4E64ECCB57A7F17E9"
        ),
        "expected_speaker_style_sha256": (
            "F7A16B175407F1FB10B0F079670C17BF9136B927C0A994A14935FDFFF7DAE661"
        ),
        "expected_terminology_policy_sha256": (
            "82BD16973F9619ADD0E4065ECB9CDA16F8E60D1BAB1E81B31347B9517EE1B296"
        ),
        "expected_translation_policy_sha256": (
            "20F48BDD2739A69BA3745444C96ED2863890C01EFBEB59470506112100C3BE3C"
        ),
        "expected_candidate_sha256": (
            "A53154037286C295069A7DA2F195060CA5E7A5996F94FBFCA97A11F13597CCBE"
        ),
        "expected_combined_slice_candidate_sha256": (
            "339D82EC93427A48E2CBC6CE822EE128C98CD69BF9387A710814CC6C7944CE01"
        ),
        "expected_combined_changed_literal_count": 58,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B115_S1349",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1349.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1350.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1351.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B115",
    "queue_row_count": 136,
    "queue_visible_count": 199,
    "queue_first": "15:731:0",
    "queue_last": "15:866:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
