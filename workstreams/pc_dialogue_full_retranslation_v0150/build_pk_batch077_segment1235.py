#!/usr/bin/env python3
"""Build source-redacted PK B077 segment 1235 residual decisions."""

from pathlib import Path

from build_pk_batch077_common import make_config, run


SCRIPT = Path(__file__).resolve()
TARGET_RECORD_IDS = (
    995, 998, 999, 1000, 1001, 1002, 1003, 1004, 1007, 1010,
)
BASE_DONORS = {
    995: 983,
    998: 986,
    999: 987,
    1000: 988,
    1001: 989,
    1002: 990,
    1003: 991,
    1004: 992,
    1007: 995,
    1010: 998,
}
CONFIG = make_config(
    script=SCRIPT,
    segment=1235,
    queue_start=0,
    queue_stop=67,
    slice_first="8:995:0",
    slice_last="8:1019:1",
    target_coordinates=(
        "8:995:0",
        "8:998:0",
        "8:998:1",
        "8:998:2",
        "8:999:1",
        "8:999:2",
        "8:1000:1",
        "8:1000:2",
        "8:1001:0",
        "8:1001:1",
        "8:1001:2",
        "8:1002:1",
        "8:1002:2",
        "8:1003:1",
        "8:1003:2",
        "8:1004:0",
        "8:1004:1",
        "8:1007:0",
        "8:1007:1",
        "8:1010:0",
    ),
    translations={
        "8:995:0": ", 맡겨",
        "8:998:0": ", 맡겨",
        "8:998:1": "\n그리",
        "8:998:2": ", 우선 「",
        "8:999:1": "\n우선 「",
        "8:999:2": "」 성하에 「",
        "8:1000:1": "\n우선 「",
        "8:1000:2": "」 성하에 「",
        "8:1001:0": ", 맡겨",
        "8:1001:1": "\n그리",
        "8:1001:2": ", 우선 「",
        "8:1002:1": "\n우선 「",
        "8:1002:2": "」 성하에 「",
        "8:1003:1": "\n우선 「",
        "8:1003:2": "」 성하에 「",
        "8:1004:0": ", 맡겨",
        "8:1004:1": "\n그리",
        "8:1007:0": ", 맡겨",
        "8:1007:1": "\n우선 「",
        "8:1010:0": ", 맡겨",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        995: 3,
        998: 5,
        999: 4,
        1000: 4,
        1001: 5,
        1002: 4,
        1003: 4,
        1004: 4,
        1007: 3,
        1010: 2,
    },
    prefill_companion_coordinates=(
        "8:995:1",
        "8:995:2",
        "8:998:3",
        "8:998:4",
        "8:999:0",
        "8:999:3",
        "8:1000:0",
        "8:1000:3",
        "8:1001:3",
        "8:1001:4",
        "8:1002:0",
        "8:1002:3",
        "8:1003:0",
        "8:1003:3",
        "8:1004:2",
        "8:1004:3",
        "8:1007:2",
        "8:1010:1",
    ),
    prefill_companion_donor={
        "8:995:1": "8:983:1",
        "8:995:2": "8:983:2",
        "8:998:3": "8:986:3",
        "8:998:4": "8:986:4",
        "8:999:0": "8:987:0",
        "8:999:3": "8:987:3",
        "8:1000:0": "8:988:0",
        "8:1000:3": "8:988:3",
        "8:1001:3": "8:986:3",
        "8:1001:4": "8:989:4",
        "8:1002:0": "8:987:0",
        "8:1002:3": "8:990:3",
        "8:1003:0": "8:991:0",
        "8:1003:3": "8:988:3",
        "8:1004:2": "8:992:2",
        "8:1004:3": "8:992:3",
        "8:1007:2": "8:995:2",
        "8:1010:1": "8:998:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        record_id: tuple(
            f"8:{BASE_DONORS[record_id]}:{literal_id}"
            for literal_id in range({
                995: 3,
                998: 5,
                999: 4,
                1000: 4,
                1001: 5,
                1002: 4,
                1003: 4,
                1004: 4,
                1007: 3,
                1010: 2,
            }[record_id])
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_raw_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_base_literal_matches={
        record_id: ((8, BASE_DONORS[record_id]),)
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: ((8, BASE_DONORS[record_id]),)
        for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record={
        995: ((862, 322, 226), ("028C32",)),
        998: ((862, 322, 604, 1066), ("02463F", "023C")),
        999: ((628, 226), ("02463F", "023C")),
        1000: ((1066, 142), ("02463F", "023C")),
        1001: ((862, 322, 604, 1066), ("02463F", "023C")),
        1002: ((628, 226), ("02463F", "023C")),
        1003: ((1066, 142), ("02463F", "023C")),
        1004: ((862, 322, 604, 226), ("023C",)),
        1007: ((862, 322, 1066), ("026432",)),
        1010: ((862, 322, 1096), ()),
    },
    source_call_roots=(142, 226, 322, 604, 628, 862, 1066, 1096),
    boundary_record_keys=tuple(
        (8, record_id)
        for record_id in (
            982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992,
            994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003,
            1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011,
            1018, 1019, 1020,
        )
    ),
    speaker_style=(
        (995, "confident_external_relations_proposal"),
        (998, "confident_castle_town_development_proposal"),
        (999, "formal_assigned_land_development_proposal"),
        (1000, "formal_land_enrichment_proposal"),
        (1001, "confident_military_preparation_proposal"),
        (1002, "formal_assigned_land_armament_proposal"),
        (1003, "formal_land_governance_proposal"),
        (1004, "confident_domain_facility_proposal"),
        (1007, "confident_castle_capture_planning"),
        (1010, "confident_land_enrichment_pledge"),
    ),
    terminology_policy=(
        ("castle town", "성하"),
        ("assigned territory", "임지"),
        ("domain", "영내"),
        ("governance", "통치"),
        ("armaments", "군비"),
        ("castle capture", "공략"),
        ("facility and person tokens", "「」"),
        ("confident acceptance", "맡겨"),
    ),
    basis=(
        "pristine PK Japanese is authoritative and complete PK English, "
        "Simplified Chinese and Traditional Chinese context was manually "
        "reviewed; ten completed Base records with identical literal and "
        "operand-masked templates supply semantic wording only, while their "
        "runtime and VM state are never inherited; twenty residuals and "
        "eighteen exact-prefill companions form ten complete proposal and "
        "pledge records; castle-town, domain, governance, armament and capture "
        "terminology, speaker register, dynamic quoted names, inline tokens, "
        "calls, protected whitespace, gaps, boundaries, two-run reproduction, "
        "tamper rejection, reverse overlays, outside-scope identity and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256":
        "A773BC2A346A94EF11442275CC15B7EC79729ABC130B1FB137130468C8D5B917",
        "expected_queue_slice_sha256":
        "76E6D3043E4C5A54ECC2EDF5381A2ADA13E58729748DFF9E0A54BD508B92B326",
        "expected_prefilled_coordinate_sha256":
        "1A6A474B95F89F7EBEA4FF77A5E0D055AFEB5869E2E6F7FCD5F6946CA3295E18",
        "expected_prefill_slice_context_sha256":
        "CEEEE7D93987B10A594CE2B716C51BF9275D908FA7EEF32282731AD09F4CB272",
        "expected_target_coordinate_sha256":
        "8C2CBF1ABAE5C63412604B40385B8EEA264D008D3F3B41C2D761FE6A33058138",
        "expected_source_target_sha256":
        "BF0F8DF13BAD76878C1DDB50AF1CE0F66FA748CFBC59F55D791B77FF60058A6D",
        "expected_current_target_sha256":
        "91BBEAA4684F7BEF1CFD29AF0B858412BDDA81129969DD0F6CECA0C42F11935D",
        "expected_context_corpus_sha256":
        "BC6AD64CCD8C2F358FF09BB1BF406A04308A1A9B4F3BBA75A80BEDE5FCC75621",
        "expected_gap_contract_sha256":
        "68727B716E288370927E8A56F1EE1FDC91171329789648F9F1F69A8EE173FFDE",
        "expected_boundary_sha256":
        "CBF5571349561C4BE80E3AC16FF34DBFB28540234FCEC9CECEEC013154059FBD",
        "expected_runtime_control_sha256":
        "699A7DF61E601C87DE4040E9E6916256BF309D2A8D2D7A7DE4F295D5488E2D70",
        "expected_base_search_sha256":
        "AA20921D7AFC5EE75349D7D2D9CFEA4F4BFDA4E7ADA73D3B321E8F0E1E43D0CB",
        "expected_complete_assembly_sha256":
        "C1AA3337796C07B207A3BA1CFC9F71C258B95D7FE32410869CCEAF6EFDC8335F",
        "expected_call_graph_sha256":
        "F25A0ED9D708BAC26E60A2C694549E8ED359434FD631ACF7A192DBFDE7A11087",
        "expected_speaker_style_sha256":
        "616BC73D70350EC0F3345807269C3223FFCA229BB343F4C7FE67CD42EB11B7AE",
        "expected_terminology_policy_sha256":
        "5BCCF64C3FF60E873E02D59330B8A96CB8D45B92B48DA76D691F253F0BA45910",
        "expected_translation_policy_sha256":
        "7E1AF6894A55DCF8C61331028A29F3677498C4C1A32358528B94B266906E8C24",
        "expected_candidate_sha256":
        "2E0BAAF6C85A2DC266D517D8B3793397F8F7EC82920B94C3782096CB6DBECCC0",
        "expected_combined_slice_candidate_sha256":
        "FCFAA0FAFC5DAACC218979BEFCD8E28E560ECE4B46CF9DA8BC749AEB1538AFF4",
        "expected_combined_changed_literal_count": 55,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
