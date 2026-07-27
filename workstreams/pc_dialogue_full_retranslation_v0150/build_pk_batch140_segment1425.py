#!/usr/bin/env python3
"""Build source-redacted PK B140 segment 1425 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:465:0", "17:465:1", "17:466:0", "17:467:0",
    "17:467:1", "17:467:2", "17:468:0", "17:468:1",
    "17:468:2", "17:469:0", "17:469:1", "17:469:2",
    "17:470:0", "17:470:1", "17:471:0", "17:471:1",
    "17:471:2", "17:472:0", "17:472:1", "17:472:2",
    "17:473:0", "17:473:1", "17:473:2", "17:474:0",
    "17:474:1", "17:475:0", "17:476:0", "17:476:1",
    "17:477:0", "17:477:1", "17:478:0", "17:479:0",
    "17:479:1", "17:480:0", "17:480:1", "17:481:0",
    "17:482:0", "17:482:1", "17:483:0", "17:483:1",
    "17:484:0", "17:485:0", "17:485:1", "17:486:0",
    "17:486:1", "17:487:0", "17:488:0", "17:488:1",
    "17:489:0", "17:489:1", "17:489:2", "17:490:0",
    "17:491:0", "17:492:0", "17:493:0", "17:494:0",
    "17:495:0", "17:496:0", "17:497:0", "17:497:1",
    "17:498:0", "17:498:1", "17:499:0", "17:500:0",
    "17:501:0", "17:501:1", "17:501:2",
)
TRANSLATIONS = {
    "17:465:0": "아군 부대를 잃지 않고 목표 3개를 달성하라",
    "17:465:1": " 실패",
    "17:466:0": "아군 부대를 잃지 않고 목표 3개를 달성하라",
    "17:467:0": "요충지 총",
    "17:467:1": "4곳을 제압하라 (",
    "17:467:2": "/4)",
    "17:468:0": "요충지 총",
    "17:468:1": "4곳을 제압하라",
    "17:468:2": " 성공",
    "17:469:0": "요충지 총",
    "17:469:1": "4곳을 제압하라",
    "17:469:2": " 실패",
    "17:470:0": "요충지 총",
    "17:470:1": "4곳을 제압하라",
    "17:471:0": "적군 총",
    "17:471:1": "4개 부대를 격파하라 (",
    "17:471:2": "/4)",
    "17:472:0": "적군 총",
    "17:472:1": "4개 부대를 격파하라",
    "17:472:2": " 성공",
    "17:473:0": "적군 총",
    "17:473:1": "4개 부대를 격파하라",
    "17:473:2": " 실패",
    "17:474:0": "적군 총",
    "17:474:1": "4개 부대를 격파하라",
    "17:475:0": "부대를 격파하라",
    "17:476:0": "부대를 격파하라",
    "17:476:1": " 성공",
    "17:477:0": "부대를 격파하라",
    "17:477:1": " 실패",
    "17:478:0": "부대를 격파하라",
    "17:479:0": "부대를 격파하라",
    "17:479:1": " 성공",
    "17:480:0": "부대를 격파하라",
    "17:480:1": " 실패",
    "17:481:0": "부대를 격파하라",
    "17:482:0": "부대를 격파하라",
    "17:482:1": " 성공",
    "17:483:0": "부대를 격파하라",
    "17:483:1": " 실패",
    "17:484:0": "부대를 격파하라",
    "17:485:0": "부대를 격파하라",
    "17:485:1": " 성공",
    "17:486:0": "부대를 격파하라",
    "17:486:1": " 실패",
    "17:487:0": "주군과 함께 싸우고 명예를 지키며 죽는다…\n후회는 조금도 없다",
    "17:488:0": "아아…",
    "17:488:1": "주군… 저도 곧 가겠습니다\n황천 앞에서 잠시만 기다려 주십시오…",
    "17:489:0": "여기까지인가…\n미안하다",
    "17:489:1": ", 지부",
    "17:489:2": "… 네게 승리를 안겨 주지 못했구나…",
    "17:490:0": "…\n마지막까지 따라 줘서 고맙다",
    "17:491:0": "!\n너 때문에 히데요리 님이 슬퍼하실 것이다!",
    "17:492:0": "…\n이곳에서는 무사로서 일어설 수밖에 없다!",
    "17:493:0": "가능하다면 귀하와는 싸우고 싶지 않았소…",
    "17:494:0": "…\n이곳은 전장, 싸우는 것이 운명이다…",
    "17:495:0": "네놈 때문에 내 아내가 죽게 됐다!",
    "17:496:0": "이 싸움에서 이기기 위해 어쩔 수 없는 일이었다…",
    "17:497:0": "! 나는 네가 싫다!\n",
    "17:497:1": "님을 위해 네 목을 받아 가겠다!",
    "17:498:0": "!",
    "17:498:1": "따위의 편에 서다니\n도요토미의 은혜를 잊었나!",
    "17:499:0": "님… 도요토미의 세상은 곧 끝난다\n어째서 그렇게까지 매달리는가",
    "17:500:0": "…\n네 부대의 철포대는 아직 더 강해질 수 있다",
    "17:501:0": "!　",
    "17:501:1": "히데요리",
    "17:501:2": "공을 현혹하는 간신이여!\n천하태평을 위해 포박하라!",
}
TARGET_RECORD_IDS = tuple(range(465, 502))
EXPECTED_ARITY = {
    465: 2, 466: 1, 467: 3, 468: 3, 469: 3, 470: 2,
    471: 3, 472: 3, 473: 3, 474: 2, 475: 1, 476: 2,
    477: 2, 478: 1, 479: 2, 480: 2, 481: 1, 482: 2,
    483: 2, 484: 1, 485: 2, 486: 2, 487: 1, 488: 2,
    489: 3, 490: 1, 491: 1, 492: 1, 493: 1, 494: 1,
    495: 1, 496: 1, 497: 2, 498: 2, 499: 1, 500: 1,
    501: 3,
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    record_id: ("9:400:0", "9:401:0", "8:465:0")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    467: ((), ("0232",)),
    471: ((), ("0232",)),
    487: ((), ("024734",)),
    488: ((), ("024734",)),
    490: ((), ("024735",)),
    491: ((), ("024735",)),
    492: ((), ("024735",)),
    494: ((), ("024735",)),
    497: ((), ("024735", "024835")),
    498: ((), ("024735", "024835")),
    499: ((), ("024735",)),
    500: ((), ("024735",)),
    501: ((), ("024733",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1425, queue_start=67, queue_stop=134,
    slice_first="17:465:0", slice_last="17:501:2",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(), prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple((17, i) for i in range(437, 534)),
    speaker_style=tuple(
        (i, "historical_event_or_objective_text")
        for i in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Jibu", "지부"),
        ("Hideyori", "히데요리"),
        ("key point", "요충지"),
        ("enemy unit", "적군 부대"),
        ("firearm unit", "철포대"),
        ("Yomi", "황천"),
        ("project long ellipsis", "…"),
    ),
    basis=(
        "all sixty-seven visible B140 middle-slice coordinates form thirty-"
        "seven complete records and are manually reviewed against pristine "
        "PK JP and available PK EN SC TC context; completed Base objective, "
        "battle and defeat rows provide semantic register context only; "
        "objective counters use consistent Korean command and ASCII counter "
        "punctuation without violating protected outer whitespace, while the "
        "Jibu defeat line is reassembled with the validated no-outer-space "
        "fragment pattern; names, titles, dynamic tokens, controls, "
        "protected whitespace, line breaks, complete arity, pins, reverse "
        "overlays, tamper rejection, outside-scope identity, optional "
        "neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=19,
    pins={
        "expected_queue_universe_sha256": "46AC009F2442000B77B8824FDBBB676398B300A99602408336C2C6021E105D13",
        "expected_queue_slice_sha256": "C60AA243861AB023D6A99A6A35031D5FC17630C3355AEB5890A56DA77A28C379",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "C60AA243861AB023D6A99A6A35031D5FC17630C3355AEB5890A56DA77A28C379",
        "expected_source_target_sha256": "7916682BF9D2446CC21F1A06ADB8892FEBFDFC52F83CBCE8D7EA794A6D0F17A9",
        "expected_current_target_sha256": "DC4F2B1E17D2319DE4FE090E7F51332CF2A60F2B5CB30BFE591055574B0B3472",
        "expected_context_corpus_sha256": "89E1A9C78704BA431F3E6FD4BAB11F6EA787C631BC35BC474D081F79EE23DBB2",
        "expected_gap_contract_sha256": "5B7DC4C7CDD0C5A0FAC91864830AE7468A1274B2EE945443BB376044D8F39CAA",
        "expected_boundary_sha256": "512AED12D9259E78353ACBE1540481EAA72D0EA7891F7091E6B582EB05D49F29",
        "expected_runtime_control_sha256": "F78D81E3A34A9E876A6E5CD3BB5021897ACCFE243B203254EA6F8C52527E5597",
        "expected_base_search_sha256": "99DB2F74F6929CFF90347796BDB9832BBBCD7839B1BB9C109716F9BAD1351C27",
        "expected_complete_assembly_sha256": "E1E43D3E8A5D9629ADA5C7E8F0B0874B2D78B179B7C0FA1BE639A94EA5AE3088",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "6F2648C96C26D9A20D880C316C5F93F8F7A78C41FF6C3E7A9C8B0819DCB158B4",
        "expected_terminology_policy_sha256": "8C9B50BEA6F5EA599B8D4C0A766654E7E86DD0B71B0A63B7668021E849C8A059",
        "expected_translation_policy_sha256": "4A18B9F49244103CADD00C525492F25AB3071C7E377CF4BD05E199C10897EE00",
        "expected_candidate_sha256": "757B8139195C1B435F5C501F1DF484C5E37BE0CCDE20FACDEDEAC58A50ED926A",
        "expected_combined_slice_candidate_sha256": "757B8139195C1B435F5C501F1DF484C5E37BE0CCDE20FACDEDEAC58A50ED926A",
        "expected_combined_changed_literal_count": 19,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B140_S1425",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B140_S1425.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B140_S1424.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B140_S1426.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B140", "queue_row_count": 97,
    "queue_visible_count": 200, "queue_first": "17:437:0",
    "queue_last": "17:533:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
