#!/usr/bin/env python3
"""Build source-redacted PK B139 segment 1422 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:380:0", "17:380:1", "17:380:2", "17:381:0",
    "17:381:1", "17:381:2", "17:381:3", "17:382:0",
    "17:382:1", "17:382:2", "17:383:0", "17:384:0",
    "17:385:0", "17:385:1", "17:385:2", "17:386:0",
    "17:386:1", "17:387:0", "17:387:1", "17:388:0",
    "17:388:1", "17:388:2", "17:389:0", "17:389:1",
    "17:390:0", "17:390:1", "17:391:0", "17:392:0",
    "17:392:1", "17:393:0", "17:393:1", "17:393:2",
    "17:394:0", "17:394:1", "17:394:2", "17:394:3",
    "17:394:4", "17:395:0", "17:396:0", "17:397:0",
    "17:398:0", "17:398:1", "17:398:2", "17:398:3",
    "17:398:4", "17:399:0", "17:399:1", "17:399:2",
    "17:400:0", "17:400:1", "17:401:0", "17:401:1",
    "17:401:2", "17:402:0", "17:402:1", "17:402:2",
    "17:402:3", "17:402:4", "17:403:0", "17:403:1",
    "17:403:2", "17:404:0", "17:404:1", "17:404:2",
    "17:405:0", "17:405:1", "17:405:2",
)
TRANSLATIONS = {
    "17:380:0": "여, 역시",
    "17:380:1": "긴고",
    "17:380:2": "는\n배신할 생각인가?",
    "17:381:0": "아마",
    "17:381:1": "님은 우리와",
    "17:381:2": "도쿠가와 측",
    "17:381:3": "을\n저울질하고 계신 듯합니다",
    "17:382:0": "군이 움직인",
    "17:382:1": "마쓰오산",
    "17:382:2": "은\n양군의 측면을 살필 수 있는 절호의 장소입니다",
    "17:383:0": "전황이 우세한 진영을 도와\n승자 편에 붙으려는 속셈이겠지요",
    "17:384:0": "즉, 배신을 막고 이기려면\n조금도 불리해져서는 안 됩니다",
    "17:385:0": "우세를 유지하며 적군을 계속 압도하라고?\n",
    "17:385:1": "교부",
    "17:385:2": "도 없는데 나 혼자서…?",
    "17:386:0": "하지만 할 수밖에 없겠군…\n누구 하나 패주시키지 않고 바로",
    "17:386:1": "를 궁지에 몰겠다!",
    "17:387:0": "오타니",
    "17:387:1": "님도 곧 원군을 이끌고\n도착하실 것입니다",
    "17:388:0": "위축되지 않고 지휘하면 승기가 보일 것입니다\n…자,",
    "17:388:1": "도쿠가와",
    "17:388:2": "의 선봉이 움직입니다!",
    "17:389:0": "선봉장은",
    "17:389:1": "가 차지하겠다!\n용맹한 아카조나에여, 나를 따르라!",
    "17:390:0": "멋대로 선수를 치다니!? 비겁하다!\n",
    "17:390:1": "부대에 뒤처지지 마라!",
    "17:391:0": "…좋아! 모두, 맞서 싸우자!\n먼저 선봉을 격파해 적의 기세를 꺾어라!",
    "17:392:0": "본진의 명령을 전합니다!\n",
    "17:392:1": "부대, 전진해 주십시오! 그럼 이만!",
    "17:393:0": "이",
    "17:393:1": "시마즈",
    "17:393:2": "에게 말에서도 내리지 않고 명령하다니…?\n가신의 가신 주제에 무례하구나!",
    "17:394:0": "애초에,",
    "17:394:1": "이시다 지부",
    "17:394:2": "가 싸움에 대해 무엇을 알겠나?\n",
    "17:394:3": "시마즈",
    "17:394:4": "는 제멋대로 움직이겠다",
    "17:395:0": "! 어서 진군하시오!!\n싸움은 이미 시작됐소!",
    "17:396:0": "진군하지 않겠습니다",
    "17:397:0": "뭐라고…!?",
    "17:398:0": "나를 비롯해,",
    "17:398:1": "모리 가문",
    "17:398:2": "중신은 모두\n",
    "17:398:3": "도쿠가와",
    "17:398:4": "와 불전의 약정을 맺었기 때문입니다",
    "17:399:0": "무슨 짓이냐!　",
    "17:399:1": "모리",
    "17:399:2": "의 대장은 나다!\n그런 이야기는 듣지 못했다!",
    "17:400:0": "주군!　",
    "17:400:1": "님! 다른 부대에서 전령이 왔습니다!\n“싸울 때가 무르익었는데 왜 움직이지 않는가”라고…",
    "17:401:0": "우리는 식사 중이라고 전해라!\n…이번 싸움에서, ",
    "17:401:1": "모리 가문",
    "17:401:2": "은 관망한다!",
    "17:402:0": "좋아, 늦지 않았군!\n",
    "17:402:1": "모리",
    "17:402:2": " 본군을 데려왔다, ",
    "17:402:3": "지부",
    "17:402:4": "!",
    "17:403:0": "나도 각오를 굳혔다!\n",
    "17:403:1": "모리",
    "17:403:2": " 가문이 너희에게 승리를 안겨 주마!",
    "17:404:0": "하하하, ",
    "17:404:1": "오타니 교부",
    "17:404:2": "가 해냈다!\n우리 총대장께서 납신다!",
    "17:405:0": "주, 주군께서 직접 참전하신다고!?\n이래서는 ",
    "17:405:1": "내대신",
    "17:405:2": "님과 맺은 약정이…!",
}
TARGET_RECORD_IDS = tuple(range(380, 406))
EXPECTED_ARITY = {
    380: 3, 381: 4, 382: 3, 383: 1, 384: 1, 385: 3,
    386: 2, 387: 2, 388: 3, 389: 2, 390: 2, 391: 1,
    392: 2, 393: 3, 394: 5, 395: 1, 396: 1, 397: 1,
    398: 5, 399: 3, 400: 2, 401: 3, 402: 5, 403: 3,
    404: 3, 405: 3,
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
    380: ((), ("024735",)),
    381: ((), ("024834",)),
    382: ((), ("024834",)),
    386: ((), ("024835",)),
    389: ((), ("024635",)),
    390: ((), ("024834",)),
    392: ((), ("024834",)),
    395: ((), ("024735",)),
    400: ((), ("024834",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1422, queue_start=67, queue_stop=134,
    slice_first="17:380:0", slice_last="17:405:2",
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
    boundary_record_keys=tuple((17, i) for i in range(347, 437)),
    speaker_style=tuple(
        (i, "historical_sekigahara_dialogue") for i in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Kingo", "긴고"),
        ("Gyōbu", "교부"),
        ("Jibu", "지부"),
        ("Naifu", "내대신"),
        ("Matsuoyama", "마쓰오산"),
        ("Tokugawa", "도쿠가와"),
        ("Shimazu", "시마즈"),
        ("Mōri", "모리"),
        ("red-armored troops", "아카조나에"),
        ("project long ellipsis", "…"),
    ),
    basis=(
        "all sixty-seven visible B139 middle-slice coordinates form twenty-"
        "six complete records and are manually reviewed against pristine PK "
        "JP and available PK EN SC TC context; completed Base battle and "
        "defeat rows provide semantic register context only; the Sekigahara "
        "Kingo defection, Otani reinforcement, Shimazu refusal and Mori "
        "neutrality sequence preserves historical titles and names, while "
        "awkward winning-side, routed-ally, reaction, punctuation and victory "
        "wording are corrected; dynamic tokens, controls, protected outer "
        "whitespace, line breaks, complete arity, pins, reverse overlays, "
        "tamper rejection, outside-scope identity, optional neighbors and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=5,
    pins={
        "expected_queue_universe_sha256": "A72C309D8A6281E8C5B1C2E48BCA08FD8A3A683D0F06420C73EFA7CD28E91E1C",
        "expected_queue_slice_sha256": "558209FF895FE8E4D92EB660DE5D75ED622FF99A3439F477CE16F402E6DCE975",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "558209FF895FE8E4D92EB660DE5D75ED622FF99A3439F477CE16F402E6DCE975",
        "expected_source_target_sha256": "02715B944CE052A78BA0CA0584787EA4B3E5DC8E9FDD01DDCE4D958DCBB1CEA6",
        "expected_current_target_sha256": "DB88C678CEAED55002E0B11303794FEBA2AE327E066AEF685FE7B53EDB4989BF",
        "expected_context_corpus_sha256": "5C17DFF0CD513CECC8482150D5D1487892DD8DE26D7BBBB415E17C2259A1ECB1",
        "expected_gap_contract_sha256": "332AA089CB4EB5805315A2D2B35CE95AF6CE16BAC72A875B4FF3E523C91A1421",
        "expected_boundary_sha256": "DD47E85D9EBA651A7AD065146A1737D924EF0342B749F48BD95C5279FFBBF7BC",
        "expected_runtime_control_sha256": "BABFEFA2B4D0E4947545B26F62F06C484E4CE20E1D689065CDF84F7AAA14E15C",
        "expected_base_search_sha256": "6ED2E56B113549669B503CDB9076722C48AB3D8B3792DCA9023272E900166D7C",
        "expected_complete_assembly_sha256": "B4774739189B596E94D5CF4AF127D753A22E6CB1314FCC5B72A95A0CE13DD3AB",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "462408BDBD7B7B7FF303ADCEE27C3AED0476BEFAD5158A294573348BAB8C8E65",
        "expected_terminology_policy_sha256": "06D36CC22B7FE3DCDFE143BEB0BE3D99093FFC0A872BBCDF7483CBF43B9F75FD",
        "expected_translation_policy_sha256": "1192CC88E63BD41F292BFC02FC658FE3D5124D7639260298497BFEAAA2187854",
        "expected_candidate_sha256": "0CE443F3038A061FCEB42BA1396682070D6C3A0665C1810AF52EBA96782B11FD",
        "expected_combined_slice_candidate_sha256": "0CE443F3038A061FCEB42BA1396682070D6C3A0665C1810AF52EBA96782B11FD",
        "expected_combined_changed_literal_count": 5,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B139_S1422",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B139_S1422.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B139_S1421.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B139_S1423.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B139", "queue_row_count": 90,
    "queue_visible_count": 199, "queue_first": "17:347:0",
    "queue_last": "17:436:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
