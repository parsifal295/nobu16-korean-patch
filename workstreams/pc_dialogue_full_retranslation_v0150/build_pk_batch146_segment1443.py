#!/usr/bin/env python3
"""Build source-redacted PK B146 segment 1443 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:1122:0", "17:1123:0", "17:1124:0", "17:1125:0",
    "17:1125:1", "17:1125:2", "17:1126:0", "17:1127:0",
    "17:1127:1", "17:1127:2", "17:1128:0", "17:1129:0",
    "17:1130:0", "17:1131:0", "17:1132:0", "17:1133:0",
    "17:1133:1", "17:1134:0", "17:1135:0", "17:1135:1",
    "17:1135:2", "17:1136:0", "17:1137:0", "17:1138:0",
    "17:1139:0", "17:1140:0", "17:1141:0", "17:1142:0",
    "17:1143:0", "17:1144:0", "17:1144:1", "17:1145:0",
    "17:1146:0", "17:1147:0", "17:1147:1", "17:1147:2",
    "17:1148:0", "17:1149:0", "17:1150:0", "17:1150:1",
    "17:1150:2", "17:1151:0", "17:1152:0", "17:1152:1",
    "17:1153:0", "17:1154:0", "17:1155:0", "17:1156:0",
    "17:1157:0", "17:1157:1",
)

TRANSLATIONS = {
    "17:1122:0": "마지막 울타리마저…!\n큭, 들었던 이야기와 다르잖아…",
    "17:1123:0": "적이 혼란에 빠졌다!\n이 틈에 단숨에 공격하라!",
    "17:1124:0": "아직 울타리조차 넘지 못했는데\n벌써 이렇게 많은 병사가…",
    "17:1125:0": "주군, 이대로는 승산이 없습니다!\n일단 ",
    "17:1125:1": "가이",
    "17:1125:2": "까지 물러나시지요",
    "17:1126:0": "안 된다! 적에게 등을 보일 수는 없다!\n죽어 간 이들에게 면목이 서지 않는다",
    "17:1127:0": "게다가 지금",
    "17:1127:1": "나가시노성",
    "17:1127:2": "이 점령됐으니\n얼마나 거센 추격을 받을지 모릅니다",
    "17:1128:0": "적어도 추격을 망설일 만큼 타격을 줘야\n비로소 물러날 수 있다…!",
    "17:1129:0": "주군…",
    "17:1130:0": "…퇴각한다",
    "17:1131:0": "하, 하지만\n정말 괜찮으시겠습니까?",
    "17:1132:0": "퇴로를 확보하기 위해서라고 하면 된다\n이런 싸움에 목숨을 걸 가치는 없다",
    "17:1133:0": "주군, 아군이 잇달아 전사하고 있습니다\n",
    "17:1133:1": "님도 물러난 듯합니다",
    "17:1134:0": "뭐라고…!\n큭, 이럴 리가…",
    "17:1135:0": "다시 한번 말씀드립니다\n",
    "17:1135:1": "다케다",
    "17:1135:2": "를 위해서라도 여기서는 물러나시지요",
    "17:1136:0": "그렇군…\n미안하다, 내가 잘못했다…",
    "17:1137:0": "그럼 후위는 제게 맡기십시오\n…이것으로 작별입니다!",
    "17:1138:0": "…\n나는, 나는…",
    "17:1139:0": "역시 이 싸움은…\n지금은 일단 물러나자",
    "17:1140:0": "주군께서 물러나실 때까지 제가 상대하겠습니다!\n제 돌격을 받아라!",
    "17:1141:0": "시시하군… 이만큼 판을 깔고\n수적으로 우세하고도 지켜 내지 못하나",
    "17:1142:0": "거기 너, 각 부대에 전하라\n마음껏 싸우라고",
    "17:1143:0": "하지만 철포 외의 대비는 부족하다\n적의 기세도 상당할 것이다",
    "17:1144:0": "…이토록 고전하게 되다니\n과연",
    "17:1144:1": "의 아들… 얕볼 수 없군",
    "17:1145:0": "어리석은 놈… 적에게 낚였군…\n규율을 지키지 않으면 혼란만 생긴다",
    "17:1146:0": "이 내가… 적에게 낚이다니\n이래서는 면목이 서지 않는다…!",
    "17:1147:0": "뭐지…?\n",
    "17:1147:1": "오다",
    "17:1147:2": "군이 혼란에 빠졌나?",
    "17:1148:0": "천재일우의 기회다!\n지금 공격하라!",
    "17:1149:0": "는 놓쳤지만\n훌륭한 전과라 할 수 있겠군",
    "17:1150:0": "저 ",
    "17:1150:1": "다케다",
    "17:1150:2": "군이 이토록 간단히…\n이것이 철포의 힘인가",
    "17:1151:0": "장점을 살리고 단점을 보완한다\n그런 싸움을 해야 비로소 의미가 있지",
    "17:1152:0": "좋아, 이제",
    "17:1152:1": "도 기세가 꺾여\n더는 우리의 적수가 아니다",
    "17:1153:0": "철포의 힘을 너무 믿었던 건가\n아니면 계책이 좋지 않았던 걸까…",
    "17:1154:0": "어느 쪽이든\n이래서도 진다면 쓸모가 없다",
    "17:1155:0": "새로운 전법을 만들어 낼 수 있으리라\n생각했건만…",
    "17:1156:0": "적 6개 부대를 격파하라",
    "17:1157:0": "적 6개 부대를 격파하라(",
    "17:1157:1": "/6)",
}

TARGET_RECORD_IDS = tuple(range(1122, 1158))
EXPECTED_ARITY = {
    1122: 1, 1123: 1, 1124: 1, 1125: 3, 1126: 1, 1127: 3,
    1128: 1, 1129: 1, 1130: 1, 1131: 1, 1132: 1, 1133: 2,
    1134: 1, 1135: 3, 1136: 1, 1137: 1, 1138: 1, 1139: 1,
    1140: 1, 1141: 1, 1142: 1, 1143: 1, 1144: 2, 1145: 1,
    1146: 1, 1147: 3, 1148: 1, 1149: 1, 1150: 3, 1151: 1,
    1152: 2, 1153: 1, 1154: 1, 1155: 1, 1156: 1, 1157: 2,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {1156, 1157}
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
    1133: ((), ("024835",)),
    1138: ((), ("024835",)),
    1144: ((), ("024835",)),
    1149: ((), ("024835",)),
    1152: ((), ("024834",)),
    1157: ((), ("0232",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1443,
    queue_start=67,
    queue_stop=117,
    slice_first="17:1122:0",
    slice_last="17:1157:1",
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
        ("Kai", "가이"),
        ("Nagashino Castle", "나가시노성"),
        ("Takeda", "다케다"),
        ("Oda", "오다"),
        ("arquebus", "철포"),
        ("rearguard", "후위"),
        ("barricade", "울타리"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "final fifty visible B146 queue coordinates because no approved "
        "Base prefill exists in the slice; pristine PK JP is authoritative "
        "and every populated EN, SC and TC same-record fragment array was "
        "manually reviewed as auxiliary context; completed Base objective "
        "and officer dialogue rows are semantic and terminology references "
        "only because none of the thirty-six PK records has a raw, literal "
        "or operand-masked Base match; Kai, Nagashino Castle, Takeda, Oda "
        "and arquebus retain established historical project forms, and "
        "the rearguard term is not confused with a rear army; retreat "
        "debate, sacrificial rearguard vows, tactical disorder, musket "
        "assessment and objectives remain distinct; inline person and "
        "counter tokens, protected spaces, line breaks, particles, "
        "punctuation, terminators, complete record arity, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1442 decision and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=31,
    pins={
        "expected_queue_universe_sha256":
        "A7286743C009FC4868727791BF85EA5E13408C90474A24BBD833B79E8E14F147",
        "expected_queue_slice_sha256":
        "671DFF92057F39F3C9DC23C732DF18D96CB86E6FB14883A1A0525A4C1AB2C81C",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "671DFF92057F39F3C9DC23C732DF18D96CB86E6FB14883A1A0525A4C1AB2C81C",
        "expected_source_target_sha256":
        "7908D7CAA8A0928A4300AF77628427DD3F9CC1C72AFABAB9ABC8363E3EF29F72",
        "expected_current_target_sha256":
        "74CC8DB44E45518B7EBB60EF7B794F00843681667742600FBBDE6E75A77C25F0",
        "expected_context_corpus_sha256":
        "10B887143FFF07BA99AAF184E8C0F099E8FDD5AC56635B7A9C0DB468C34480D0",
        "expected_gap_contract_sha256":
        "E31C9104B6C835F80DAB89C9B66E2444D5AF5C032D4EAC41803F2613CDF0792F",
        "expected_boundary_sha256":
        "4076D392CF22F47694F9D73E6575AD782FF3992FCF5136B596CF855CB6039A27",
        "expected_runtime_control_sha256":
        "26988C61DB3CAF977AC5F36D6ACC4E9DDEC094248F01A673EC0AF67399387158",
        "expected_base_search_sha256":
        "737813A6A7603FC09E0692F610C0DF24D4CA2B9175F1749655DBABDE7C911083",
        "expected_complete_assembly_sha256":
        "12ED7ED6110D7C4FB903356CA57ECA18256FEDEF9434E65B1170937C294F6AD6",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "8621A64FA26D51DDEB224DCB8FB314CB8E7F791126DE9E73ABE10B3E38DB45A1",
        "expected_terminology_policy_sha256":
        "A5BB187D0A9BF3294E4BCA197141343D596A464064276BBAB7C7E055BAA8A3E3",
        "expected_translation_policy_sha256":
        "90080750364CAAF334051417E4A8603B8F8E242B78B02111727195EC677BE80A",
        "expected_candidate_sha256":
        "7AC44C9FDD95177FBB2AF314426076D1F61906E22073B8859179DA3551164F33",
        "expected_combined_slice_candidate_sha256":
        "7AC44C9FDD95177FBB2AF314426076D1F61906E22073B8859179DA3551164F33",
        "expected_combined_changed_literal_count": 31,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B146_S1443",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B146_S1443.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B146_S1442.private.v1.jsonl",
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
