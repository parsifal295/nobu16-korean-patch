#!/usr/bin/env python3
"""Build source-redacted PK B134 segment 1407 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:2567:0",
    "15:2567:2",
    "15:2567:4",
    "15:2568:0",
    "15:2569:0",
    "15:2569:2",
    "15:2569:4",
    "15:2570:1",
    "15:2571:3",
    "15:2572:2",
    "15:2573:0",
    "15:2573:1",
    "15:2573:2",
    "15:2573:3",
    "15:2573:4",
    "15:2574:0",
    "15:2574:1",
    "15:2574:2",
    "15:2575:0",
    "15:2575:1",
    "15:2575:2",
    "15:2576:0",
    "15:2577:0",
    "15:2577:1",
    "15:2578:0",
    "15:2578:1",
    "15:2578:2",
    "15:2579:0",
    "15:2579:1",
    "15:2580:0",
    "15:2581:1",
    "15:2582:0",
    "15:2582:1",
    "15:2582:3",
    "15:2583:0",
    "15:2583:1",
    "15:2583:3",
    "15:2583:4",
    "15:2584:0",
    "15:2584:1",
    "15:2584:3",
    "15:2584:4",
    "15:2585:1",
    "15:2585:2",
    "15:2585:3",
    "15:2586:0",
    "15:2586:1",
    "15:2586:2",
    "15:2586:3",
    "15:2587:0",
    "15:2587:1",
    "15:2587:2",
    "15:2587:3",
    "15:2587:4",
    "15:2587:5",
)
TRANSLATIONS = {
    "15:2567:0": "기나이는 모두 우리 가문의 지배하에 있",
    "15:2567:2": "성",
    "15:2567:4": "성은 우리 가문의 지배하에 있",
    "15:2568:0": (
        "천하 평정에 필요한 성을 동맹 세력이\n"
        "차지하고 있다면 외교 관계를\n"
        "해소하고 공격해 빼앗아야 합니다"
    ),
    "15:2569:0": "전국의 과반수가 우리 가문을 따르고 있",
    "15:2569:2": "성",
    "15:2569:4": "성은 우리 가문의 지배하에 있",
    "15:2570:1": "성",
    "15:2571:3": "성",
    "15:2572:2": "성",
    "15:2573:0": ", 아뢸 말씀이 있습니다",
    "15:2573:1": "\n지금이야말로",
    "15:2573:2": "와(과) 자웅을 겨룰 때입니다\n부디",
    "15:2573:3": "결단해 주십시오",
    "15:2573:4": "!",
    "15:2574:0": "!\n",
    "15:2574:1": "을(를) 무너뜨리고\n천하를 거머쥡시다",
    "15:2574:2": "!",
    "15:2575:0": "뭐라, 결전을 걸어왔다고?\n",
    "15:2575:1": (
        "을(를) 멸하면 우리 천하가 눈앞이다……\n"
        "받아들이지 않겠는"
    ),
    "15:2575:2": "가!",
    "15:2576:0": (
        "을(를) 멸하면 우리 천하가 눈앞이다……\n"
        "모두 단단히 각오하고\n"
        "서둘러 싸울 채비를 갖춰라!"
    ),
    "15:2577:0": "은(는) 결전 제의를 받아들였습니다",
    "15:2577:1": "\n약정한 날이 오면\n마침내 결전의 때입니다",
    "15:2578:0": "의 움직임을 보면\n먼저",
    "15:2578:1": "을(를) 노릴 것입니다",
    "15:2578:2": (
        "\n방비를 단단히 해 적의 습격에 대비합시다"
    ),
    "15:2579:0": (
        "한편 우리도 적의 전선 성을 제압해\n"
        "결전의 발판으로 삼아야겠습니다\n"
        "목표로 삼을 성은 어디입니까"
    ),
    "15:2579:1": "?",
    "15:2580:0": "목표로 삼을 성을 선택하십시오",
    "15:2581:1": "을(를) 함락시켜\n적의 기세를 꺾겠습니다",
    "15:2582:0": "결전일은 앞으로",
    "15:2582:1": "일 후입니다",
    "15:2582:3": (
        "의 방비를 굳히면서\n"
        "결전에 대비해 충분한 전력을 갖춥시다"
    ),
    "15:2583:0": "결전일까지 앞으로",
    "15:2583:1": "일",
    "15:2583:3": "의 방비를 굳히면서\n",
    "15:2583:4": "와(과)의 결전에 대비합시다",
    "15:2584:0": "약정한 때가 왔습니다",
    "15:2584:1": "\n전군, 군비는 완벽합니까",
    "15:2584:3": "와(과)의 결전으로 향합시다",
    "15:2584:4": "!",
    "15:2585:1": "을(를) 제압한다!\n",
    "15:2585:2": "께 길보를 전하겠습니다",
    "15:2585:3": "!",
    "15:2586:0": "역시 왔군",
    "15:2586:1": "!\n결전지로 향하게 둘 수는 없다",
    "15:2586:2": (
        "\n무슨 수를 써서라도 여기서 발을 묶겠다"
    ),
    "15:2586:3": "!",
    "15:2587:0": "좋아,",
    "15:2587:1": "을(를) 제압했다",
    "15:2587:2": "!\n",
    "15:2587:3": "은(는) 이제 결전지로 향한다",
    "15:2587:4": "\n여력이 있는 자는 뒤따르",
    "15:2587:5": "라!",
}
TARGET_RECORD_IDS = tuple(range(2567, 2588))
EXPECTED_ARITY = {
    2567: 5,
    2568: 1,
    2569: 5,
    2570: 4,
    2571: 4,
    2572: 4,
    2573: 5,
    2574: 3,
    2575: 3,
    2576: 1,
    2577: 2,
    2578: 3,
    2579: 2,
    2580: 1,
    2581: 2,
    2582: 4,
    2583: 5,
    2584: 5,
    2585: 4,
    2586: 4,
    2587: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2567:1",
    "15:2569:1",
    "15:2570:0",
    "15:2570:3",
    "15:2571:0",
    "15:2571:1",
    "15:2571:2",
    "15:2572:0",
    "15:2572:1",
    "15:2572:3",
    "15:2581:0",
    "15:2585:0",
)
PREFILL_COMPANION_DONOR = {
    "15:2567:1": "15:1532:1",
    "15:2569:1": "15:1534:1",
    "15:2570:0": "15:1535:0",
    "15:2570:3": "15:1535:3",
    "15:2571:0": "15:1536:0",
    "15:2571:1": "15:1536:1",
    "15:2571:2": "15:1536:2",
    "15:2572:0": "15:1537:0",
    "15:2572:1": "15:1537:1",
    "15:2572:3": "15:1537:3",
    "15:2581:0": "6:2851:0",
    "15:2585:0": "6:4052:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2567:3",
    "15:2569:3",
    "15:2570:2",
    "15:2582:2",
    "15:2583:2",
    "15:2584:2",
)
EXACT_BASE_DONOR = {
    2571: (15, 1536),
    2572: (15, 1537),
}
SEMANTIC_BASE_CONTEXT = {
    2567: ("15:1532:0", "15:1532:1", "15:1532:2", "15:1532:4"),
    2568: ("6:1682:0",),
    2569: ("15:1534:0", "15:1534:1", "15:1534:2", "15:1534:4"),
    2570: ("15:1535:0", "15:1535:1", "15:1535:3"),
    2571: (),
    2572: (),
    2573: ("2:555:0", "6:2632:0"),
    2574: ("2:555:0",),
    2575: ("2:555:0", "2:257:0"),
    2576: ("2:257:0", "6:4031:0"),
    2577: ("6:2178:0",),
    2578: ("16:33:0", "16:33:1"),
    2579: ("7:1605:0",),
    2580: ("6:4021:0",),
    2581: ("6:2851:0",),
    2582: ("2:257:0", "6:2178:0"),
    2583: ("2:257:0", "6:2178:0"),
    2584: ("2:257:0", "6:2178:0"),
    2585: ("6:4052:0", "15:2196:0"),
    2586: ("2:555:0",),
    2587: ("2:555:0",),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    2570: ((15, 1535),),
    2571: ((15, 1536),),
    2572: ((15, 1537),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2567: ((1090, 568, 1090), ("0232", "0233")),
    2568: ((82,), ()),
    2569: ((1090, 568, 1090), ("0232", "0233")),
    2570: ((568, 1090), ("0232", "0233")),
    2571: ((82, 568), ("0232", "0233")),
    2572: ((1090, 568, 394), ("0232",)),
    2573: ((8, 82, 1174, 412), ("025032",)),
    2574: ((862, 1126, 514), ("025032",)),
    2575: ((754,), ("025032",)),
    2576: ((), ("024834",)),
    2577: ((538, 604), ("025032",)),
    2578: ((568, 1066), ("025032", "026432")),
    2579: ((700, 466), ()),
    2580: ((322,), ()),
    2581: ((1126, 514), ("026432",)),
    2582: ((550, 1066), ("0232", "026432")),
    2583: ((550, 1066), ("0232", "026432", "025032")),
    2584: ((244, 844, 190, 514), ("025032",)),
    2585: ((29, 1132), ("026432",)),
    2586: ((538, 298, 1132), ()),
    2587: ((1132, 1, 190, 340), ("026432",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1407,
    queue_start=67,
    queue_stop=134,
    slice_first="15:2567:0",
    slice_last="15:2587:5",
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
        1090, 568, 82, 394, 8, 1174, 412, 862, 1126,
        514, 754, 538, 604, 1066, 700, 466, 322, 550,
        244, 844, 190, 29, 1132, 298, 1, 340,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2525, 2601)
    ),
    speaker_style=(
        (2567, "formal_unification_progress_report"),
        (2568, "concise_unification_alliance_warning"),
        (2569, "formal_unification_progress_report"),
        (2570, "formal_total_castle_progress_report"),
        (2571, "formal_dual_unification_progress_report"),
        (2572, "formal_capital_progress_report"),
        (2573, "formal_decisive_battle_proposal"),
        (2574, "bold_decisive_battle_acceptance"),
        (2575, "rough_decisive_battle_acceptance"),
        (2576, "rough_war_preparation_command"),
        (2577, "formal_challenge_acceptance_report"),
        (2578, "formal_enemy_attack_forecast"),
        (2579, "formal_frontline_castle_proposal"),
        (2580, "concise_castle_selection_prompt"),
        (2581, "formal_castle_capture_acceptance"),
        (2582, "formal_decisive_battle_countdown"),
        (2583, "formal_decisive_battle_countdown"),
        (2584, "formal_decisive_battle_march"),
        (2585, "bold_castle_capture_command"),
        (2586, "rough_enemy_interception"),
        (2587, "rough_decisive_battle_march"),
    ),
    terminology_policy=(
        ("capital region", "기나이"),
        ("unification of the realm", "천하 평정"),
        ("our house", "우리 가문"),
        ("decisive battle", "결전"),
        ("contest for supremacy", "자웅을 겨루다"),
        ("agreement", "약정, 약조"),
        ("battle preparations", "싸울 채비, 군비"),
        ("enemy attack", "적의 습격"),
        ("foothold", "발판"),
        ("good news", "길보"),
        ("dynamic particles", "은(는), 을(를), 와(과)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B134 review-queue coordinates at "
        "zero-based ordinals sixty-seven through one hundred thirty-three "
        "and the approved Base prefill; invisible newline-only targets are "
        "excluded from queue indexing but retained as hidden current "
        "companions in complete record assembly; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context; two "
        "source-identical progress records reuse approved completed Base "
        "Korean assemblies, while one source-identical record containing a "
        "hidden newline and the PK-specific unification and decisive-battle "
        "records use completed Base rows only as semantic and glossary "
        "context and never inherit Base runtime or VM state; the capital "
        "region, unification of the realm, our house, decisive battles, "
        "contests for supremacy, agreements, battle preparations, enemy "
        "attacks, footholds and good news retain established historical "
        "project wording and formal, bold, rough or concise registers; "
        "calls, inline force, castle, officer and count tokens, protected "
        "outer whitespace, line breaks, particles, punctuation, ellipses, "
        "terminators, complete record arity, all twelve slice prefills, six "
        "hidden newlines, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=41,
    pins={
        "expected_queue_universe_sha256": (
            "BDF36DC6AA15A71B145A66EE3EE96918E276D9863BDDAEB4B914B07C158854B1"
        ),
        "expected_queue_slice_sha256": (
            "8A37D0641BF99EF6D58AB5C34F2E6AA70DEB582AF3708BA868F7734E358AA5E2"
        ),
        "expected_prefilled_coordinate_sha256": (
            "85B6882BEDD5C4B391757AC6B7C36EC163496B80ABF7723AB6838ECC0A641D45"
        ),
        "expected_prefill_slice_context_sha256": (
            "A173979308FC3E0CC05A9F6C8E45DCEC79530D46298983A527873AC5228D148D"
        ),
        "expected_target_coordinate_sha256": (
            "EA5C1959529ADCA5A1B78D6870DA161B6EDF8B9A57B5FE2C5B05F2C592D74428"
        ),
        "expected_source_target_sha256": (
            "AC84EE04E8691B13144291A44BAF61E67C6DE89E8D8A74299197ABBD2815A8DA"
        ),
        "expected_current_target_sha256": (
            "B16FA0512939D46FA17A20D678C528440D13903E2209F7124D04F9F6EAAABA3D"
        ),
        "expected_context_corpus_sha256": (
            "B7B9D81CF50637BE6BAE84055CD49869C9178D900D93BB4A6970C10B3599C5B1"
        ),
        "expected_gap_contract_sha256": (
            "67A22D4EA9E8BD5C231613677A31A45C416B92260BE54B7A605DC48A4B4D3778"
        ),
        "expected_boundary_sha256": (
            "704ECBDF4F3D47E3E0CC16C9A373A2A4E1472E2FDAD12D28C049F6F5E2396126"
        ),
        "expected_runtime_control_sha256": (
            "2985399AF1E7E853E4014C270B363B40B59895092EB389F4036038F9E454E5A9"
        ),
        "expected_base_search_sha256": (
            "7E2E8A2EF9ECDCD17A9D20AE712D6984ADB37AFC56CA42154DE4EBA1CD856373"
        ),
        "expected_complete_assembly_sha256": (
            "6DF22771B4E01F97C88B58CFCCD84108FF20931F315CA15569C402E4EAAC7D7A"
        ),
        "expected_call_graph_sha256": (
            "795A98E95A44631BA21E51AD074E8449AF30F8EA7303B13A3ED0B9F1776C2B6E"
        ),
        "expected_speaker_style_sha256": (
            "92E5DB1322E97C398BC77EDD243B155FA19E9D29727230567F0B3636E6BDE6C6"
        ),
        "expected_terminology_policy_sha256": (
            "2504BC1B9F42CA4C54390B32522DCA08C510F28F3A0FD9DA7B19A57385ACF8DD"
        ),
        "expected_translation_policy_sha256": (
            "120E0DA02EF12C6D8DD4A758E4C754C8EC858E7160C2725A04E93987BC012AEE"
        ),
        "expected_candidate_sha256": (
            "836E2009A5DDFD3C264169DC6C3D5EC14B08F32C63BED1D5EB5C465117B23589"
        ),
        "expected_combined_slice_candidate_sha256": (
            "5FD43CAAB99CACE2A660A5B16C476376547CE466668768D3AFDFA9205CB2F436"
        ),
        "expected_combined_changed_literal_count": 45,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B134_S1407",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1407.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B134_S1406.private.v1.jsonl",
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
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
