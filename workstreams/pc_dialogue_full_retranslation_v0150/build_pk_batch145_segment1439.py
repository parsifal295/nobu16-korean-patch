#!/usr/bin/env python3
"""Build source-redacted PK B145 segment 1439 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:961:0", "17:961:1", "17:961:2", "17:961:3",
    "17:962:0", "17:962:1", "17:962:2", "17:963:0",
    "17:963:1", "17:963:2", "17:963:3", "17:964:0",
    "17:964:1", "17:964:2", "17:964:3", "17:965:0",
    "17:965:1", "17:965:2", "17:965:3", "17:966:0",
    "17:967:0", "17:967:1", "17:967:2", "17:968:0",
    "17:968:1", "17:969:0", "17:970:0", "17:971:0",
    "17:971:1", "17:972:0", "17:972:1", "17:973:0",
    "17:973:1", "17:974:0", "17:974:1", "17:974:2",
    "17:975:0", "17:976:0", "17:976:1", "17:977:0",
    "17:977:1", "17:977:2", "17:978:0", "17:978:1",
    "17:979:0", "17:979:1", "17:980:0", "17:980:1",
    "17:980:2", "17:981:0", "17:981:1", "17:981:2",
    "17:981:3", "17:983:0", "17:984:0", "17:984:1",
    "17:985:0", "17:986:0", "17:987:0", "17:988:0",
    "17:988:1", "17:989:0", "17:989:1", "17:990:0",
    "17:991:0", "17:991:1", "17:992:0",
)

TRANSLATIONS = {
    "17:961:0": "부대·",
    "17:961:1": "부대·",
    "17:961:2": "부대를 격파당하지 마라",
    "17:961:3": " 실패",
    "17:962:0": "부대·",
    "17:962:1": "부대를",
    "17:962:2": "와 교전시켜라",
    "17:963:0": "부대·",
    "17:963:1": "부대를",
    "17:963:2": "와 교전시켜라",
    "17:963:3": " 성공",
    "17:964:0": "부대·",
    "17:964:1": "부대를",
    "17:964:2": "와 교전시켜라",
    "17:964:3": " 실패",
    "17:965:0": "역시 ",
    "17:965:1": "다케다",
    "17:965:2": "는 군을 나누었군…\n다케다 본대를 기습해 별동대가 돌아오기 전에\n",
    "17:965:3": "를 베어 버리겠다!",
    "17:966:0": "딱따구리 전법을 간파당하다니…\n모두, 원군이 올 때까지 버텨라!",
    "17:967:0": "음? 잠깐,",
    "17:967:1": ", ",
    "17:967:2": "!\n어디로 갈 셈이냐!",
    "17:968:0": "…원래 제 계책의 허점입니다\n온 힘을 다해",
    "17:968:1": "의 기세를 막고 오겠습니다",
    "17:969:0": ", 저 역시 몸이 부서지는 한이 있어도\n본진에 돌입해 시간을 벌겠습니다!",
    "17:970:0": "적은 별동대가 없어 병력이 적다\n서둘러 결판을 내자",
    "17:971:0": "차륜진으로 간다. 먼저 선봉끼리 맞붙어라\n그 뒤 내가 적의 본진…　",
    "17:971:1": "를 친다",
    "17:972:0": "나는 움직이지 않고 때를 기다린다\n",
    "17:972:1": "도 적의 원군에 대비해 대기하라",
    "17:973:0": "나머지는",
    "17:973:1": "을 지키는 장수를 쓰러뜨려라\n모두, 가자!",
    "17:974:0": "큭……",
    "17:974:1": "주군",
    "17:974:2": ", 정말 죄송합니다……\n제 작전을 간파당한 탓에……",
    "17:975:0": "가 전사했다고…!\n말도 안 돼… 어쩌다 이런 일이…",
    "17:976:0": "면목이 없습니다……\n",
    "17:976:1": ", 부디 용서해 주십시오……",
    "17:977:0": "말도 안 돼,",
    "17:977:1": "가…!\n미안하다…　",
    "17:977:2": ", 미안하다…",
    "17:978:0": ", ",
    "17:978:1": "가 쓰러지다니……\n이대로는……",
    "17:979:0": "이제 적이 무너졌군\n내가 직접",
    "17:979:1": "를 쓰러뜨리겠다!",
    "17:980:0": "우리라도 서둘러 왔습니다……\n",
    "17:980:1": "주군",
    "17:980:2": "께서는 무사하십니까?!",
    "17:981:0": "사이조산",
    "17:981:1": "의 적병이 돌아오기 시작했나…\n",
    "17:981:2": "퇴로",
    "17:981:3": "를 사수하라!",
    "17:983:0": "를 지킬 자는 이제 없다!",
    "17:984:0": "전군, 나를 따라 진군하라!\n오늘이야말로",
    "17:984:1": "를 쓰러뜨린다!",
    "17:985:0": "님…\n이번에는 내가 이긴 듯하군",
    "17:986:0": "님인가…\n딱따구리 전법을 잘도 간파했군",
    "17:987:0": "하지만 아군이 모두 모일 때까지\n아직 질 수는 없다…!",
    "17:988:0": "모든 별동대가 돌아오기 전에\n",
    "17:988:1": "를 궁지로 몰아라!",
    "17:989:0": "호오, 따라잡았나\n",
    "17:989:1": ", 적의 원군을 막아라",
    "17:990:0": "알겠습니다, 제가 막겠습니다",
    "17:991:0": "그 틈에 우리가",
    "17:991:1": "\n를 궁지로 몰아넣는다!",
    "17:992:0": "제가 막아 낼 수 있는 것도\n여기까지인 듯합니다…",
}

TARGET_RECORD_IDS = (
    961, 962, 963, 964, 965, 966, 967, 968, 969, 970,
    971, 972, 973, 974, 975, 976, 977, 978, 979, 980,
    981, 983, 984, 985, 986, 987, 988, 989, 990, 991,
    992,
)
EXPECTED_ARITY = {
    961: 4, 962: 3, 963: 4, 964: 4, 965: 4, 966: 1,
    967: 3, 968: 2, 969: 1, 970: 1, 971: 2, 972: 2,
    973: 2, 974: 3, 975: 1, 976: 2, 977: 3, 978: 2,
    979: 2, 980: 3, 981: 4, 983: 1, 984: 2, 985: 1,
    986: 1, 987: 1, 988: 2, 989: 2, 990: 1, 991: 2,
    992: 1,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {961, 962, 963, 964}
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
    965: ((), ("024833",)),
    967: ((), ("024835", "024935")),
    968: ((), ("024835",)),
    969: ((8,), ()),
    971: ((), ("024835",)),
    972: ((), ("024835",)),
    973: ((), ("024835",)),
    975: ((), ("024835",)),
    976: ((8,), ()),
    977: ((), ("024835", "024835")),
    978: ((), ("024835", "024935")),
    979: ((), ("024835",)),
    983: ((), ("024835",)),
    984: ((), ("024835",)),
    985: ((), ("024835",)),
    986: ((), ("024835",)),
    988: ((), ("024835",)),
    989: ((), ("024835",)),
    991: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1439,
    queue_start=0,
    queue_stop=67,
    slice_first="17:961:0",
    slice_last="17:992:0",
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
    source_call_roots=(8,),
    boundary_record_keys=tuple(
        (17, record_id) for record_id in range(926, 1034)
    ),
    speaker_style=tuple(
        (record_id, "kawanakajima_historical_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Takeda", "다케다"),
        ("woodpecker strategy", "딱따구리 전법"),
        ("wheeling formation", "차륜진"),
        ("Saijosan", "사이조산"),
        ("detachment", "별동대"),
        ("main camp", "본진"),
        ("retreat route", "퇴로"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B145 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context; "
        "completed Base objective and officer dialogue rows are semantic "
        "and terminology references only because none of the thirty-one "
        "PK records has a raw, literal or operand-masked Base match; the "
        "Japanese text, rather than the divergent English lure and "
        "surprise-attack lines, controls the reconstruction; Takeda, the "
        "woodpecker strategy, wheeling formation and Saijosan retain "
        "established historical forms; tactical orders, sacrificial vows, "
        "death reports and commander exchanges remain distinct; direct "
        "calls, inline person and unit tokens, protected spaces, line "
        "breaks, particles, punctuation, terminators, complete record "
        "arity, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, reciprocal S1440 and S1441 "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=18,
    pins={
        "expected_queue_universe_sha256":
        "70E0037D99B43444619DC9E531C28BA2DC4FCE9B6772EE886C653132791548E0",
        "expected_queue_slice_sha256":
        "66CC9828A2D19FFFDA26FC2E640B48146C897728584929F3188650152F37E9CD",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "66CC9828A2D19FFFDA26FC2E640B48146C897728584929F3188650152F37E9CD",
        "expected_source_target_sha256":
        "170864A8BC0C7B34CB6AC3ED9CE793C3D9E56EEDE0BB060235C0F4D65E40275B",
        "expected_current_target_sha256":
        "FA3B891D6472262020CB03DFA40193724F23143D43C17B5A4E94EA01D0641400",
        "expected_context_corpus_sha256":
        "40DF8E6F091D56470657530F2949F7E3679106D788AEE1924C3F34FB5E13E55C",
        "expected_gap_contract_sha256":
        "E9E73669DADC089453CF42A916CF060D8A06D41F8A5042BBA7346B3C8D43CE11",
        "expected_boundary_sha256":
        "B8A01623B0F748F45488DDB91D154EFF75CEAD984D0090E117FD530068BC9B07",
        "expected_runtime_control_sha256":
        "496A40FAE0BCDA0112675E9BDDC747B5DDD6C2A0D6564AB71D7C104DE9E25C80",
        "expected_base_search_sha256":
        "97B709A4A01D626DB15E3F5DECA4EDE5B4BA1628399B8D2B5E404BA6A000D5D7",
        "expected_complete_assembly_sha256":
        "4ACB59C55593653F38598D69C29644C0F80C386845D24DB4518847C15F015B91",
        "expected_call_graph_sha256":
        "34F168518E1698E7FE9E5BC5D2252B8EBD655E803B6CE7BBC2DB0A0E5D20F05B",
        "expected_speaker_style_sha256":
        "07619EFB6481DAC4521E9BB7A5214FF1C73F340816E6AC262996FEAFF6D998BF",
        "expected_terminology_policy_sha256":
        "F2FD58F9AFC6BDF21C408675B58AD8E790D5434ECFD7BED694A15ABE40247A7E",
        "expected_translation_policy_sha256":
        "FEBE25EDA8E896112A95536952A335509B5C8D7A59D0B7CD8D3B0DE45A7A31CC",
        "expected_candidate_sha256":
        "CD8A7C91CE0FF31DFF3A9E6BAA513A7A5CD1A950C3BBCA5C9CE217A7DFCBCF46",
        "expected_combined_slice_candidate_sha256":
        "CD8A7C91CE0FF31DFF3A9E6BAA513A7A5CD1A950C3BBCA5C9CE217A7DFCBCF46",
        "expected_combined_changed_literal_count": 18,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B145_S1439",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B145_S1439.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B145_S1440.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B145_S1441.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B145",
    "queue_row_count": 108,
    "queue_visible_count": 198,
    "queue_first": "17:961:0",
    "queue_last": "17:1068:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
