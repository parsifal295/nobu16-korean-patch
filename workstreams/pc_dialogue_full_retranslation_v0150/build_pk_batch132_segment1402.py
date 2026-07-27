#!/usr/bin/env python3
"""Build source-redacted PK B132 segment 1402 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2451:1",
    "15:2453:0",
    "15:2453:1",
    "15:2453:2",
    "15:2454:0",
    "15:2454:1",
    "15:2455:0",
    "15:2455:1",
    "15:2456:0",
    "15:2456:1",
    "15:2456:2",
    "15:2457:0",
    "15:2457:1",
    "15:2457:2",
    "15:2458:0",
    "15:2458:1",
    "15:2459:0",
    "15:2459:1",
    "15:2460:0",
    "15:2460:1",
    "15:2461:0",
    "15:2461:1",
    "15:2461:2",
    "15:2462:0",
    "15:2462:1",
    "15:2462:2",
    "15:2463:0",
    "15:2464:0",
    "15:2464:1",
    "15:2465:0",
    "15:2465:1",
    "15:2466:0",
    "15:2466:1",
    "15:2467:0",
    "15:2467:1",
    "15:2468:0",
    "15:2468:1",
    "15:2468:2",
    "15:2469:0",
    "15:2469:1",
    "15:2469:2",
    "15:2469:3",
    "15:2470:0",
    "15:2470:1",
    "15:2470:2",
    "15:2470:3",
    "15:2471:0",
    "15:2471:1",
    "15:2472:0",
    "15:2472:1",
    "15:2472:2",
    "15:2473:0",
    "15:2473:1",
    "15:2473:2",
    "15:2473:3",
    "15:2474:0",
    "15:2474:1",
    "15:2474:2",
    "15:2474:3",
)
TRANSLATIONS = {
    "15:2451:1": "에게\n",
    "15:2453:0": "출진한 모든 병력이\n",
    "15:2453:1": "성하에 집결했습니다",
    "15:2453:2": "\n이제 총공격에 나서시지요",
    "15:2454:0": "지금이야말로",
    "15:2454:1": (
        "에 총공격을 감행할 때입니다\n"
        "이만한 군세가 모였으니\n"
        "함락하지 못할 성은 없습니다"
    ),
    "15:2455:0": "을(를) 공략할 군량이\n곧 바닥날 것입니다",
    "15:2455:1": "\n총공격할지 철수할지 부디 결단을 내려 주십시오",
    "15:2456:0": "우리 가문에 불만을 품은 무장이 있습니다",
    "15:2456:1": (
        "……\n지금까지의 공적을 감장으로 치하한다면\n"
        "충성심도 높아질 것으로 사료됩니다"
    ),
    "15:2456:2": "만",
    "15:2457:0": "공적이 탁월한 자가 있습니다",
    "15:2457:1": "!\n부디 그동안의 활약을\n감장으로 치하해 주시지",
    "15:2457:2": "않겠습니까?",
    "15:2458:0": "우리 가문도 오랫동안 싸워 왔습니다",
    "15:2458:1": (
        "\n이제 공이 큰 자들을\n"
        "감장으로 치하해 주시면 좋겠습니다……"
    ),
    "15:2459:0": "을(를) 종속시키시겠습니까",
    "15:2459:1": (
        "?\n그 가문을 비호하는 대신 당주로 하여금\n"
        "가재로서 우리 가문을 보필하게 하시지요"
    ),
    "15:2460:0": "을(를) 종속시키시겠습니까",
    "15:2460:1": (
        "?\n지금 우리 가문의 기세라면\n"
        "병사를 쓰지 않고도 복속시킬 수 있습니다"
    ),
    "15:2461:0": "예전과는 정세가 달라져\n",
    "15:2461:1": (
        "도 더는 최전선이라 할 수 없습니다\n"
        "방위 전념을 해제하시겠습니까"
    ),
    "15:2461:2": "?",
    "15:2462:0": "은(는) 더는 최전선이 아니며\n공격받을 우려도 적습니다",
    "15:2462:1": "\n방위 전념을 해제하시겠습니까",
    "15:2462:2": "?",
    "15:2463:0": (
        "은(는) 바로 우리 가문의 요충지입니다……\n"
        "결코 빼앗기지 않도록\n"
        "가문의 힘을 모아 방비를 굳히시겠습니까?"
    ),
    "15:2464:0": "우리 가문 방위의 요지가 될 곳은\n",
    "15:2464:1": "\n그 성을 방위에 전념시키는 건 어떻겠습니까?",
    "15:2465:0": (
        "전쟁에서 긴요한 것은 군량을 끊기지 않게 하는 일입니다\n"
    ),
    "15:2465:1": (
        "에 군량을 넉넉히 비축해\n"
        "다른 성의 보급에 전념시키는 건 어떻겠습니까?"
    ),
    "15:2466:0": "원정에는 많은 군량이 반드시 필요합니다……\n",
    "15:2466:1": (
        "에 군량을 넉넉히 비축해\n"
        "다른 성의 보급에 전념시키는 건 어떻겠습니까?"
    ),
    "15:2467:0": "평정중을 임명하는 건 어떻겠습니까",
    "15:2467:1": (
        "\n가문의 방침을 정하고 가중의 결속을 다지려면\n"
        "평정중의 역할이 긴요합니다"
    ),
    "15:2468:0": "시장이 우리 가문의 비호 아래 들도록\n",
    "15:2468:1": "일대를 두루 설득하고 싶습니다\n",
    "15:2468:2": "은(는) 상인들과 친분이 많기 때문입니다……",
    "15:2469:0": "상인들을 두루 설득하여\n",
    "15:2469:1": "일대에서",
    "15:2469:2": "곳의 시장을\n장악하고 돌아왔습니다",
    "15:2469:3": "!",
    "15:2470:0": "상인들을 두루 설득하여\n",
    "15:2470:1": "에서",
    "15:2470:2": "곳의 시장을\n장악하고 돌아왔습니다",
    "15:2470:3": "!",
    "15:2471:0": "개 성에서 시장을 장악해 상업이 총",
    "15:2471:1": "증가했습니다",
    "15:2472:0": "일대의 민심을 달래는 일을\n",
    "15:2472:1": "에게 맡겨 주시겠습니까",
    "15:2472:2": "?\n백성의 마음속은 누구보다 잘 알고 있습니다",
    "15:2473:0": "마을을 두루 찾아다니며\n",
    "15:2473:1": "일대에서",
    "15:2473:2": "곳의 농촌을\n장악하고 돌아왔습니다",
    "15:2473:3": "!",
    "15:2474:0": "마을을 두루 찾아다니며\n",
    "15:2474:1": "에서",
    "15:2474:2": "곳의 농촌을\n장악하고 돌아왔습니다",
    "15:2474:3": "!",
}
TARGET_RECORD_IDS = (2451, *range(2453, 2475))
EXPECTED_ARITY = {
    2451: 3,
    2453: 3,
    2454: 2,
    2455: 2,
    2456: 3,
    2457: 3,
    2458: 2,
    2459: 2,
    2460: 2,
    2461: 3,
    2462: 3,
    2463: 1,
    2464: 2,
    2465: 2,
    2466: 2,
    2467: 2,
    2468: 3,
    2469: 4,
    2470: 4,
    2471: 2,
    2472: 3,
    2473: 4,
    2474: 4,
}
PREFILL_COMPANION_COORDINATES = ("15:2451:0", "15:2451:2")
PREFILL_COMPANION_DONOR = {
    "15:2451:0": "15:2420:0",
    "15:2451:2": "15:2420:2",
}
EXACT_BASE_DONOR = {2451: (15, 2420)}
SEMANTIC_BASE_CONTEXT = {
    2451: (),
    2453: ("7:1440:0", "7:1449:0", "9:2933:0"),
    2454: ("7:1440:0", "7:1449:0", "9:2933:0"),
    2455: ("7:1440:0", "7:1449:0", "9:2933:0"),
    2456: ("6:3500:0", "6:3503:0", "9:1900:0"),
    2457: ("6:3487:1", "6:3503:0", "9:1900:0"),
    2458: ("6:3500:0", "6:3503:0", "9:1900:0"),
    2459: ("6:4655:0", "6:4656:1"),
    2460: ("2:484:0", "6:4656:1"),
    2461: ("6:3271:1", "6:3772:0"),
    2462: ("6:3271:1", "6:3772:0"),
    2463: ("6:417:0", "6:3298:0"),
    2464: ("6:417:0", "6:3298:0"),
    2465: ("6:1886:0",),
    2466: ("6:1886:0",),
    2467: ("6:700:0", "6:708:0", "6:714:0"),
    2468: ("6:4120:2",),
    2469: ("6:4120:2",),
    2470: ("6:4120:2",),
    2471: ("6:4120:2",),
    2472: ("8:341:1", "8:708:0", "8:709:0"),
    2473: ("6:4119:2",),
    2474: ("6:4119:2",),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    2451: ((15, 2420),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2451: ((1174, 700, 610), ("025132",)),
    2453: ((634, 1126), ("026432",)),
    2454: ((742,), ("026432",)),
    2455: ((190,), ("026432",)),
    2456: ((178, 226), ()),
    2457: ((178, 730, 322), ()),
    2458: ((628,), ()),
    2459: ((748,), ("025032",)),
    2460: ((748, 1066), ("025032",)),
    2461: ((748,), ("026432",)),
    2462: ((610, 748), ("026432",)),
    2463: ((), ("026432",)),
    2464: ((556,), ("02643201432C020000",)),
    2465: ((), ("026432",)),
    2466: ((), ("026432",)),
    2467: ((700, 610, 562), ()),
    2468: ((1,), ("026432",)),
    2469: ((628,), ("026432", "0232")),
    2470: ((628,), ("026432", "0232")),
    2471: ((), ("0232", "0233")),
    2472: ((1, 352, 1090), ("026432",)),
    2473: ((628,), ("026432", "0232")),
    2474: ((628,), ("026432", "0232")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1402,
    queue_start=134,
    queue_stop=200,
    slice_first="15:2450:0",
    slice_last="15:2474:3",
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
        1, 178, 190, 226, 322, 352, 556, 562, 610, 628, 634,
        700, 730, 742, 748, 1066, 1090, 1126, 1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2396, 2485)
    ),
    speaker_style=(
        (2451, "formal_ally_reinforcement_request"),
        (2453, "formal_total_assault_proposal"),
        (2454, "confident_total_assault_proposal"),
        (2455, "urgent_assault_or_withdrawal_counsel"),
        (2456, "formal_discontented_officer_merit_award"),
        (2457, "formal_distinguished_officer_merit_award"),
        (2458, "formal_housewide_merit_award"),
        (2459, "formal_subordination_and_house_steward_proposal"),
        (2460, "confident_bloodless_subordination_proposal"),
        (2461, "formal_defense_focus_release"),
        (2462, "formal_low_risk_defense_focus_release"),
        (2463, "solemn_strategic_castle_defense"),
        (2464, "formal_defense_cornerstone_proposal"),
        (2465, "formal_provisions_supply_focus"),
        (2466, "formal_expedition_provisions_supply_focus"),
        (2467, "formal_council_appointment_proposal"),
        (2468, "confident_market_persuasion_request"),
        (2469, "formal_surrounding_market_control_report"),
        (2470, "formal_castle_market_control_report"),
        (2471, "system_market_commerce_growth_report"),
        (2472, "confident_popular_sentiment_pacification_request"),
        (2473, "formal_surrounding_village_control_report"),
        (2474, "formal_castle_village_control_report"),
    ),
    terminology_policy=(
        ("all-out assault", "총공격"),
        ("letter of commendation", "감장"),
        ("subordination", "종속, 복속"),
        ("house steward", "가재"),
        ("defense focus", "방위 전념"),
        ("strategic position", "요충지"),
        ("provisions", "군량"),
        ("council", "평정중"),
        ("household", "가중"),
        ("market", "시장"),
        ("rural village", "농촌"),
        ("popular sentiment", "민심"),
        ("dynamic particles", "을(를)\u00b7은(는)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B132 queue coordinates one hundred thirty-four "
        "through one hundred ninety-nine and the approved Base prefill; "
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary context; the "
        "ally reinforcement fragment reuses the approved completed Base "
        "Korean assembly selected by literal and operand-masked source "
        "identity, while the remaining PK-only records are translated "
        "manually from the full multilingual context; Base runtime and VM "
        "state are never inherited; total assaults, letters of commendation, "
        "subordination, house stewards, defense focus, strategic positions, "
        "provisions, councils, household affairs, markets, rural villages "
        "and popular sentiment retain established historical project "
        "wording and each formal, urgent, confident, solemn or system "
        "register; calls, inline officer, house, castle, count and commerce "
        "tokens, opaque control sequences, protected outer whitespace, line "
        "breaks, particles, punctuation, ellipses, terminators, complete "
        "record arity, all seven slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=48,
    pins={
        "expected_queue_universe_sha256": "4B81A2B81F0E8C254EBA4771F9E0DCDF4F57F82DF74DE0B5E0E61D99D11263A4",
        "expected_queue_slice_sha256": "15BF20BD224C17374B600863A26F6B10DFAC4AC08E5A3FF942AAD9CB192B5621",
        "expected_prefilled_coordinate_sha256": "91A069CFC2EA8AF25098AE8A3224C2A68F4B775D250E354B53474A9C6A02F7D9",
        "expected_prefill_slice_context_sha256": "0BEC5CEAEE800D1AA7680467ED9BD027BE1A783B44B673798A30E741A415B461",
        "expected_target_coordinate_sha256": "C44E8D8574680E75A06FFB36E5D00FC03CA9DB3543B95CDECD6C1329EC7508E8",
        "expected_source_target_sha256": "740CA519F9BC4631628C85C2DF5798467285ACA77A70FE0B5CF280F671B7EC20",
        "expected_current_target_sha256": "90C35E16C0613753B451552F217315DF92875E55FA2FE135CE27AD55D224A392",
        "expected_context_corpus_sha256": "8D8785D2CB13D6EEC821599ACD953FE03E89249059B0051AEA785D3BD2C6F60B",
        "expected_gap_contract_sha256": "9DECE5132EA6C51CC0E0074A96EEDF428C6220E81CA6AAB6A406C61FEC6ED646",
        "expected_boundary_sha256": "A73642037B18201746D0F3D8DE63F536C458F7C0C0ACDDE9948BCAAA4CA4B5CF",
        "expected_runtime_control_sha256": "BD72E594DE159D18D74F4A81EEA7DC56547B455C3D63E5EDBB1457B0FEE43344",
        "expected_base_search_sha256": "1C3AD9ADD7E440CC7A8BE090165787919EA0AD171C0EC1DEE0CDE55588ED0EEA",
        "expected_complete_assembly_sha256": "E7FF08A7AB3051924386D950B853824CA33E65D84F73A1887BF93411780484F1",
        "expected_call_graph_sha256": "AFB676A3BFC9092676DE24FCB36E1FBAE37E8CFAB559D892502525FCFBF7AC1B",
        "expected_speaker_style_sha256": "DAB8668D2B8C9EE7B69FE6850485C553F04564BE837E09F5E149587642A3A18C",
        "expected_terminology_policy_sha256": "591B073D0B02FDA4EA6C6FA65A7BB5DA880506D9EDEC73A074A2A5F8015A5DC2",
        "expected_translation_policy_sha256": "963A2C4A68D827E99B908A52BF3DB8D4E50AA68B769ECE61F37671C0A2824B9F",
        "expected_candidate_sha256": "588B6A6A946D0073E8C03DCA2D6F88ECCE2567A94DA231371A1A889AF2F1E1FE",
        "expected_combined_slice_candidate_sha256": "415B484CAE04F40D8EB5DECFB89CEA20314FC6FC60936E2970214111E17CB5FD",
        "expected_combined_changed_literal_count": 55,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B132_S1402",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1402.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1400.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B132_S1401.private.v1.jsonl",
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
