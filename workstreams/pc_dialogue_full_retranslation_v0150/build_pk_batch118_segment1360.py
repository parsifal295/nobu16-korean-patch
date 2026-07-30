#!/usr/bin/env python3
"""Build source-redacted PK B118 segment 1360 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1193,
    1194,
    1195,
    1196,
    1197,
    1200,
    1201,
    1214,
    1216,
)
TARGET_COORDINATES = (
    "15:1193:0",
    "15:1193:1",
    "15:1194:0",
    "15:1194:1",
    "15:1195:0",
    "15:1196:0",
    "15:1197:0",
    "15:1200:1",
    "15:1201:1",
    "15:1214:0",
    "15:1216:0",
    "15:1216:1",
)
TRANSLATIONS = {
    "15:1193:0": "·",
    "15:1193:1": "와(과)",
    "15:1194:0": "·",
    "15:1194:1": "와(과)",
    "15:1195:0": "·",
    "15:1196:0": "부터",
    "15:1197:0": "부터",
    "15:1200:1": "에",
    "15:1201:1": "→",
    "15:1214:0": "이번",
    "15:1216:0": "의 신용 ",
    "15:1216:1": "→",
}
EXPECTED_ARITY = {
    1193: 3,
    1194: 3,
    1195: 2,
    1196: 2,
    1197: 2,
    1200: 3,
    1201: 2,
    1214: 3,
    1216: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1193:2",
    "15:1194:2",
    "15:1195:1",
    "15:1196:1",
    "15:1197:1",
    "15:1200:0",
    "15:1200:2",
    "15:1201:0",
    "15:1214:1",
    "15:1214:2",
)
PREFILL_COMPANION_DONOR = {
    "15:1193:2": "15:1185:2",
    "15:1194:2": "15:1185:2",
    "15:1195:1": "15:1187:1",
    "15:1196:1": "15:1188:1",
    "15:1197:1": "15:1188:1",
    "15:1200:0": "15:1192:0",
    "15:1200:2": "15:1192:2",
    "15:1201:0": "15:1193:0",
    "15:1214:1": "15:1206:1",
    "15:1214:2": "15:1206:2",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ()
EXACT_BASE_DONOR = {
    1193: (15, 1185),
    1194: (15, 1185),
    1195: (15, 1187),
    1196: (15, 1188),
    1197: (15, 1188),
    1200: (15, 1192),
    1201: (15, 1193),
    1214: (15, 1206),
    1216: (15, 1208),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_RAW_MATCHES = {
    1193: ((15, 1185), (15, 1186)),
    1194: ((15, 1185), (15, 1186)),
    1195: ((15, 1187),),
    1196: ((15, 1188), (15, 1189)),
    1197: ((15, 1188), (15, 1189)),
    1200: (),
    1201: ((15, 1193),),
    1214: ((15, 1206),),
    1216: ((15, 1208), (15, 1209)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1200: ((15, 1192),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    1193: ((), ("029632", "029732")),
    1194: ((), ("029632", "029732")),
    1195: ((), ("029632", "029732")),
    1196: ((), ("029632", "029732")),
    1197: ((), ("029632", "029732")),
    1200: ((1, 904, 1162), ("025032",)),
    1201: ((), ("025032", "023C", "023D050505")),
    1214: ((), ("023C", "025032")),
    1216: ((), ("025032", "0232", "0233050505")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1360,
    queue_start=134,
    queue_stop=200,
    slice_first="15:1170:0",
    slice_last="15:1216:1",
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
        1,
        904,
        1162,
    ),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(1178, 1224)
    ),
    speaker_style=(
        (1193, "system_road_opening_summary"),
        (1194, "system_road_opening_summary"),
        (1195, "system_army_passage_notice"),
        (1196, "system_directional_road_opening"),
        (1197, "system_directional_road_opening"),
        (1200, "confident_formal_relationship_proposal"),
        (1201, "system_friendship_change"),
        (1214, "formal_relationship_outcome_report"),
        (1216, "system_trust_change"),
    ),
    terminology_policy=(
        ("road", "가도"),
        ("road opening", "개통"),
        ("army", "군세"),
        ("passage", "통행"),
        ("relationship improvement", "관계 개선"),
        ("money", "금전"),
        ("friendship", "우호도"),
        ("trust", "신용"),
        ("our house", "우리 가문"),
        ("dynamic conjunction", "와(과)"),
        ("directional particle", "(으)로"),
        ("project middle dot", "·"),
        ("project change arrow", "→"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B118 queue ordinals 134 through 199 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; all nine complete records reuse "
        "approved completed Base Korean assemblies selected by raw, literal "
        "and operand-masked source identity; Base runtime and VM state are "
        "never inherited; roads, openings, army passage, relationship "
        "improvement, friendship, trust, house references, dynamic "
        "conjunctions and directional particles retain established project "
        "and historical terminology; direct calls, inline settlement, "
        "faction, operation and old or new value tokens, protected outer "
        "whitespace, gaps, literal arity, terminators, all ten same-record "
        "prefills, all fifty-four slice prefills, complete assemblies, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256": (
            "1207015E2B3B81B1D053FA00F35628E780A874C0D44CFB013764244FF33CAAC3"
        ),
        "expected_queue_slice_sha256": (
            "3F03FE80D0B511687D13DF2D0758E223BD8F9E467B2EF8D950C1C8A164D2B2B9"
        ),
        "expected_prefilled_coordinate_sha256": (
            "63B15B37C1502029387A4F4287CAFAA0DF5B6B10DBA2EE56D23D0134BDC1E679"
        ),
        "expected_prefill_slice_context_sha256": (
            "16E04980B8F8149E3D7EACA4C73DE28BC25504454C6F3D72A8658516FF9EF51B"
        ),
        "expected_target_coordinate_sha256": (
            "93AFA2F048FB45D9B68A1F1B5F0340E1E256BFE00A560CC8BEF107D25C7325BC"
        ),
        "expected_source_target_sha256": (
            "13B766FDDE7A9D49B1E9EEA5E66D2216CB46E85989DAC924993DDDAD4DDBD05E"
        ),
        "expected_current_target_sha256": (
            "175C616E23B0CE850AE2F04DA04000421B333551156CC3EC92BBCAF45ED31836"
        ),
        "expected_context_corpus_sha256": (
            "01132F26EE8C33E41493AAE3EC7099BA97DC2F1DFB38E6B5FD215321136F9F4A"
        ),
        "expected_gap_contract_sha256": (
            "52008F57C9622D9201FF71BFC88EBE1E1EB1CCCD84E16255713531EEB4BE43B8"
        ),
        "expected_boundary_sha256": (
            "CEE95C5985C10B8DED00E1B870BB927314FEDA27439A0DD5BCEBFE12B22E0278"
        ),
        "expected_runtime_control_sha256": (
            "E72C23C2DA7D4886649E36EE7497D5AD33F166DCF6FA43206A0B614B4C74AD69"
        ),
        "expected_base_search_sha256": (
            "C1A65DC283D7BDCEA7F4A5E1DF7D748138A40C3A63EF46F2FE25F35A02C5102A"
        ),
        "expected_complete_assembly_sha256": (
            "7B1F4C15FF849AB33AC85066A5D35A6260CADBB268DA3283124AA161EF5196BD"
        ),
        "expected_call_graph_sha256": (
            "1BD77263E60507E596AB0985CE33A60575B5A0DCA812DEB5AAC2556964714057"
        ),
        "expected_speaker_style_sha256": (
            "91DE169A5BED6D47761CE6D5896E3483C44CAFED096B7EB8FB3093C6DDBAC1F6"
        ),
        "expected_terminology_policy_sha256": (
            "FD52162C6BBB49A7A371763551DD8B33E37A684BF5E1DD4D97EC8DBA60C6F31A"
        ),
        "expected_translation_policy_sha256": (
            "7E3F7450AA612452EAE64227FB1625D368076AA8732516CBFE845E85114CB053"
        ),
        "expected_candidate_sha256": (
            "0E1A6AC660DFFFB5129B7202938CF342BD3C1E91CA26256ED8A64AEFB789D29B"
        ),
        "expected_combined_slice_candidate_sha256": (
            "89A5C3204A7D708171369D6A47C11EB98A7833E988BDE2F88C82600AB51D55B9"
        ),
        "expected_combined_changed_literal_count": 44,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B118_S1360",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1360.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1358.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1359.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B118",
    "queue_row_count": 111,
    "queue_visible_count": 200,
    "queue_first": "15:1106:0",
    "queue_last": "15:1216:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
