#!/usr/bin/env python3
"""Build source-redacted PK B140 segment 1424 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:437:0", "17:437:1", "17:437:2", "17:437:3", "17:437:4",
    "17:438:0", "17:438:1", "17:439:0", "17:439:1",
    "17:440:0", "17:440:1", "17:440:2", "17:441:0",
    "17:442:0", "17:442:1", "17:442:2",
    "17:443:0", "17:443:1", "17:443:2",
    "17:444:0", "17:444:1", "17:444:2", "17:444:3", "17:444:4",
    "17:445:0", "17:445:1",
    "17:446:0", "17:446:1", "17:446:2",
    "17:446:3", "17:446:4", "17:446:5",
    "17:447:0", "17:448:0", "17:449:0", "17:450:0",
    "17:451:0", "17:452:0", "17:453:0",
    "17:454:0", "17:454:1", "17:455:0",
    "17:456:0", "17:456:1", "17:456:2", "17:456:3",
    "17:457:0", "17:457:1", "17:457:2", "17:458:0",
    "17:459:0", "17:459:1", "17:459:2", "17:459:3",
    "17:460:0", "17:460:1",
    "17:461:0", "17:461:1", "17:461:2",
    "17:462:0", "17:462:1", "17:462:2", "17:462:3",
    "17:463:0", "17:463:1", "17:464:0", "17:464:1",
)

TRANSLATIONS = {
    "17:437:0": "설마 이번 싸움에서",
    "17:437:1": "미쓰나리",
    "17:437:2": "가 이기는가!?\n이대로는",
    "17:437:3": "모리",
    "17:437:4": "가문이…… 서둘러 진군한다!",
    "17:438:0": "히로이에",
    "17:438:1": "가 드디어 움직일 마음이 생겼나\n우리도 진군한다",
    "17:439:0": "모리",
    "17:439:1": "군이 움직였다!\n우리도 뒤처지지 마라!",
    "17:440:0": "우리도 움직이도록 하지\n",
    "17:440:1": "오타니",
    "17:440:2": "님의 지휘는 실로 훌륭했다",
    "17:441:0": "설마 이렇게 될 줄이야……\n우리의 사전 공작도 뒤집혔나……",
    "17:442:0": "남은 적은 ",
    "17:442:1": "이에야스",
    "17:442:2": "뿐이다!\n전군 진격하라!",
    "17:443:0": "절반이 넘는 ",
    "17:443:1": "요충지",
    "17:443:2": "를 빼앗겼나……",
    "17:444:0": "전황이 ",
    "17:444:1": "동군",
    "17:444:2": " 쪽으로 기울기 시작했나……\n우리의 적은 ",
    "17:444:3": "미쓰나리",
    "17:444:4": "이다! 진군하라!",
    "17:445:0": "고바야카와",
    "17:445:1": "가 움직였나! 우리도 호응하자!",
    "17:446:0": "고바야카와",
    "17:446:1": "녀석,",
    "17:446:2": "동군",
    "17:446:3": "의 편에 서다니……\n우리 힘만으로",
    "17:446:4": "이에야스",
    "17:446:5": "를 쓰러뜨릴 수밖에 없다……",
    "17:447:0": "순조롭게 적 부대를 격파하고 있군……\n이대로 계속 공격하라!",
    "17:448:0": "모두 잘했다!\n우리 도요토미의 승리다!",
    "17:449:0": "내 아카조나에도 여기까지인가……",
    "17:450:0": "따위에게 지다니!?\n말도 안 돼…… 말도 안 된다!",
    "17:451:0": "의 본진은 이 앞이다!\n일제히 공격하라!",
    "17:452:0": (
        "군인가…… 이 병력으로는 버틸 수 없다\n"
        "아군 진지로 끌어들여 싸울까……?"
    ),
    "17:453:0": "이토록 몰릴 줄이야……",
    "17:454:0": ", 어찌 이리 강한가……!\n과연",
    "17:454:1": "에게는 과분한 자로군……",
    "17:455:0": (
        "패배인가! 내가 지는 것인가!\n"
        "때를 기다리고 또 기다린 끝이 이것인가!"
    ),
    "17:456:0": "역적",
    "17:456:1": "은 패배하고\n",
    "17:456:2": "히데요리",
    "17:456:3": "공을 해칠 자도 사라졌다!",
    "17:457:0": "모두, 승전 함성을 올려라!\n이제",
    "17:457:1": "도요토미 가문",
    "17:457:2": "의 천하는 지켜질 것이다!",
    "17:458:0": (
        "이토록 패했으니 물러날 길도 없겠지\n"
        "이제 미련 없이 할복하겠다……"
    ),
    "17:459:0": "큰아버님,",
    "17:459:1": "시마즈",
    "17:459:2": "를 위해서라도 물러나십시오!\n대신",
    "17:459:3": "가 스테가마리로 목숨을 바치겠습니다",
    "17:460:0": (
        "……알겠다! 정면의 적을 돌파하고 물러난다!\n"
        "이름을 남길 무공을 세워라,"
    ),
    "17:460:1": "!",
    "17:461:0": "공……　",
    "17:461:1": "태합",
    "17:461:2": "전하……\n면목이 없습니다……",
    "17:462:0": "이에야스",
    "17:462:1": "의 부대를 발견했나!\n전군 전진! ",
    "17:462:2": "이에야스",
    "17:462:3": "의 목을 베어라!",
    "17:463:0": "아군 부대를 괴멸시키지 않고 목표 3개를 달성하라(",
    "17:463:1": "/3)",
    "17:464:0": "아군 부대를 잃지 않고 목표 3개 달성",
    "17:464:1": " 성공",
}

TARGET_RECORD_IDS = tuple(range(437, 465))
EXPECTED_ARITY = {
    437: 5, 438: 2, 439: 2, 440: 3, 441: 1, 442: 3,
    443: 3, 444: 5, 445: 2, 446: 6, 447: 1, 448: 1,
    449: 1, 450: 1, 451: 1, 452: 1, 453: 1, 454: 2,
    455: 1, 456: 4, 457: 3, 458: 1, 459: 4, 460: 2,
    461: 3, 462: 4, 463: 2, 464: 2,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {443, 463, 464}
        else ("9:1006:0",)
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    450: ((), ("024835",)),
    451: ((), ("024835",)),
    452: ((), ("024834",)),
    454: ((), ("024833", "024935")),
    456: ((), ("024833",)),
    459: ((), ("024635",)),
    460: ((), ("024735",)),
    461: ((), ("024735",)),
    463: ((), ("0232",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1424,
    queue_start=0,
    queue_stop=67,
    slice_first="17:437:0",
    slice_last="17:464:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (17, record_id) for record_id in range(400, 505)
    ),
    speaker_style=tuple(
        (record_id, "sekigahara_historical_battle_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Mitsunari", "미쓰나리"),
        ("Mōri", "모리"),
        ("Hiroie", "히로이에"),
        ("Ōtani", "오타니"),
        ("Ieyasu", "이에야스"),
        ("Kobayakawa", "고바야카와"),
        ("Hideyori", "히데요리"),
        ("Toyotomi Clan", "도요토미 가문"),
        ("Shimazu", "시마즈"),
        ("Taikō", "태합"),
        ("Red Cavalry", "아카조나에"),
        ("sutegamari", "스테가마리"),
        ("strategic point", "요충지"),
        ("seppuku", "할복"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B140 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN same-record fragment array "
        "was manually reviewed as auxiliary context, while JP-only "
        "Sekigahara exchanges were reviewed from complete assemblies and "
        "their adjacent historical sequence; completed Base strategic-point "
        "and officer dialogue rows are semantic and terminology references "
        "only because none of the twenty-eight PK records has a raw, literal "
        "or operand-masked Base match; established names, ranks and clan "
        "forms are retained, the Shimazu rear-guard tactic is identified as "
        "sutegamari, and objective, defeat, victory, retreat and last-stand "
        "registers remain distinct; colour tags, inline person, force, role "
        "and location tokens, protected spaces, line breaks, particles, "
        "punctuation, terminators, complete record arity, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1425 and S1426 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=20,
    pins={
        "expected_queue_universe_sha256":
        "46AC009F2442000B77B8824FDBBB676398B300A99602408336C2C6021E105D13",
        "expected_queue_slice_sha256":
        "77F111E36572623940480E0219991366EA6A382EA0895BFB93A5B4F6BF786FD4",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "77F111E36572623940480E0219991366EA6A382EA0895BFB93A5B4F6BF786FD4",
        "expected_source_target_sha256":
        "B5AB3BADF99FB75B0702D115BB2589D79E9B479DE26720F003684D28106F911A",
        "expected_current_target_sha256":
        "FD6A24A0611B4B218AC3DECFBBBFDB9B775BE8A7E2B23EFF6A673E528714A085",
        "expected_context_corpus_sha256":
        "89E1A9C78704BA431F3E6FD4BAB11F6EA787C631BC35BC474D081F79EE23DBB2",
        "expected_gap_contract_sha256":
        "384E8686D099389A4CFC6A5F6757DFAF2AD5CF8F4A260477D20DEDFB86E0F2CF",
        "expected_boundary_sha256":
        "D5E0C65D43E646B6517A6EDCA2EF6DB74E5D4D2F1013FDE965C428A78F69553B",
        "expected_runtime_control_sha256":
        "AC1761FFEDE058E0D953D32AB6EB36D489DDC34F04882684DDCF75C7E7E9CC38",
        "expected_base_search_sha256":
        "FF678DF353CB6711BF0B58D4D512FFB01248BB63185E6516D365E7CF84B765DC",
        "expected_complete_assembly_sha256":
        "70B304CD5100A644B626FD2E927EF35B4CB4FD3A8EF503CFEEB95CDD0F3C8652",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "9FD21C745B9D3FDD03F39C933F7E9365F1C2C7582EDC7FE51B25DECA102653FD",
        "expected_terminology_policy_sha256":
        "278D221EB330E8DF0DFE726C5E5CCEE6CB62304ED7564500D9354F030EA9A970",
        "expected_translation_policy_sha256":
        "6EFA3F51D6A599813E8DB4A4A19452EA6CE35F37700E9D0D3D1D2F6F0D8AD7D8",
        "expected_candidate_sha256":
        "386A855F0CFE9ED1115AC436F86AD45F050A4B7F9A29CE618BE553B9758B7DCE",
        "expected_combined_slice_candidate_sha256":
        "386A855F0CFE9ED1115AC436F86AD45F050A4B7F9A29CE618BE553B9758B7DCE",
        "expected_combined_changed_literal_count": 20,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B140_S1424",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B140_S1424.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B140_S1425.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B140_S1426.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B140",
    "queue_row_count": 97,
    "queue_visible_count": 200,
    "queue_first": "17:437:0",
    "queue_last": "17:533:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
