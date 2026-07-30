#!/usr/bin/env python3
"""Build source-redacted PK B144 segment 1438 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER

SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = tuple(range(932, 961))
TARGET_COORDINATES = (
    "17:932:0", "17:932:1", "17:932:2", "17:933:0",
    "17:934:0", "17:934:1", "17:934:2", "17:934:3",
    "17:935:0", "17:936:0", "17:936:1", "17:937:0", "17:937:1",
    "17:938:0", "17:939:0", "17:939:1", "17:939:2", "17:940:0",
    "17:941:0", "17:942:0", "17:942:1",
    "17:943:0", "17:943:1", "17:943:2",
    "17:944:0", "17:944:1", "17:944:2",
    "17:945:0", "17:946:0", "17:946:1", "17:946:2",
    "17:947:0", "17:947:1", "17:948:0", "17:949:0",
    "17:950:0", "17:950:1", "17:951:0", "17:951:1", "17:951:2",
    "17:952:0", "17:952:1", "17:952:2", "17:953:0",
    "17:954:0", "17:954:1", "17:955:0", "17:955:1",
    "17:956:0", "17:956:1", "17:956:2",
    "17:957:0", "17:957:1", "17:957:2", "17:957:3",
    "17:958:0", "17:958:1", "17:958:2", "17:958:3",
    "17:959:0", "17:959:1", "17:959:2",
    "17:960:0", "17:960:1", "17:960:2", "17:960:3",
)
TRANSLATIONS = {
    "17:932:0": "내 목숨은 어찌 되어도 좋다……\n하지만 형님은……\u3000",
    "17:932:1": "다케다", "17:932:2": "는 아직 끝날 수 없다!",
    "17:933:0": ", 각오해라!\n목숨을 맞바꾸는 한이 있어도 널 막겠다!",
    "17:934:0": "다케다 덴큐 노부시게", "17:934:1": "……네가",
    "17:934:2": "다케다", "17:934:3": "의 부장인가!\n훌륭한 각오와 기백이다! ……잘 가라!",
    "17:935:0": "……미안하다……!\n네 죽음을 결코 헛되게 하지 않겠다",
    "17:936:0": "죽음을 각오한 병사로 우리 기세를 꺾나……훌륭하다!\n하지만 내 칼날은 반드시",
    "17:936:1": "에게 닿을 것이다",
    "17:937:0": ", ", "17:937:1": "의 죽음을 헛되게 하지 마라!\n무슨 수를 써서라도 버텨라!",
    "17:938:0": "제3진, 앞으로!\n이제 결판이 보이겠군",
    "17:939:0": "적의 ", "17:939:1": "퇴로", "17:939:2": "를 빼앗았다!\n이제 주군을 구할 수 있겠군!",
    "17:940:0": "이대로는 퇴로가 끊기겠군……\n물러날 때다, 퇴각하라!",
    "17:941:0": "역시 내 호적수, 쉽게 이길 수는 없군\n다음에는 반드시 결판을 내자",
    "17:942:0": "위기를 알아채자 망설임 없이 물러나는가\n",
    "17:942:1": ", 과연 훌륭한 퇴각 판단이군",
    "17:943:0": "이것으로 ", "17:943:1": "북부 시나노",
    "17:943:2": "를 장악했다고 할 수 있겠군\n하지만 이토록 큰 희생을 치르다니……",
    "17:944:0": "이것으로 ", "17:944:1": "북부 시나노",
    "17:944:2": "를 완전히 장악했소\n처음 목표는 달성했다고 할 수 있겠소",
    "17:945:0": "형님의 패업은 순조롭습니다!\n상경도 더는 꿈이 아닙니다!",
    "17:946:0": "이 모두가 너희의 헌신 덕분이다!\n",
    "17:946:1": ", ", "17:946:2": "……앞으로도 두 사람을 믿겠다",
    "17:947:0": "큭, 이것이 군신의 싸움인가……당해 낼 수 없군\n",
    "17:947:1": ", 다음에 다시 만나자",
    "17:948:0": "드, 드디어 마주했군……\n자, 그 목을 내놓아라",
    "17:949:0": "이 목은 내줄 수 없다!\n우리는 여기서 끝날 수 없다!",
    "17:950:0": "선봉 ", "17:950:1": "부대를 격파하라",
    "17:951:0": "선봉 ", "17:951:1": "부대를 격파하라", "17:951:2": " 성공",
    "17:952:0": "선봉 ", "17:952:1": "부대를 격파하라", "17:952:2": " 실패",
    "17:953:0": "부대를 격파하라",
    "17:954:0": "부대를 격파하라", "17:954:1": " 성공",
    "17:955:0": "부대를 격파하라", "17:955:1": " 실패",
    "17:956:0": "적의 ", "17:956:1": "퇴로", "17:956:2": "를 파괴하라",
    "17:957:0": "적의 ", "17:957:1": "퇴로", "17:957:2": "를 파괴하라", "17:957:3": " 성공",
    "17:958:0": "적의 ", "17:958:1": "퇴로", "17:958:2": "를 파괴하라", "17:958:3": " 실패",
    "17:959:0": "부대\u00b7", "17:959:1": "부대\u00b7", "17:959:2": "부대를 격파당하지 마라",
    "17:960:0": "부대\u00b7", "17:960:1": "부대\u00b7",
    "17:960:2": "부대를 격파당하지 마라", "17:960:3": " 성공",
}
EXPECTED_ARITY = {
    932: 3, 933: 1, 934: 4, 935: 1, 936: 2, 937: 2, 938: 1,
    939: 3, 940: 1, 941: 1, 942: 2, 943: 3, 944: 3, 945: 1,
    946: 3, 947: 2, 948: 1, 949: 1, 950: 2, 951: 3, 952: 3,
    953: 1, 954: 2, 955: 2, 956: 3, 957: 4, 958: 4, 959: 3, 960: 4,
}
SEMANTIC_BASE_CONTEXT = {rid: ("9:1006:0",) for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_RAW_MATCHES = {rid: () for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {rid: ((), ()) for rid in TARGET_RECORD_IDS}
EXPECTED_CONTROLS_BY_RECORD.update({
    933: ((), ("024833",)),
    935: ((), ("024835",)),
    936: ((), ("024835",)),
    937: ((), ("024835", "024935")),
    942: ((), ("024835",)),
    946: ((), ("024835", "024935")),
    947: ((), ("024835",)),
    948: ((), ("024835",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1438, queue_start=134, queue_stop=200,
    slice_first="17:932:0", slice_last="17:960:3",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(), prefill_companion_donor={},
    hidden_current_companion_coordinates=(), semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD, source_call_roots=(),
    boundary_record_keys=tuple((17, rid) for rid in range(900, 990)),
    speaker_style=tuple((rid, "historical_battle_dialogue") for rid in TARGET_RECORD_IDS),
    terminology_policy=(("Takeda", "다케다"), ("Northern Shinano", "북부 시나노"),
        ("retreat point", "퇴로"), ("vanguard", "선봉"), ("project long ellipsis", "……")),
    basis=("the B144 residual slice was reviewed from pristine PK source, multilingual "
        "fragments, complete assemblies and historical battle context; Base is semantic "
        "context only; historical titles, controls, tokens, whitespace, particles, "
        "registers, pins, overlays, reproduction, tamper rejection and Steam read-only "
        "state are guarded"),
    expected_changed_literal_count=19,
    pins={
        "expected_queue_universe_sha256": "573B276CE8CE04DBDA6709EC8A3634712677C3238EBE0BA94A3A30DA2610C464",
        "expected_queue_slice_sha256": "41C25447C10DAFBA31E16F2BDC31CB2AB26A4C9C23BB38FB91E2F31C896EBB77",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "41C25447C10DAFBA31E16F2BDC31CB2AB26A4C9C23BB38FB91E2F31C896EBB77",
        "expected_source_target_sha256": "AF4C35BAB2B49A39660678B1411E40F79DD101473E521972972A1D409FD2729A",
        "expected_current_target_sha256": "3AC76C3E9A323D888BBE4B5CF536A35BB5524527B8DD44E702541B1832BE121C",
        "expected_context_corpus_sha256": "CE8F29663C7509292677E839A7D979700161461D5F85671363A5C7080690C1E7",
        "expected_gap_contract_sha256": "CD004D4A5EA8F9DF04E20AEACA6D15AE7677EF39847C7EADD5F4554666FBBF21",
        "expected_boundary_sha256": "CA8089A4ABB0A605B69659B40D050370BFF894C2D50D01C36F907C14F7D1AD38",
        "expected_runtime_control_sha256": "313E42EF48ED2A4593E1C45DF91DE6CA5AFDF5ED3EEED9E87300E83C5E9FCDDC",
        "expected_base_search_sha256": "FF0792158C73D8025E25465E510681BBA631C6A07474596404454CED6A9498ED",
        "expected_complete_assembly_sha256": "8433B70EB855B1285E3694790B37CC1674B1D33449EE006381C2B7F661E3A476",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "6204090C2FEA71300AEB312B267AD960185A4F3B763402C234211159B9F0F6DB",
        "expected_terminology_policy_sha256": "7C84647543965D122CA4991AA77C7E21045E123CAD2D4CA6D05827228E955DF3",
        "expected_translation_policy_sha256": "97E09E477FC82794F2028477F2E66B474DDDE7AA5E4C3ECCC40615E0A21D450A",
        "expected_candidate_sha256": "3BA418F892CE00D6EF610C0D6E7D9764B70731F76BED030ED592D40DF2A5F7FD",
        "expected_combined_slice_candidate_sha256": "3BA418F892CE00D6EF610C0D6E7D9764B70731F76BED030ED592D40DF2A5F7FD",
        "expected_combined_changed_literal_count": 19,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B144_S1438",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B144_S1438.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B144_S1436.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B144_S1437.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B144", "queue_row_count": 115,
    "queue_visible_count": 200, "queue_first": "17:846:0", "queue_last": "17:960:3",
})


def install_globals():
    _ORIGINAL_INSTALL_GLOBALS()
    COMMON.BASE.BLOCK_ID = 17
    COMMON.BASE.EXACT_BASE_DONOR = {}


COMMON.install_globals = install_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
