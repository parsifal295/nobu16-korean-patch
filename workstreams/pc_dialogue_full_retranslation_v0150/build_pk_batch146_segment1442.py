#!/usr/bin/env python3
"""Build source-redacted PK B146 segment 1442 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:1069:0", "17:1069:1", "17:1069:2", "17:1070:0",
    "17:1070:1", "17:1071:0", "17:1072:0", "17:1073:0",
    "17:1074:0", "17:1075:0", "17:1076:0", "17:1077:0",
    "17:1078:0", "17:1078:1", "17:1078:2", "17:1079:0",
    "17:1081:0", "17:1084:0", "17:1085:0", "17:1086:0",
    "17:1087:0", "17:1088:0", "17:1089:0", "17:1090:0",
    "17:1091:0", "17:1092:0", "17:1093:0", "17:1093:1",
    "17:1094:0", "17:1094:1", "17:1095:0", "17:1095:1",
    "17:1096:0", "17:1097:0", "17:1097:1", "17:1098:0",
    "17:1098:1", "17:1099:0", "17:1100:0", "17:1100:1",
    "17:1101:0", "17:1101:1", "17:1102:0", "17:1103:0",
    "17:1103:1", "17:1104:0", "17:1104:1", "17:1105:0",
    "17:1106:0", "17:1106:1", "17:1107:0", "17:1108:0",
    "17:1109:0", "17:1110:0", "17:1111:0", "17:1112:0",
    "17:1113:0", "17:1113:1", "17:1114:0", "17:1115:0",
    "17:1115:1", "17:1116:0", "17:1117:0", "17:1118:0",
    "17:1119:0", "17:1120:0", "17:1121:0",
)

TRANSLATIONS = {
    "17:1069:0": "……그 이야기는 그만두십시오\n",
    "17:1069:1": "미카타가하라",
    "17:1069:2": "의 광경이 아직도 꿈에 나옵니다",
    "17:1070:0": "그리 심통 부리지 마라\n…그보다,",
    "17:1070:1": "라고 했던가?\n그자에 관해 말이다…",
    "17:1071:0": "그자의 무례한 헌책을 부디 용서하십시오…!\n그런데 어째서 그 계책을 몰래 인정하셨습니까?\n군의에서는 몹시 노하셨는데…",
    "17:1072:0": "그 질책은 연기였다\n그 자리에서 계책을 인정하면 적의 첩자가 알아채고\n역으로 이용할 수도 있었으니",
    "17:1073:0": "의 기습으로 적을 끌어냈다\n그자에게 맡은 바를 훌륭히 해냈다고 전하라\n…자, 철포 준비는 끝났겠지?",
    "17:1074:0": "예, 가능한 만큼 모두 모아\n각 부대에 나눠 준비했습니다",
    "17:1075:0": "좋다. 그럼 출진하자\n철포가 전황을 얼마나 좌우하는지\n이 자리에서 시험해 보겠다",
    "17:1076:0": "여러분, 저것을 보십시오!",
    "17:1077:0": "들판에 성이 세워져 있다…!?\n나아가려면 저곳을 뚫어야 하는가!",
    "17:1078:0": "배후의 ",
    "17:1078:1": "도비가스야마 요새",
    "17:1078:2": "가 기습당한 지금\n우리에게는 물러날 길이 없습니다…",
    "17:1079:0": "물러날 수 없다면 나아갈 수밖에 없겠지…\n어떻게든 이 사지를 벗어나라!",
    "17:1081:0": "주군, 알겠습니다!",
    "17:1084:0": "적은 수적으로 열세다\n그렇다면 반드시 우리 양익을 노릴 것이다",
    "17:1085:0": "양옆을 제압하러 온 적을 울타리까지 끌어들여\n움직임이 둔해진 병사를 노려라",
    "17:1086:0": "울타리 앞으로 나선 자는 벌하겠다!\n알겠나? 그럼 각자 위치로 가라!",
    "17:1087:0": "자…\n철포의 가능성을 찾아내 보이겠다",
    "17:1088:0": "아군은 수적으로 열세입니다\n여기서는 양익부터 무너뜨리는 것이 상책인 듯합니다",
    "17:1089:0": "수가 적다면 학익진이 제격이다\n아버님도 분명 이렇게 하실 것이다!",
    "17:1090:0": "이번 싸움은 학익진으로 간다!\n미하타와 다테나시여, 굽어살피소서!",
    "17:1091:0": "과연 이 싸움에서 이길 수 있을까…\n우선 상황을 지켜보자",
    "17:1092:0": "요충지 앞으로 나가지 말고 적 6개 부대를 격파하라",
    "17:1093:0": "요충지 앞으로 나가지 말고 적 6개 부대를 격파하라(",
    "17:1093:1": "/6)",
    "17:1094:0": "요충지 앞으로 나가지 말고 적 6개 부대를 격파하라",
    "17:1094:1": " 성공",
    "17:1095:0": "요충지 앞으로 나가지 말고 적 6개 부대를 격파하라",
    "17:1095:1": " 실패",
    "17:1096:0": "요충지를 빼앗기지 마라",
    "17:1097:0": "요충지를 빼앗기지 마라",
    "17:1097:1": " 성공",
    "17:1098:0": "요충지를 빼앗기지 마라",
    "17:1098:1": " 실패",
    "17:1099:0": "부대를 격파하라",
    "17:1100:0": "부대를 격파하라",
    "17:1100:1": " 성공",
    "17:1101:0": "부대를 격파하라",
    "17:1101:1": " 실패",
    "17:1102:0": "부대를 격파하라",
    "17:1103:0": "부대를 격파하라",
    "17:1103:1": " 성공",
    "17:1104:0": "부대를 격파하라",
    "17:1104:1": " 실패",
    "17:1105:0": "우리 아카조나에가 선봉을 맡는다!\n울타리가 엉성한 적의 우익을 쳐라!",
    "17:1106:0": "역시 양끝부터 공격하는가!\n저 붉은 갑옷은",
    "17:1106:1": "의 부대다. 각별히 조심하라!",
    "17:1107:0": "뭐… 안 된다!\n울타리에 막혀 앞으로 나아갈 수 없다!",
    "17:1108:0": "말이 멈춰 선 지금이 기회다!\n쉴 새 없이 계속 쏴라!",
    "17:1109:0": "큭, 실수했나…\n울타리를 몇 겹이나 세웠을 줄이야…",
    "17:1110:0": "해, 해냈다!\n저 아카조나에를 격파했다!",
    "17:1111:0": "가 울타리도 넘지 못하고 전사했다고…!?\n말도 안 돼…",
    "17:1112:0": "하지만 이제 와 물러날 수는 없다!\n무슨 수를 써서라도 울타리를 돌파하라!",
    "17:1113:0": "큭, 울타리를 돌파하다니…!\n과연 아카조나에를 이끄는",
    "17:1113:1": "의 부대다!",
    "17:1114:0": "좋다, 이제 잔꾀는 통하지 않는다!\n정정당당히 싸우자!",
    "17:1115:0": "큰일이다, 무슨 수를 써서라도 막아라!\n",
    "17:1115:1": "님을 뵐 면목이 없다!",
    "17:1116:0": "참으로 무서운 것은 철포가 아니라 울타리였군…\n당장 철거에 나서라!",
    "17:1117:0": "역시 울타리를 노려 오는가\n철포를 쏘아 다가오는 적을 격퇴하라!",
    "17:1118:0": "옆으로 흩어지지 말고 한곳을 돌파하라!\n울타리만 부수면 승산이 있다!",
    "17:1119:0": "사격을 집중해 울타리를 지켜라!\n아군 사선에 들어가지 않도록 주의하라!",
    "17:1120:0": "큭, 이래서는 울타리를 부순다 해도…\n분하구나…",
    "17:1121:0": "몰아붙여졌을 때는 초조했지만\n이로써 제1진은 격파했다!",
}

TARGET_RECORD_IDS = (
    1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077,
    1078, 1079, 1081, 1084, 1085, 1086, 1087, 1088, 1089,
    1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098,
    1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107,
    1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116,
    1117, 1118, 1119, 1120, 1121,
)
EXPECTED_ARITY = {
    1069: 3, 1070: 2, 1071: 1, 1072: 1, 1073: 1, 1074: 1,
    1075: 1, 1076: 1, 1077: 1, 1078: 3, 1079: 1, 1081: 1,
    1084: 1, 1085: 1, 1086: 1, 1087: 1, 1088: 1, 1089: 1,
    1090: 1, 1091: 1, 1092: 1, 1093: 2, 1094: 2, 1095: 2,
    1096: 1, 1097: 2, 1098: 2, 1099: 1, 1100: 2, 1101: 2,
    1102: 1, 1103: 2, 1104: 2, 1105: 1, 1106: 2, 1107: 1,
    1108: 1, 1109: 1, 1110: 1, 1111: 1, 1112: 1, 1113: 2,
    1114: 1, 1115: 2, 1116: 1, 1117: 1, 1118: 1, 1119: 1,
    1120: 1, 1121: 1,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {
            1092, 1093, 1094, 1095, 1096, 1097, 1098,
            1099, 1100, 1101, 1102, 1103, 1104,
        }
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
    1070: ((), ("024833",)),
    1073: ((), ("024835",)),
    1093: ((), ("0232",)),
    1106: ((), ("024834",)),
    1111: ((), ("024835",)),
    1113: ((), ("024834",)),
    1115: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1442,
    queue_start=0,
    queue_stop=67,
    slice_first="17:1069:0",
    slice_last="17:1121:0",
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
        (17, record_id) for record_id in range(1034, 1158)
    ),
    speaker_style=tuple(
        (record_id, "nagashino_historical_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Mikatagahara", "미카타가하라"),
        ("Tobigasuyama fortress", "도비가스야마 요새"),
        ("arquebus", "철포"),
        ("crane-wing formation", "학익진"),
        ("Mihata and Tatenashi", "미하타와 다테나시"),
        ("red cavalry", "아카조나에"),
        ("barricade", "울타리"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B146 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context; "
        "completed Base objective and officer dialogue rows are semantic "
        "and terminology references only because none of the fifty PK "
        "records has a raw, literal or operand-masked Base match; "
        "Mikatagahara, Tobigasuyama, arquebuses, crane-wing formation, "
        "Mihata and Tatenashi and the red cavalry retain established "
        "historical project forms; the Japanese text controls divergent "
        "auxiliary descriptions of fortifications and tactics; strategic "
        "deception, field orders, objectives, musket volleys and death "
        "reports remain distinct; inline person and counter tokens, "
        "protected spaces, line breaks, particles, punctuation, "
        "terminators, complete record arity, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "reciprocal S1443 and S1444 decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=37,
    pins={
        "expected_queue_universe_sha256":
        "A7286743C009FC4868727791BF85EA5E13408C90474A24BBD833B79E8E14F147",
        "expected_queue_slice_sha256":
        "E735FF2117DE1086918217C6D783A32685241C6B8DD7F8FFBB01094B9808331C",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "E735FF2117DE1086918217C6D783A32685241C6B8DD7F8FFBB01094B9808331C",
        "expected_source_target_sha256":
        "BAB160E27BB5280A5AF489C51408D1384CEF99D809BE0E9B4FFB41AD6C52BBB1",
        "expected_current_target_sha256":
        "404BD87EB0D549D829B0FC0C265324513119A24597468D127E1A39925E122132",
        "expected_context_corpus_sha256":
        "10B887143FFF07BA99AAF184E8C0F099E8FDD5AC56635B7A9C0DB468C34480D0",
        "expected_gap_contract_sha256":
        "748AF54FF89A0B9EE5E82D7D57FBCF6D5CFB49CB84021DF1F484FD106C6E91BB",
        "expected_boundary_sha256":
        "4076D392CF22F47694F9D73E6575AD782FF3992FCF5136B596CF855CB6039A27",
        "expected_runtime_control_sha256":
        "EAE631DE5D7E4B45DE5028F4B47BFDD7DE9F245527DD712B5BBF83C873E06C17",
        "expected_base_search_sha256":
        "CA31F1B91F1EBDC14D2DF2658DCC7DE569181546D25F1AEA029F9B051DD9AAD6",
        "expected_complete_assembly_sha256":
        "14CBA7AE067FA751D3D6BA0569DA112CFD09A67B93DB0133CDF5EB249F1B9EF8",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "682B6411469284F27B2A25E39E7F8521C9A2157669AB911728138C3D2F53D288",
        "expected_terminology_policy_sha256":
        "B55CF683D6B2DE0AB29195E4C08108FCEBF8CFC6FEFC1D9958105EB02BD3F2CF",
        "expected_translation_policy_sha256":
        "98EECA0DE464917DF3084417C3702C5CF3BD4123454DE8EAFA96E70FCCA7EF51",
        "expected_candidate_sha256":
        "102A3DE2D09EDBFA45D5FEBDDB743E3EE1186D32E291E76AC7F1E0160C0C015C",
        "expected_combined_slice_candidate_sha256":
        "102A3DE2D09EDBFA45D5FEBDDB743E3EE1186D32E291E76AC7F1E0160C0C015C",
        "expected_combined_changed_literal_count": 37,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B146_S1442",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B146_S1442.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B146_S1443.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B146_S1444.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B146",
    "queue_row_count": 90,
    "queue_visible_count": 117,
    "queue_first": "17:1069:0",
    "queue_last": "17:1157:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
