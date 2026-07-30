#!/usr/bin/env python3
"""Build source-redacted PK B132 segment 1400 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2396:1",
    "15:2397:1",
    "15:2398:1",
    "15:2399:1",
    "15:2400:1",
    "15:2401:1",
    "15:2402:1",
    "15:2403:1",
    "15:2403:3",
    "15:2404:2",
    "15:2405:2",
    "15:2409:2",
    "15:2412:2",
    "15:2413:2",
    "15:2419:1",
    "15:2419:2",
    "15:2420:0",
)
TRANSLATIONS = {
    "15:2396:1": "의 수입이\n다른 가문보다 넉넉한 상태",
    "15:2397:1": "의 수입만큼은\n다른 가문보다 풍족한 상태",
    "15:2398:1": "의 수입만큼은\n다른 가문보다 풍족한 상태",
    "15:2399:1": "의 수입이\n다른 가문보다 넉넉한 상태",
    "15:2400:1": "의 수입이\n다른 가문보다 넉넉한 상태",
    "15:2401:1": "의 수입만큼은\n다른 가문보다 풍족한 상태",
    "15:2402:1": "의 수입만큼은\n다른 가문보다 풍족한 상태",
    "15:2403:1": "의",
    "15:2403:3": "……",
    "15:2404:2": "맡기",
    "15:2405:2": "결정해 주시기를 청하",
    "15:2409:2": "맡기",
    "15:2412:2": "……",
    "15:2413:2": "……",
    "15:2419:1": "\n특히",
    "15:2419:2": "의",
    "15:2420:0": "의",
}
TARGET_RECORD_IDS = (
    2396, 2397, 2398, 2399, 2400, 2401, 2402, 2403,
    2404, 2405, 2409, 2412, 2413, 2419, 2420,
)
EXPECTED_ARITY = {
    2396: 3,
    2397: 4,
    2398: 4,
    2399: 3,
    2400: 3,
    2401: 4,
    2402: 4,
    2403: 4,
    2404: 3,
    2405: 3,
    2409: 3,
    2412: 3,
    2413: 3,
    2419: 4,
    2420: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2396:0", "15:2396:2",
    "15:2397:0", "15:2397:3",
    "15:2398:0", "15:2398:3",
    "15:2399:0", "15:2399:2",
    "15:2400:0", "15:2400:2",
    "15:2401:0", "15:2401:3",
    "15:2402:0", "15:2402:3",
    "15:2403:0", "15:2403:2",
    "15:2404:0", "15:2404:1",
    "15:2405:0", "15:2405:1",
    "15:2409:0", "15:2409:1",
    "15:2412:0", "15:2412:1",
    "15:2413:0", "15:2413:1",
    "15:2419:0", "15:2419:3",
    "15:2420:1",
)
PREFILL_COMPANION_DONOR = {
    "15:2396:0": "15:2365:0",
    "15:2396:2": "15:2365:2",
    "15:2397:0": "15:2366:0",
    "15:2397:3": "15:2366:3",
    "15:2398:0": "15:2366:0",
    "15:2398:3": "15:2366:3",
    "15:2399:0": "15:2365:0",
    "15:2399:2": "15:2365:2",
    "15:2400:0": "15:2365:0",
    "15:2400:2": "15:2365:2",
    "15:2401:0": "15:2366:0",
    "15:2401:3": "15:2366:3",
    "15:2402:0": "15:2366:0",
    "15:2402:3": "15:2366:3",
    "15:2403:0": "15:2372:0",
    "15:2403:2": "15:2372:2",
    "15:2404:0": "15:2373:0",
    "15:2404:1": "15:2373:1",
    "15:2405:0": "15:2374:0",
    "15:2405:1": "15:2374:1",
    "15:2409:0": "15:2378:0",
    "15:2409:1": "15:2378:1",
    "15:2412:0": "15:2381:0",
    "15:2412:1": "15:2381:1",
    "15:2413:0": "15:2381:0",
    "15:2413:1": "15:2382:1",
    "15:2419:0": "15:2388:0",
    "15:2419:3": "15:2388:3",
    "15:2420:1": "15:2389:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2397:2",
    "15:2398:2",
    "15:2401:2",
    "15:2402:2",
)
EXACT_BASE_DONOR = {
    2396: (15, 2365),
    2399: (15, 2368),
    2400: (15, 2369),
    2403: (15, 2372),
    2404: (15, 2373),
    2405: (15, 2374),
    2409: (15, 2378),
    2412: (15, 2381),
    2413: (15, 2382),
    2419: (15, 2388),
    2420: (15, 2389),
}
SEMANTIC_BASE_CONTEXT = {
    **{record_id: () for record_id in EXACT_BASE_DONOR},
    2397: ("15:2366:0", "15:2366:1", "15:2366:3"),
    2398: ("15:2367:0", "15:2367:1", "15:2367:3"),
    2401: ("15:2370:0", "15:2370:1", "15:2370:3"),
    2402: ("15:2371:0", "15:2371:1", "15:2371:3"),
}
INCOME_SIMPLE_MATCHES = ((15, 2365), (15, 2368), (15, 2369))
INCOME_EXTENDED_MATCHES = (
    (15, 2366), (15, 2367), (15, 2370), (15, 2371),
)
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    2420: ((15, 2389),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    2396: INCOME_SIMPLE_MATCHES,
    2397: INCOME_EXTENDED_MATCHES,
    2398: INCOME_EXTENDED_MATCHES,
    2399: INCOME_SIMPLE_MATCHES,
    2400: INCOME_SIMPLE_MATCHES,
    2401: INCOME_EXTENDED_MATCHES,
    2402: INCOME_EXTENDED_MATCHES,
    2403: ((15, 2372),),
    2404: ((15, 2373),),
    2405: ((15, 2374),),
    2409: ((15, 2378),),
    2412: ((15, 2381),),
    2413: ((15, 2382),),
    2419: ((15, 2388),),
    2420: ((15, 2389),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2396: ((550, 1066), ("023C",)),
    2397: ((550, 1096), ("023C", "023C")),
    2398: ((550, 1096), ("023C", "023C")),
    2399: ((550, 1066), ("023C",)),
    2400: ((550, 1066), ("023C",)),
    2401: ((550, 1096), ("023C", "023C")),
    2402: ((550, 1096), ("023C", "023C")),
    2403: ((562,), ("025132", "026432")),
    2404: ((178, 1168, 142), ()),
    2405: ((160, 1174, 190), ()),
    2409: ((550, 1168, 142), ()),
    2412: ((598, 550), ()),
    2413: ((598, 550), ()),
    2419: ((178, 610), ("023C", "025132")),
    2420: ((88,), ("023C", "025132")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1400,
    queue_start=0,
    queue_stop=67,
    slice_first="15:2396:0",
    slice_last="15:2422:0",
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
        88, 142, 160, 178, 190, 550, 562, 598, 610,
        1066, 1096, 1168, 1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2355, 2424)
    ),
    speaker_style=(
        (2396, "formal_income_policy_assessment"),
        (2397, "formal_income_battle_diplomacy_assessment"),
        (2398, "formal_income_battle_diplomacy_assessment"),
        (2399, "formal_income_policy_assessment"),
        (2400, "formal_income_policy_assessment"),
        (2401, "formal_income_battle_diplomacy_assessment"),
        (2402, "formal_income_battle_diplomacy_assessment"),
        (2403, "hesitant_attack_timing_assessment"),
        (2404, "deferential_disadvantage_readiness_counsel"),
        (2405, "cautious_disadvantage_timing_request"),
        (2409, "confident_advantage_readiness_counsel"),
        (2412, "anxious_provisions_assessment"),
        (2413, "anxious_ally_support_assessment"),
        (2419, "cautious_great_power_diplomacy_counsel"),
        (2420, "vigilant_great_power_monitoring_counsel"),
    ),
    terminology_policy=(
        ("our house", "우리 가문"),
        ("income", "수입"),
        ("diplomacy", "외교"),
        ("policy", "정책"),
        ("battle", "합전"),
        ("bargaining chip", "협상 카드"),
        ("capture", "공략"),
        ("timing", "시기"),
        ("disadvantage and advantage", "열세, 우세"),
        ("officers and soldiers", "장병"),
        ("sortie", "출진"),
        ("provisions", "병량"),
        ("allies", "우군"),
        ("great power", "대세력"),
        ("dispute", "분쟁"),
        ("movement", "동향"),
        ("watch closely", "주시"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B132 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; eleven complete "
        "records reuse approved completed Base Korean assemblies selected "
        "by raw, literal and operand-masked source identity, while four "
        "source-identical records whose hidden newline is not a visible "
        "Base decision use their corresponding completed Base rows only as "
        "semantic context; Base runtime and VM state are never inherited; "
        "income, diplomacy, policy, battle, bargaining chips, attack timing, "
        "officers and soldiers, sortie, provisions, allies, great powers, "
        "disputes and monitoring retain established historical project "
        "terminology and formal, deferential, cautious, confident or anxious "
        "speaker registers; calls, inline house and force tokens, protected "
        "outer whitespace, line breaks, particles, punctuation, ellipses, "
        "terminators, complete record arity, all fifty slice prefills, all "
        "twenty-nine visible same-record companions, four hidden newline "
        "companions, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, reciprocal S1401 and S1402 "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256":
        "4B81A2B81F0E8C254EBA4771F9E0DCDF4F57F82DF74DE0B5E0E61D99D11263A4",
        "expected_queue_slice_sha256":
        "77FFBFBA0EFF6E1B1D0E18881EF75D8B463DCF513373D2D2C102B4B93331A661",
        "expected_prefilled_coordinate_sha256":
        "E7930E6492046C52C9F0276787CE4ED949C0229BAD1187EBB0047C851A6BE5FD",
        "expected_prefill_slice_context_sha256":
        "8910A902744EAAC7931D96B37B0FDBD30EBDE0363E503831C5BE12E99B786CEF",
        "expected_target_coordinate_sha256":
        "BC3279AB71C5E4E3DBBA19DBED3C8557B97E457111541D6C8E7522935DC4E34F",
        "expected_source_target_sha256":
        "633F7D617B6CFF1B2E8D63EB1461719B4D331B91FDAEF220AF89CD3C8EB81859",
        "expected_current_target_sha256":
        "F85FDFE1EDB18D1277384A29E7591A56FECABDA5471ACDD605967310035E61F4",
        "expected_context_corpus_sha256":
        "8D8785D2CB13D6EEC821599ACD953FE03E89249059B0051AEA785D3BD2C6F60B",
        "expected_gap_contract_sha256":
        "90A4711714DD38E605EEAA615AA4745314DEFEDFD406391ABDE104751161AD4D",
        "expected_boundary_sha256":
        "2EF02B69B4FB5F531CEC62370BE14E62C5A0FFC2E410901EA5956025CF0F5267",
        "expected_runtime_control_sha256":
        "5BEF3911B06D60BA63A10C46299ED4A78BC900C01F3527D10D98B5EC8B772970",
        "expected_base_search_sha256":
        "905C7A9CED8C7938CF8B1561AE8FCAD7AE53DD623211121D8830A0BA20D7294A",
        "expected_complete_assembly_sha256":
        "54D55A187147FF67C8E7EA4ABB3F6ACE78343D5D564960F6FC0D3200746A5589",
        "expected_call_graph_sha256":
        "18F10E2085C3B269F345BE6FBC68576351D20DEEB22DEE01010E521AE1A859DF",
        "expected_speaker_style_sha256":
        "2F3DF2A2250E14DAB8B3441FFF02744EF3EA71F4603EB6889F7640EF16919488",
        "expected_terminology_policy_sha256":
        "FBC20AB3BC8D02C2A437D3D90C167B3A3F0BAD7B58FD14A6B808A477FC771AB9",
        "expected_translation_policy_sha256":
        "0CF1655F646EA5702F2ECED642681B960E7544221E7A17FE97B677124EA66C43",
        "expected_candidate_sha256":
        "E74CEC2F85F0143AC88BFBC93E273449D8371376D3EEBB230A93826A47F63333",
        "expected_combined_slice_candidate_sha256":
        "61807E08E0F758EF5CEE0A6BA7BEDC7766C43F0DC1B22C563B82B9829151DAAD",
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B132_S1400",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1400.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1401.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1402.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B132",
    "queue_row_count": 78,
    "queue_visible_count": 200,
    "queue_first": "15:2396:0",
    "queue_last": "15:2474:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
