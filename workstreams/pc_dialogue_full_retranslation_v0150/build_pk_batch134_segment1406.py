#!/usr/bin/env python3
"""Build source-redacted PK B134 segment 1406 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2548:0", "15:2548:1", "15:2548:2", "15:2548:3",
    "15:2549:0", "15:2549:1", "15:2549:2",
    "15:2550:0", "15:2550:1", "15:2550:2",
    "15:2551:0", "15:2551:1",
    "15:2552:0", "15:2552:1", "15:2552:2",
    "15:2553:0", "15:2553:1", "15:2553:2",
    "15:2554:0", "15:2554:1", "15:2554:2", "15:2554:3",
    "15:2555:0", "15:2555:1", "15:2555:2", "15:2555:3",
    "15:2555:4",
    "15:2556:0", "15:2556:1", "15:2556:2", "15:2556:3",
    "15:2556:4",
    "15:2557:0", "15:2557:1", "15:2557:2", "15:2557:3",
    "15:2557:4", "15:2557:5",
    "15:2558:0", "15:2558:1", "15:2558:2", "15:2558:3",
    "15:2558:4",
    "15:2559:0", "15:2559:1", "15:2559:2", "15:2559:3",
    "15:2559:4",
    "15:2560:0", "15:2560:1", "15:2560:2",
    "15:2561:0", "15:2561:1",
    "15:2562:0", "15:2562:1",
    "15:2563:0", "15:2563:1", "15:2563:2", "15:2563:3",
    "15:2564:0", "15:2564:1", "15:2564:2", "15:2564:3",
    "15:2565:1", "15:2565:3",
    "15:2566:0",
)
TRANSLATIONS = {
    "15:2548:0": "에 의한",
    "15:2548:1": "등",
    "15:2548:2": "개 성에 대한",
    "15:2548:3": "을(를) 저지",
    "15:2549:0": (
        "에 보급할 군량이 없으면\n"
        "우리 가문의 원정도 어려워집니다"
    ),
    "15:2549:1": "\n해적중에게서 쌀을 빌리",
    "15:2549:2": "시겠습니까?",
    "15:2550:0": (
        "보급 거점에 군량이 없으면\n"
        "우리 가문의 원정도 어려워집니다"
    ),
    "15:2550:1": "\n해적중에게서 쌀을 빌리",
    "15:2550:2": "시겠습니까?",
    "15:2551:0": "이",
    "15:2551:1": "의 보급 군량을 보충",
    "15:2552:0": "이",
    "15:2552:1": "등",
    "15:2552:2": "개 성의 보급 군량을 보충",
    "15:2553:0": "보급 거점인",
    "15:2553:1": "에\n쌀을 운반해 두었습니다",
    "15:2553:2": "!\n이제 원정군도 군량 걱정은 없을 것입니다",
    "15:2554:0": "보급 거점",
    "15:2554:1": "개 성에 쌀을 운반해 두었습니다",
    "15:2554:2": (
        "!\n이만큼 비축했으니,\n"
        "원정군도 군량 걱정은 없을 것입니다"
    ),
    "15:2554:3": "!",
    "15:2555:0": "! 훌륭한 활약입니다",
    "15:2555:1": "!\n",
    "15:2555:2": "이라 불리는 자에게\n",
    "15:2555:3": "도 식은 죽 먹기였겠지요",
    "15:2555:4": "!",
    "15:2556:0": "잘해 주었구나",
    "15:2556:1": "!\u3000",
    "15:2556:2": "!\n이 활약이야말로,\n",
    "15:2556:3": "이라 불리는 까닭이지",
    "15:2556:4": "!",
    "15:2557:0": "! 견줄 데 없는 활약이구나",
    "15:2557:1": "!\n",
    "15:2557:2": "인",
    "15:2557:3": "이",
    "15:2557:4": "라고 하니,\n감장을 몇 장 써도 모자라겠구나",
    "15:2557:5": "!",
    "15:2558:0": "장하구나,",
    "15:2558:1": "!\n우리 가문을 구하는 이는 역시",
    "15:2558:2": "!\n참으로,",
    "15:2558:3": "의 이름에 부끄럽지 않은 활약이로다",
    "15:2558:4": "……",
    "15:2559:0": "잘해 주었구나",
    "15:2559:1": "!\u3000",
    "15:2559:2": "!\n이",
    "15:2559:3": "이 우리를 지키는 한,\n우리 가문이 쇠할 일은 없다",
    "15:2559:4": "!",
    "15:2560:0": "우리 가문으로서는,",
    "15:2560:1": (
        "의 대병력은 위협입니다……\n"
        "언젠가 닥칠 침공에 대비해,\n전선의"
    ),
    "15:2560:2": "을 방위 거점으로 정하는 것이 어떻겠습니까?",
    "15:2561:0": (
        "우리 가문의 영토는 넓어 휴대 군량만으로 원정하기 "
        "어렵습니다……\n원정군이 군량을 보충할 수 있도록\n"
        "전선에 가까운"
    ),
    "15:2561:1": "을 보급 거점으로 삼는 것이 어떻겠습니까?",
    "15:2562:0": (
        "은 너무나 강대합니다……\n"
        "큰 대가가 필요할 것입니다"
    ),
    "15:2562:1": (
        "만\n이럴 때는 철병을 교섭하는 것도 방법일 듯합니다"
    ),
    "15:2563:0": "과의 약속을 충족하는 군이\n",
    "15:2563:1": "의 관할에 있는 듯합니다",
    "15:2563:2": "\n그 군을 맡기시겠습니까",
    "15:2563:3": "?",
    "15:2564:0": "과의 약속을 충족하는 군이\n",
    "15:2564:1": "에 있는 듯합니다",
    "15:2564:2": "\n군단을 옮겨 그 군을 맡기시겠습니까",
    "15:2564:3": "?",
    "15:2565:1": "성",
    "15:2565:3": "성은 우리 가문이 거느리고 있습니다",
    "15:2566:0": (
        "지방 통일에 필요한 성을 동맹 세력이\n"
        "제압하고 있다면 외교 관계를\n해소한 뒤 공략해야 합니다"
    ),
}
TARGET_RECORD_IDS = tuple(range(2548, 2567))
EXPECTED_ARITY = {
    2548: 4, 2549: 3, 2550: 3, 2551: 2, 2552: 3,
    2553: 3, 2554: 4, 2555: 5, 2556: 5, 2557: 6,
    2558: 5, 2559: 5, 2560: 3, 2561: 2, 2562: 2,
    2563: 4, 2564: 4, 2565: 4, 2566: 1,
}
PREFILL_COMPANION_COORDINATES = ("15:2565:0",)
PREFILL_COMPANION_DONOR = {"15:2565:0": "15:1530:0"}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:2565:2",)
SEMANTIC_BASE_CONTEXT = {
    2548: ("13:80:0",),
    **{
        record_id: ("6:1886:0",)
        for record_id in range(2549, 2555)
    },
    **{
        record_id: ("9:841:0",)
        for record_id in range(2555, 2560)
    },
    2560: ("14:107:3",),
    2561: ("13:316:0",),
    2562: ("15:2224:0",),
    2563: ("6:3098:0",),
    2564: ("6:3098:0",),
    2565: ("15:1530:0", "15:1530:1", "15:1530:3"),
    2566: ("15:1531:0",),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2548: ((), ("025032", "026432", "0232", "023C")),
    2549: ((1126, 1066), ("026432",)),
    2550: ((1126, 1066), ()),
    2551: ((), ("024633", "026432")),
    2552: ((), ("024633", "026432", "0232")),
    2553: ((544, 508, 610, 730), ("026432",)),
    2554: ((538, 508, 610, 730), ("0232",)),
    2555: ((508, 1042, 736), ("024735", "02474E", "023C")),
    2556: ((538, 1042, 736), ("024735", "02474E")),
    2557: ((1042, 8, 184, 760, 718), ("024735", "02474E")),
    2558: ((8, 1042, 736, 1042), ("024735", "02474E")),
    2559: ((538, 778, 730), ("024735", "02474E")),
    2560: ((), ("025032", "026432")),
    2561: ((), ("026432",)),
    2562: ((610,), ("025032",)),
    2563: ((604, 1096), ("024833", "026432")),
    2564: ((604, 1096), ("024833", "025A32")),
    2565: ((568, 1090), ("023C", "0232", "0233")),
    2566: ((82,), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1406,
    queue_start=0,
    queue_stop=67,
    slice_first="15:2548:0",
    slice_last="15:2566:0",
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
        8, 82, 184, 508, 538, 544, 568, 604, 610, 718, 730,
        736, 760, 778, 1042, 1066, 1090, 1096, 1126,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2508, 2567)
    ),
    speaker_style=(
        (2548, "system_multi_castle_action_prevention"),
        (2549, "formal_single_base_supply_proposal"),
        (2550, "formal_multi_base_supply_proposal"),
        (2551, "system_single_base_supply_replenishment"),
        (2552, "system_multi_base_supply_replenishment"),
        (2553, "confident_single_base_supply_report"),
        (2554, "confident_multi_base_supply_report"),
        (2555, "formal_title_based_praise"),
        (2556, "lordly_title_based_praise"),
        (2557, "lordly_peerless_service_praise"),
        (2558, "lordly_clan_saving_service_praise"),
        (2559, "lordly_clan_guardian_praise"),
        (2560, "formal_defensive_base_proposal"),
        (2561, "formal_supply_base_proposal"),
        (2562, "formal_withdrawal_negotiation_counsel"),
        (2563, "formal_county_assignment_proposal"),
        (2564, "formal_legion_transfer_proposal"),
        (2565, "system_regional_unification_progress"),
        (2566, "system_regional_unification_alliance_guidance"),
    ),
    terminology_policy=(
        ("castle", "성"),
        ("supplies", "군량"),
        ("campaign", "원정"),
        ("pirate coteries", "해적중"),
        ("resupply base", "보급 거점"),
        ("commendation", "감장"),
        ("our clan", "우리 가문"),
        ("defensive base", "방위 거점"),
        ("carried provisions", "휴대 군량"),
        ("withdrawal", "철병"),
        ("county", "군"),
        ("legion", "군단"),
        ("regional unification", "지방 통일"),
        ("allied clan", "동맹 세력"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B134 queue "
        "coordinates and its one approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context; the "
        "completed Base corpus supplies only independent semantic references "
        "for provisions, praise, defensive planning, withdrawal, county "
        "assignment and regional unification, while no Base runtime, VM "
        "state or complete-record translation is inherited because none of "
        "the nineteen PK records has a raw, literal or operand-masked Base "
        "match; castles, provisions, campaigns, pirate coteries, resupply "
        "bases, commendations, our clan, defensive bases, carried provisions, "
        "withdrawal, counties, legions, regional unification and allied "
        "clans retain established historical project wording and system, "
        "formal, confident or lordly registers; calls, inline castle, person, "
        "force, title, action and count tokens, protected outer whitespace, "
        "newlines, particles, punctuation, one hidden newline, one exact "
        "prefill companion, terminators, complete record arity, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1407 and S1408 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=42,
    pins={
        "expected_queue_universe_sha256":
        "BDF36DC6AA15A71B145A66EE3EE96918E276D9863BDDAEB4B914B07C158854B1",
        "expected_queue_slice_sha256":
        "CB590AAC2BF4DA67AFEDE19C51688FA5D287F0AEB2DCFB10E65F66C9EDDD9B0E",
        "expected_prefilled_coordinate_sha256":
        "22661B2AAFF813901C6257889C609FEDE8CCE68F5640BB8A9BEAA26F684DE18B",
        "expected_prefill_slice_context_sha256":
        "E8F58B44A8D09FC6F3A6168BA0B70F4E0373DD077F9EC0473547B3F98348B298",
        "expected_target_coordinate_sha256":
        "70BA7E389E122F236EF1C9710C12639445D1B1EC5E73DEEE2F76CB78E2E7CC63",
        "expected_source_target_sha256":
        "7DDDA8ED73FF3370844CA765F0ED0CC0AFE43B26F6331D1E6B050A526A28D02B",
        "expected_current_target_sha256":
        "A9CE0A135FF0F90BB9C4F852BFDF43793DA9F4D2CE1A07856B65970773441279",
        "expected_context_corpus_sha256":
        "B7B9D81CF50637BE6BAE84055CD49869C9178D900D93BB4A6970C10B3599C5B1",
        "expected_gap_contract_sha256":
        "2E169097F5D54B1B175C7C64EE4D393F0E94D97C45B8E0AA6DC1AED9B520D93E",
        "expected_boundary_sha256":
        "4196563D415F7F417BBDB2B02C1971D53E873BB0BB59E2535E6A398E83A5B55D",
        "expected_runtime_control_sha256":
        "76244B581084EDF745BB0D7F5CEB21D9789C357D4862E6500CD0B7DAECEE1D81",
        "expected_base_search_sha256":
        "0230102E69A89E0722696F50B4245DE2DF6799EBE67B0A32BE9A2EE5A48016EB",
        "expected_complete_assembly_sha256":
        "363FF0CE273CF8F57C84529E7B80A7D1612909D57D06BB7BA417E583075C83EC",
        "expected_call_graph_sha256":
        "68F521A9EBAD7E0981D1510AC89F8F45B68E8A5EC029BC047BE95F2BB914DCAF",
        "expected_speaker_style_sha256":
        "8141B696B832DF038262558A5562535061FE5A4689FA5F90089F18245D90F803",
        "expected_terminology_policy_sha256":
        "8B4D35C948B78B644D1F5D686613230F4745FB4DE078A64C3BB5E98812D84863",
        "expected_translation_policy_sha256":
        "979533E8F997A99D31D7F627DD001B3E2251726EBDB9F91540CACA9408470366",
        "expected_candidate_sha256":
        "C4F67492DA27904DA3DD5AD1887861DB54D8187EAA6B4B76A18A6AA6B1A55B5D",
        "expected_combined_slice_candidate_sha256":
        "C4F67492DA27904DA3DD5AD1887861DB54D8187EAA6B4B76A18A6AA6B1A55B5D",
        "expected_combined_changed_literal_count": 42,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B134_S1406",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1406.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1407.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1408.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B134",
    "queue_row_count": 73,
    "queue_visible_count": 200,
    "queue_first": "15:2548:0",
    "queue_last": "16:19:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
