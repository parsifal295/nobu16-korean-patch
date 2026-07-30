#!/usr/bin/env python3
"""Build source-redacted PK B133 segment 1403 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2475:0", "15:2475:1",
    "15:2476:0", "15:2476:1",
    "15:2477:0", "15:2477:1", "15:2477:2", "15:2477:3",
    "15:2478:0", "15:2478:1", "15:2478:2",
    "15:2479:0", "15:2479:1", "15:2479:2",
    "15:2480:0", "15:2480:1",
    "15:2481:0", "15:2481:1", "15:2481:2",
    "15:2482:0", "15:2482:1",
    "15:2483:0", "15:2483:1", "15:2483:2",
    "15:2484:0", "15:2484:1",
    "15:2485:0", "15:2485:2",
    "15:2486:0", "15:2486:1",
    "15:2487:0", "15:2487:1", "15:2487:2",
    "15:2488:0",
    "15:2489:0", "15:2489:1",
    "15:2490:0", "15:2490:1", "15:2490:2",
    "15:2491:0", "15:2491:1",
    "15:2492:0", "15:2492:1", "15:2492:2",
    "15:2493:0", "15:2493:1",
    "15:2494:0", "15:2494:1", "15:2494:2",
    "15:2495:0", "15:2495:1", "15:2495:2", "15:2495:3",
    "15:2496:0", "15:2496:1", "15:2496:2",
    "15:2497:0", "15:2497:1", "15:2497:2", "15:2497:3",
    "15:2497:4",
    "15:2498:0",
    "15:2499:0", "15:2499:1",
    "15:2500:0",
    "15:2501:0", "15:2501:1",
)
TRANSLATIONS = {
    "15:2475:0": "성에서 농촌을 장악하여 석고가 총",
    "15:2475:1": "증가",
    "15:2476:0": (
        "우리 무사의 소임은 영지를 지키는 것!\n"
        "지금이야말로 나라 안의 토착 무사들에게 호소해\n"
        "병사로 소집해 오겠습니다"
    ),
    "15:2476:1": "!",
    "15:2477:0": "나라 안의 토착 무사들에게 협력을 청해,\n",
    "15:2477:1": "등",
    "15:2477:2": "개 성의 병력을\n늘리고 왔습니다",
    "15:2477:3": "!",
    "15:2478:0": "이 토착 무사들을 소집하여,\n",
    "15:2478:1": "등",
    "15:2478:2": "개 성의 병력을\n크게 늘렸다고 합니다",
    "15:2479:0": "나라 안의 토착 무사들에게 협력을 청해,\n",
    "15:2479:1": "의 병력을\n늘리고 왔습니다",
    "15:2479:2": "!",
    "15:2480:0": "이 토착 무사들을 소집하여,\n",
    "15:2480:1": "의 병력을\n크게 늘렸다고 합니다",
    "15:2481:0": "등",
    "15:2481:1": "개 성에서 총",
    "15:2481:2": "만큼 병력 증가",
    "15:2482:0": "에서",
    "15:2482:1": "만큼 병력 증가",
    "15:2483:0": "의",
    "15:2483:1": "등",
    "15:2483:2": "개 성의 병력 증가",
    "15:2484:0": "의",
    "15:2484:1": "에서 병력 증가",
    "15:2485:0": "등에서는 쌀이 부족합니다",
    "15:2485:2": "이 휘하 관리들과 함께\n영내에 남는 쌀을 징수해 오겠습니다",
    "15:2486:0": "등",
    "15:2486:1": "개 성에서\n군량미를 조달해 왔습니다",
    "15:2487:0": "이 영내에서 쌀을 조달하여,\n",
    "15:2487:1": "등",
    "15:2487:2": "개 성에\n군량을 비축했다고 합니다",
    "15:2488:0": "에서\n군량미를 조달해 왔습니다",
    "15:2489:0": "이 영내에서 쌀을 조달하여,\n",
    "15:2489:1": "에\n군량을 비축했다고 합니다",
    "15:2490:0": "등",
    "15:2490:1": "개 성에서 총",
    "15:2490:2": "만큼 군량 회복",
    "15:2491:0": "에서",
    "15:2491:1": "만큼 군량 회복",
    "15:2492:0": "의",
    "15:2492:1": "등",
    "15:2492:2": "개 성의 군량 회복",
    "15:2493:0": "의",
    "15:2493:1": "에서 군량 회복",
    "15:2494:0": "은 패전으로 동요하고 있습니다",
    "15:2494:1": "\n설득에는 자신 있으니,",
    "15:2494:2": "이\n항복하도록 설득하고 오겠습니다",
    "15:2495:0": "지난 패전에 동요했는지,\n",
    "15:2495:1": "에서는 성주",
    "15:2495:2": "가\n",
    "15:2495:3": "에게 항복하기로 결정한 모양입니다!",
    "15:2496:0": "에서는 성주",
    "15:2496:1": "이\n우리에게 항복하기로 결정했습니다",
    "15:2496:2": "!\n이로써 싸우지 않고 성을 얻을 수 있습니다",
    "15:2497:0": "에 항복을 권유했습니다",
    "15:2497:1": "만\n성주",
    "15:2497:2": "은 이를 거절했습니다",
    "15:2497:3": "……\n이렇게 된 이상 공격해 빼앗을 수밖에",
    "15:2497:4": "없습니다!",
    "15:2498:0": "의 개성 교섭에 성공",
    "15:2499:0": "에 의해",
    "15:2499:1": "이 돌아섰습니다",
    "15:2500:0": "의 개성 교섭에 실패",
    "15:2501:0": "에 의한",
    "15:2501:1": "의 포섭을 저지",
}
TARGET_RECORD_IDS = tuple(range(2475, 2502))
EXPECTED_ARITY = {
    2475: 2, 2476: 2, 2477: 4, 2478: 3, 2479: 3,
    2480: 2, 2481: 3, 2482: 2, 2483: 3, 2484: 2,
    2485: 3, 2486: 2, 2487: 3, 2488: 1, 2489: 2,
    2490: 3, 2491: 2, 2492: 3, 2493: 2, 2494: 3,
    2495: 4, 2496: 3, 2497: 5, 2498: 1, 2499: 2,
    2500: 1, 2501: 2,
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:2485:1",)
SEMANTIC_BASE_CONTEXT = {
    **{2475: ("14:43:1",)},
    **{
        record_id: ("9:423:0",)
        for record_id in range(2476, 2485)
    },
    **{
        record_id: ("13:316:0",)
        for record_id in range(2485, 2494)
    },
    **{
        record_id: ("6:1591:0",)
        for record_id in (2494, 2495, 2496, 2497, 2498, 2500)
    },
    2499: ("8:248:2",),
    2501: ("13:80:0",),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2475: ((), ("0232", "0233")),
    2476: ((1126,), ()),
    2477: ((628,), ("026432", "0232")),
    2478: ((), ("025032", "026432", "0232")),
    2479: ((628,), ("026432",)),
    2480: ((), ("025032", "026432")),
    2481: ((), ("026432", "0232", "0233")),
    2482: ((), ("026432", "0232")),
    2483: ((), ("025032", "026432", "0232")),
    2484: ((), ("025032", "026432")),
    2485: ((748, 1, 1090), ("026432",)),
    2486: ((628,), ("026432", "0232")),
    2487: ((), ("025032", "026432", "0232")),
    2488: ((628,), ("026432",)),
    2489: ((), ("025032", "026432")),
    2490: ((), ("026432", "0232", "0233")),
    2491: ((), ("026432", "0232")),
    2492: ((), ("025032", "026432", "0232")),
    2493: ((), ("025032", "026432")),
    2494: ((1090, 1, 1126), ("026432",)),
    2495: ((), ("026432", "024833", "025032")),
    2496: ((538, 1096), ("026432", "024833")),
    2497: ((538, 628, 1090), ("026432", "024833")),
    2498: ((), ("026432",)),
    2499: ((), ("025032", "026432")),
    2500: ((), ("026432",)),
    2501: ((), ("025032", "026432")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1403,
    queue_start=0,
    queue_stop=67,
    slice_first="15:2475:0",
    slice_last="15:2501:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1, 538, 628, 748, 1090, 1096, 1126),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2435, 2549)
    ),
    speaker_style=(
        (2475, "system_crop_increase_notice"),
        (2476, "resolute_samurai_mustering_declaration"),
        (2477, "formal_multi_castle_mustering_report"),
        (2478, "formal_enemy_multi_castle_mustering_report"),
        (2479, "formal_single_castle_mustering_report"),
        (2480, "formal_enemy_single_castle_mustering_report"),
        (2481, "system_multi_castle_troop_increase"),
        (2482, "system_single_castle_troop_increase"),
        (2483, "system_force_multi_castle_troop_increase"),
        (2484, "system_force_single_castle_troop_increase"),
        (2485, "formal_rice_requisition_proposal"),
        (2486, "formal_multi_castle_provision_report"),
        (2487, "formal_enemy_multi_castle_provision_report"),
        (2488, "formal_single_castle_provision_report"),
        (2489, "formal_enemy_single_castle_provision_report"),
        (2490, "system_multi_castle_provision_recovery"),
        (2491, "system_single_castle_provision_recovery"),
        (2492, "system_force_multi_castle_provision_recovery"),
        (2493, "system_force_single_castle_provision_recovery"),
        (2494, "confident_surrender_persuasion_proposal"),
        (2495, "excited_enemy_surrender_report"),
        (2496, "excited_castle_surrender_success"),
        (2497, "resolute_surrender_refusal_report"),
        (2498, "system_surrender_negotiation_success"),
        (2499, "system_allegiance_change"),
        (2500, "system_surrender_negotiation_failure"),
        (2501, "system_recruitment_prevention"),
    ),
    terminology_policy=(
        ("rice yield", "석고"),
        ("samurai duty", "무사의 소임"),
        ("domain", "영지"),
        ("rustic samurai", "토착 무사"),
        ("soldiers and troop strength", "병사, 병력"),
        ("castle", "성"),
        ("military rice", "군량미"),
        ("provisions", "군량"),
        ("officials", "관리"),
        ("territory", "영내"),
        ("defeat", "패전"),
        ("surrender", "항복"),
        ("castle lord", "성주"),
        ("surrender negotiation", "개성 교섭"),
        ("recruitment", "포섭"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as all first "
        "sixty-seven visible B133 queue coordinates; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context; the "
        "completed Base corpus was consulted only for established semantic "
        "terminology and no Base runtime, VM state, translation row or "
        "complete-record donor is inherited because none of the twenty-seven "
        "PK records has a raw, literal or operand-masked Base match; rice "
        "yield, domains, rustic samurai, troop strength, castles, military "
        "rice, provisions, officials, territory, defeat, surrender, castle "
        "lords, surrender negotiations and recruitment retain established "
        "historical project wording; calls, inline force, castle, person and "
        "count tokens, protected outer whitespace, newlines, particles, "
        "punctuation, one hidden newline, terminators, complete record arity, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, reciprocal S1404 and S1405 decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=38,
    pins={
        "expected_queue_universe_sha256":
        "A1FCF27A1B837763A4D3B023E5EB2F988DC4BD5C61350EC2AAAA89A92ECA6396",
        "expected_queue_slice_sha256":
        "9E70928F30AFB9E7AEF787945F919783A82D078B69D2C6F10FBB62F21F2539DA",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "9E70928F30AFB9E7AEF787945F919783A82D078B69D2C6F10FBB62F21F2539DA",
        "expected_source_target_sha256":
        "367CE4140780C7E677634C86264BFDF461FC9EA21B63DC4A7DB06E1A02F3F122",
        "expected_current_target_sha256":
        "C719E5F47E3E65A2BCC0810C0A80A039A9DB4008BAB5F5C143617F5A7E236D9C",
        "expected_context_corpus_sha256":
        "074BFBC4DF1748AB72681F9DF929F87C9CD07F07E8C8BC98B45338ED41867311",
        "expected_gap_contract_sha256":
        "A9DC0886C72AFF542A5D25326BCF518958E79F3A7C4EA7A10B03E6837A14A8E4",
        "expected_boundary_sha256":
        "5C68CF6B42605216A7485E326014AB7A571FD3123BFE9220CA739F53825461AE",
        "expected_runtime_control_sha256":
        "63B25622AA3347E96112E109EF25CD4837F10FC2501826237FF304C6FB3BA968",
        "expected_base_search_sha256":
        "538DF6E9715499B0DBA4A119B1F8987FF87C08E0765264E32BD5319F648C1B48",
        "expected_complete_assembly_sha256":
        "45E65001A279698C71E2BEDBA5BE91AC232596FA14C93047FFC7FC72119A13C2",
        "expected_call_graph_sha256":
        "4382B66CA5412C05C999E097651BBEEE6767A32464FE66EE4AB22666C44247F1",
        "expected_speaker_style_sha256":
        "43452046A2F4C4F62B9FC8AC347CC5F0344D4880A2E53F74AAEE05581578238B",
        "expected_terminology_policy_sha256":
        "CB5200E89E8DA01522DD501958026ADC77DAAA6DACD6781FC6DAEC9C100DE581",
        "expected_translation_policy_sha256":
        "44164A7DCEEA78EEF8F112868E3617826B70BC05CE71427B6563B091F23B462D",
        "expected_candidate_sha256":
        "FFAA3456AD81B0AC78B742B8A23321607535D2E3C768EA5144A26AE0715BB6A7",
        "expected_combined_slice_candidate_sha256":
        "FFAA3456AD81B0AC78B742B8A23321607535D2E3C768EA5144A26AE0715BB6A7",
        "expected_combined_changed_literal_count": 38,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B133_S1403",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1403.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1404.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1405.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B133",
    "queue_row_count": 73,
    "queue_visible_count": 197,
    "queue_first": "15:2475:0",
    "queue_last": "15:2547:2",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
