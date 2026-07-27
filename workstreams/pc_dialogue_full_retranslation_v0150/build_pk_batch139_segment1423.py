#!/usr/bin/env python3
"""Build source-redacted PK B139 segment 1423 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = tuple(range(406, 437))
TARGET_COORDINATES = (
    "17:406:0", "17:406:1",
    "17:407:0", "17:407:1",
    "17:408:0", "17:408:1",
    "17:409:0",
    "17:410:0", "17:410:1", "17:410:2",
    "17:411:0", "17:411:1",
    "17:412:0", "17:412:1",
    "17:413:0",
    "17:414:0", "17:414:1", "17:414:2",
    "17:415:0",
    "17:416:0", "17:416:1", "17:416:2",
    "17:417:0", "17:417:1", "17:417:2", "17:417:3",
    "17:418:0", "17:418:1", "17:418:2",
    "17:419:0", "17:419:1",
    "17:420:0", "17:420:1",
    "17:421:0",
    "17:422:0", "17:422:1",
    "17:423:0",
    "17:424:0", "17:424:1", "17:424:2", "17:424:3",
    "17:425:0",
    "17:426:0", "17:426:1",
    "17:427:0",
    "17:428:0", "17:428:1",
    "17:429:0",
    "17:430:0",
    "17:431:0", "17:431:1", "17:431:2",
    "17:432:0",
    "17:433:0", "17:433:1",
    "17:434:0",
    "17:435:0", "17:435:1", "17:435:2", "17:435:3", "17:435:4",
    "17:436:0", "17:436:1", "17:436:2", "17:436:3",
)
TRANSLATIONS = {
    "17:406:0": "모리",
    "17:406:1": (
        "종가가 참전하시는 것이다!\n"
        "약정 따위가 무슨 소용이냐! 어서 산을 내려가라!"
    ),
    "17:407:0": "난구산",
    "17:407:1": "의 아군도 움직이기 시작했군\n참으로 다행이다!",
    "17:408:0": "좋아, 늦지 않았군!\n",
    "17:408:1": "님을 모셔 왔다!",
    "17:409:0": "님!\n여기까지 와 주시다니……",
    "17:410:0": "오는 길에",
    "17:410:1": "에게 들었다……\n나를 해치려는",
    "17:410:2": "를 벌하면 되는 것이지?",
    "17:411:0": "잘 부탁한다!\u3000",
    "17:411:1": "!",
    "17:412:0": "금빛 일색인 깃발……\n설마,",
    "17:412:1": "님께서 여기까지?",
    "17:413:0": "님께 활을 겨눌 수는 없다……!\n우리는 물러나겠다!",
    "17:414:0": "이시다",
    "17:414:1": "측이 우세하다고? 뜻밖이군……\n적은 역적",
    "17:414:2": "이다! 산을 내려가라!",
    "17:415:0": "가 우리 편이 됐나!\n천운이다! 승리가 눈앞이다!",
    "17:416:0": "가 드디어 움직였나!\n우리도",
    "17:416:1": "이에야스",
    "17:416:2": "를 향해 진군한다!",
    "17:417:0": "보아라",
    "17:417:1": "!\u3000",
    "17:417:2": "도쿠가와",
    "17:417:3": "가 지고 있지 않느냐!\n어서 산을 내려가라!",
    "17:418:0": "……신속히 산을 내려가겠습니다\n적어도 총대장의 목을",
    "17:418:1": "모리",
    "17:418:2": "의 전공으로 삼아야 합니다",
    "17:419:0": "모리",
    "17:419:1": "군이 움직였다!\n우리도 뒤처지지 마라!",
    "17:420:0": "제법 훌륭한 지휘였소,",
    "17:420:1": "님\n우리도 돕겠으니 명령을 내려 주시오……",
    "17:421:0": "설마 이렇게 될 줄이야……\n우리의 사전 공작도 뒤집혔나……",
    "17:422:0": "좋다, 남은 것은",
    "17:422:1": "토벌뿐이다!\n전군 전진하라!",
    "17:423:0": "이런……! 아군 부대가……!",
    "17:424:0": "역시 이번 싸움은,",
    "17:424:1": "도쿠가와",
    "17:424:2": "가 이기는가……\n적은 간신",
    "17:424:3": "이다! 산을 내려가라!",
    "17:425:0": "가 움직였나! 우리도 호응하자!",
    "17:426:0": "놈, 역시 배신했나!\n이렇게 된 이상 우리 힘만으로",
    "17:426:1": "를 친다!",
    "17:427:0": "아버님! 늦었습니다만,\n저희 별동대가 도착했습니다!",
    "17:428:0": "늦었다,",
    "17:428:1": "!\n결판에는 늦지 않았다만……",
    "17:429:0": "잘 들어라, 이번 실책을 만회할 공을……\n……전령인가? 무슨 일이냐?",
    "17:430:0": (
        "보고드립니다! 후방에 정체불명의 병마가 있습니다!\n"
        "깃발은 육문전입니다!"
    ),
    "17:431:0": "……",
    "17:431:1": "!\u3000",
    "17:431:2": "다!\n큰일이다, 이래서는 퇴로가……!",
    "17:432:0": "제법 허둥대는구나\n기습으로는 충분했나?",
    "17:433:0": "그저 참전하기만 하면 재미없으니……\n",
    "17:433:1": ", 도착했노라",
    "17:434:0": "요충지의 절반 이상을 제압했다!\n공세를 늦추지 말고 나아가라!",
    "17:435:0": "이번 싸움은",
    "17:435:1": "미쓰나리",
    "17:435:2": "님에게 승산이 있다고 보았다!\n내 적은",
    "17:435:3": "이에야스",
    "17:435:4": "이다! 진군을 시작하라!",
    "17:436:0": "고바야카와",
    "17:436:1": "가 드디어 움직였나!\n우리도 ",
    "17:436:2": "이에야스",
    "17:436:3": "를 향해 진군한다!",
}
EXPECTED_ARITY = {
    406: 2, 407: 2, 408: 2, 409: 1, 410: 3, 411: 2,
    412: 2, 413: 1, 414: 3, 415: 1, 416: 3, 417: 4,
    418: 3, 419: 2, 420: 2, 421: 1, 422: 2, 423: 1,
    424: 4, 425: 1, 426: 2, 427: 1, 428: 2, 429: 1,
    430: 1, 431: 3, 432: 1, 433: 2, 434: 1, 435: 5,
    436: 4,
}
SEMANTIC_BASE_CONTEXT = {
    **{record_id: ("9:3031:0",) for record_id in range(406, 423)},
    **{record_id: ("9:1006:0",) for record_id in range(423, 434)},
    **{record_id: ("9:2842:0",) for record_id in range(434, 437)},
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    408: ((), ("024835",)),
    409: ((), ("024735",)),
    410: ((), ("024935", "024835")),
    411: ((), ("024735",)),
    412: ((), ("024835",)),
    413: ((), ("024835",)),
    414: ((), ("024933",)),
    415: ((), ("024834",)),
    416: ((), ("024835",)),
    417: ((), ("024735",)),
    420: ((), ("024835",)),
    422: ((), ("024835",)),
    424: ((), ("024933",)),
    425: ((), ("024835",)),
    426: ((), ("024835", "024935")),
    428: ((), ("024735",)),
    431: ((), ("024834", "024833")),
    433: ((), ("024633",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1423,
    queue_start=134,
    queue_stop=199,
    slice_first="17:406:0",
    slice_last="17:436:3",
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
    boundary_record_keys=tuple((17, record_id) for record_id in range(370, 470)),
    speaker_style=tuple(
        (record_id, "historical_battle_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Mori main house", "모리 종가"),
        ("Nangusan", "난구산"),
        ("Ishida", "이시다"),
        ("Tokugawa", "도쿠가와"),
        ("military merit", "전공"),
        ("key point", "요충지"),
        ("detachment", "별동대"),
        ("six coins", "육문전"),
        ("all units advance", "전군 전진"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the entire "
        "B139 queue slice from zero-based ordinals one hundred thirty-four "
        "through one hundred ninety-eight because no approved Base prefill "
        "exists in the slice; pristine PK source is authoritative, all "
        "available multilingual same-record fragments were reviewed as "
        "auxiliary context, and records without auxiliary translations were "
        "reviewed from complete assemblies, controls and adjacent historical "
        "battle sequence; completed Base command, battle and objective rows "
        "are semantic and glossary context only and never contribute runtime "
        "or VM state; Mori main-house, Nangusan, Ishida, Tokugawa, military "
        "merit, key-point, detachment, six-coins and advance terminology "
        "retain established project wording; dialogue preserves urgent, "
        "formal, defiant, shocked, relieved, commanding and playful registers; "
        "tags, dynamic tokens, protected whitespace, line breaks, punctuation, "
        "terminators, record arity, pins, reverse overlays, reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor decisions "
        "and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=24,
    pins={
        "expected_queue_universe_sha256": "A72C309D8A6281E8C5B1C2E48BCA08FD8A3A683D0F06420C73EFA7CD28E91E1C",
        "expected_queue_slice_sha256": "9E640637BA83891F61DB42353D2C065AA130D02A412CD1ACA455FF10EB701FE1",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "9E640637BA83891F61DB42353D2C065AA130D02A412CD1ACA455FF10EB701FE1",
        "expected_source_target_sha256": "4A0365818EC69F1C22F7E2EB609B51C4452479907BE9782D20F54B81557C5025",
        "expected_current_target_sha256": "D2298907DA8586EBDFEE1315690AC47743B23A0E37BCA84265C8506AF79944D4",
        "expected_context_corpus_sha256": "5C17DFF0CD513CECC8482150D5D1487892DD8DE26D7BBBB415E17C2259A1ECB1",
        "expected_gap_contract_sha256": "228398F2AD78275D6AF73B196DFBB39DDFBC02D7061357883FE9F48AF2EDDC3D",
        "expected_boundary_sha256": "5053B0FADC5B41A3313ABC862C7922CF32E1AFC83B65F1ADAAF83CB52D2A549A",
        "expected_runtime_control_sha256": "96D96DA8F304B5DBC308B28BBC405D0EF67504C9306D7794CE68AAF336A94BF4",
        "expected_base_search_sha256": "EDCCDDC7E890CF52A8A39D8DECF74951D5FF1CB62400D7003F1C73718855B693",
        "expected_complete_assembly_sha256": "8FE18F8C9B836E3945DAFA81488BAB6D5B4BE1C7B414685AE4F2502E58C16868",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "34611CE595D4A1F072383333DC263DE39F1AFD65E669D547A2F49D835254DD9E",
        "expected_terminology_policy_sha256": "4366461E1592EC3DFEA8380ADBA583C47CD71B821D6A5213ADD69A5AFBF940B6",
        "expected_translation_policy_sha256": "EF1FD42026A379AF0F62A74EFD26E47D6AA0F700B0752BC7E6ABC351DAF1527B",
        "expected_candidate_sha256": "0B6DE855298B85DBA98B6737D608FD822CDBB1B718F01684D6BA719B914A47DE",
        "expected_combined_slice_candidate_sha256": "0B6DE855298B85DBA98B6737D608FD822CDBB1B718F01684D6BA719B914A47DE",
        "expected_combined_changed_literal_count": 24,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B139_S1423",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B139_S1423.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B139_S1421.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B139_S1422.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B139",
    "queue_row_count": 90,
    "queue_visible_count": 199,
    "queue_first": "17:347:0",
    "queue_last": "17:436:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
