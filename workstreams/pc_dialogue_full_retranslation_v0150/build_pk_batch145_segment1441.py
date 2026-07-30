#!/usr/bin/env python3
"""Build source-redacted PK B145 segment 1441 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = COMMON.BASE.base_and_assembly_evidence

TARGET_COORDINATES = (
    "17:1029:1",
    "17:1030:0", "17:1031:0", "17:1032:0", "17:1033:0",
    "17:1034:0", "17:1034:1", "17:1034:2",
    "17:1035:0", "17:1035:1", "17:1035:2",
    "17:1036:0", "17:1037:0", "17:1037:1",
    "17:1038:0", "17:1038:1", "17:1038:2",
    "17:1039:0", "17:1039:1", "17:1039:2",
    "17:1040:0", "17:1040:1", "17:1041:0", "17:1041:1",
    "17:1042:0", "17:1043:0", "17:1044:0", "17:1044:1",
    "17:1045:0", "17:1045:1", "17:1046:0",
    "17:1047:0", "17:1047:1", "17:1047:2",
    "17:1048:0", "17:1049:0", "17:1049:1",
    "17:1050:0", "17:1050:1", "17:1051:0",
    "17:1052:0", "17:1052:1", "17:1053:0",
    "17:1055:0", "17:1056:0", "17:1057:0", "17:1058:0",
    "17:1059:0", "17:1059:1", "17:1060:0", "17:1060:1",
    "17:1061:0", "17:1062:0", "17:1063:0",
    "17:1064:0", "17:1064:1", "17:1065:0", "17:1066:0",
    "17:1067:0", "17:1067:1", "17:1067:2",
    "17:1068:0", "17:1068:1",
)
TRANSLATIONS = {
    "17:1029:1": " 실패",
    "17:1030:0": "좋아, 이 기세다!\n이대로 성을 끝까지 지켜 내자!",
    "17:1031:0": "큭…… 정말 끈질기군……",
    "17:1032:0": "좋다, 이 기세로 성을 제압하라!",
    "17:1033:0": "성문이 뚫렸다고……?\n큰일이다…… 어떻게든 적을 막아라!",
    "17:1034:0": "가와고에성",
    "17:1034:1": "은 아직 버티고 있군!\n잘했다,",
    "17:1034:2": "!",
    "17:1035:0": "우리의 존망은 이 한 싸움에 달렸다!\n",
    "17:1035:1": "호조",
    "17:1035:2": " 정예들이여, 진군하라!",
    "17:1036:0": "우리 제2진도 진군한다!\n적의 성을 완전히 함락하라!",
    "17:1037:0": "부대로", "17:1037:1": "부대를 기습하라",
    "17:1038:0": "부대로", "17:1038:1": "부대를 기습하라",
    "17:1038:2": " 성공",
    "17:1039:0": "부대로", "17:1039:1": "부대를 기습하라",
    "17:1039:2": " 실패",
    "17:1040:0": "간다!!", "17:1040:1": ", 각오해라!",
    "17:1041:0": "뭐…… 설마", "17:1041:1": "라고!\n저자가 왜 여기에!",
    "17:1042:0": "좋아, 적이 동요하는군!\n지금이야, 단숨에 쓸어버려라!",
    "17:1043:0": "부대를 격파하라",
    "17:1044:0": "부대를 격파하라", "17:1044:1": " 성공",
    "17:1045:0": "부대를 격파하라", "17:1045:1": " 실패",
    "17:1046:0": "으악…… 얘기가 다르잖아……\n이런 곳에서 죽을 순 없어, 달아나야 해……",
    "17:1047:0": "잘했다, ", "17:1047:1": "호조",
    "17:1047:2": " 장병들이여!\n이대로 끝까지 성을 지켜라!",
    "17:1048:0": "부대와 교전해 격파하라",
    "17:1049:0": "부대와 교전해 격파하라", "17:1049:1": " 성공",
    "17:1050:0": "부대와 교전해 격파하라", "17:1050:1": " 실패",
    "17:1051:0": "님, 각오해라!",
    "17:1052:0": "호조", "17:1052:1": "군이라고……!?\n누구든 좋으니, 나를 지켜라!",
    "17:1053:0": "마, 말도 안 돼…… 내 목숨이……\n이런 곳에서 끝나다니……",
    "17:1055:0": "이번 싸움에는 나도 나서야겠군……\n성을 향해 출진한다!",
    "17:1056:0": "적의 공세도 약해졌군\n과연 형님이야",
    "17:1057:0": "를 쓰러뜨리고\n이 싸움을 끝낸다!",
    "17:1058:0": "부대를 격파하라",
    "17:1059:0": "부대를 격파하라", "17:1059:1": " 성공",
    "17:1060:0": "부대를 격파하라", "17:1060:1": " 실패",
    "17:1061:0": "설마 패하다니…… 두고 보자……",
    "17:1062:0": "승리의 함성을 올려라!\n이 싸움은 우리의 승리다!",
    "17:1063:0": "큭……\n이런 곳에서 패하다니……",
    "17:1064:0": "가와고에성",
    "17:1064:1": "이……\n이번 싸움은 우리가 졌나……",
    "17:1065:0": "이겼다! 이겼다!",
    "17:1066:0": "그토록 병력 차가 컸는데……\n방심했던 건가……",
    "17:1067:0": "강 건너편에", "17:1067:1": "다케다",
    "17:1067:2": "의 깃발이……!\n스스로 이 사지에 발을 들이다니……",
    "17:1068:0": "적들도 각오를 굳힌 것이다\n예전에",
    "17:1068:1": "에게 도전했던 너라면\n알겠지",
}

TARGET_RECORD_IDS = (
    1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038,
    1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048,
    1049, 1050, 1051, 1052, 1053, 1055, 1056, 1057, 1058, 1059,
    1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068,
)
MAIN_RECORD_IDS = tuple(x for x in TARGET_RECORD_IDS if x != 1029)
MAIN_TARGET_COORDINATES = tuple(
    x for x in TARGET_COORDINATES if not x.startswith("17:1029:")
)
EXPECTED_ARITY = {
    1029: 2, 1030: 1, 1031: 1, 1032: 1, 1033: 1, 1034: 3,
    1035: 3, 1036: 1, 1037: 2, 1038: 3, 1039: 3, 1040: 2,
    1041: 2, 1042: 1, 1043: 1, 1044: 2, 1045: 2, 1046: 1,
    1047: 3, 1048: 1, 1049: 2, 1050: 2, 1051: 1, 1052: 2,
    1053: 1, 1055: 1, 1056: 1, 1057: 1, 1058: 1, 1059: 2,
    1060: 2, 1061: 1, 1062: 1, 1063: 1, 1064: 2, 1065: 1,
    1066: 1, 1067: 3, 1068: 2,
}
NEIGHBOR = {"17:1029:0": "성문 제압 전에 적 부대 1개 격파"}
OBJECTIVE_RECORD_IDS = {
    1029, 1037, 1038, 1039, 1043, 1044, 1045, 1048, 1049, 1050,
    1058, 1059, 1060,
}
SEMANTIC_BASE_CONTEXT = {
    rid: (("9:2842:0",) if rid in OBJECTIVE_RECORD_IDS else ("9:1006:0",))
    for rid in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {rid: () for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {rid: ((), ()) for rid in TARGET_RECORD_IDS}
EXPECTED_CONTROLS_BY_RECORD.update({
    1034: ((), ("024835",)),
    1040: ((), ("024833",)),
    1041: ((), ("024835",)),
    1051: ((), ("024833",)),
    1057: ((), ("024835",)),
    1068: ((), ("024835",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1441, queue_start=134, queue_stop=198,
    slice_first="17:1029:1", slice_last="17:1068:1",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(), prefill_companion_donor={},
    hidden_current_companion_coordinates=(), semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD, source_call_roots=(),
    boundary_record_keys=tuple((17, rid) for rid in range(995, 1100)),
    speaker_style=tuple(
        (rid, "kawagoe_historical_battle_dialogue") for rid in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Kawagoe Castle", "가와고에성"), ("Hojo", "호조"),
        ("Takeda", "다케다"), ("castle gate", "성문"),
        ("second formation", "제2진"), ("project long ellipsis", "……"),
    ),
    basis=(
        "the B145 final residual slice was reviewed from pristine PK source, "
        "multilingual fragments, complete assemblies and the historical Kawagoe "
        "battle context; one full record is already covered by approved exact Base "
        "reuse and record 1029 is reciprocally assembled with segment 1440; Base is "
        "otherwise semantic context only; historical names, tactical objective "
        "wording, controls, tokens, whitespace, particles, registers, pins, overlays, "
        "reproduction, tamper rejection and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=22,
    pins={
        "expected_queue_universe_sha256": "70E0037D99B43444619DC9E531C28BA2DC4FCE9B6772EE886C653132791548E0",
        "expected_queue_slice_sha256": "92954C181574C939663F65491C4587F1F775AE7BBBB9CDA2A0E962F4274D0A64",
        "expected_prefilled_coordinate_sha256": "D19477A4DF895BE51499B707880BAF8817370518B21DC9A428725A1D57B31C27",
        "expected_prefill_slice_context_sha256": "F9A859500D5BE54D9B899BE42DD7CD41DFDF5F2A9517086356A764D3B17F674E",
        "expected_target_coordinate_sha256": "888A6BC926D2FD1F5C674AB67A15F0620BF20D3EF2B28045A526AE706F0D4CEB",
        "expected_source_target_sha256": "26C39CD6678C29A617BAEC089D131339F852FB92B77571681D18BF5AB9BECA79",
        "expected_current_target_sha256": "CA32A1D691743DBEE0865C8720A4093D1E6352A5F8DECFE6A882D56BD27BD0CB",
        "expected_context_corpus_sha256": "40DF8E6F091D56470657530F2949F7E3679106D788AEE1924C3F34FB5E13E55C",
        "expected_gap_contract_sha256": "10F6E7D4E1977E1A2774966249E6247A92D5F2D37B043DDA74D52DA053F0031A",
        "expected_boundary_sha256": "38643996C3959721D1A617580B7E65B7E6C10B60051C026B4699A4E791D62681",
        "expected_runtime_control_sha256": "B8AA102EEF0968B3A9EACEBF01AA7805BB66DF4748A57EC28E90363ABA86F5D5",
        "expected_base_search_sha256": "B6C05B2266CF95E21F964F639ED2B172858C36D9C52185ED2221EC60C68459C1",
        "expected_complete_assembly_sha256": "5F8742B61DDBB4699CC2158AF20AB9B4A72F662B61270F7BE7A83284AE21224F",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "61E015DFFD9DD204D78309FB7CB610FB8EF34DBDA40160738820CE4B75217F80",
        "expected_terminology_policy_sha256": "F779478E59342E5125A012BA203A37C0C91A01C7427FAAA50F8F8B2853995733",
        "expected_translation_policy_sha256": "D7E0144B334D72FD95BAD11D50C481BAEE3C5EE933289EB5E27AD378A9413CE6",
        "expected_candidate_sha256": "EBCAF7B1095EC833E246DCEEA8DBFE1354840883ED9BD003FD77CA118C310645",
        "expected_combined_slice_candidate_sha256": "EBCAF7B1095EC833E246DCEEA8DBFE1354840883ED9BD003FD77CA118C310645",
        "expected_combined_changed_literal_count": 22,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B145_S1441",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B145_S1441.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B145_S1439.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B145_S1440.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B145", "queue_row_count": 108,
    "queue_visible_count": 198, "queue_first": "17:961:0",
    "queue_last": "17:1068:1",
})


def boundary_evidence(
    prepared: Any,
    records: dict[str, dict[tuple[int, int], Any]],
):
    g = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_ids, saved_coords = g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"]
    g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = (
        MAIN_RECORD_IDS,
        MAIN_TARGET_COORDINATES,
    )
    try:
        base, assembly = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(prepared, records)
    finally:
        g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = saved_ids, saved_coords
    source = records["jp"][(17, 1029)]
    current = records["current"][(17, 1029)]
    sl = COMMON.literal_texts(records["jp"], (17, 1029))
    cl = COMMON.literal_texts(records["current"], (17, 1029))
    base_records = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    raw = tuple(k for k, r in base_records.items() if r.data == source.data)
    literal = tuple(
        k for k in base_records if COMMON.literal_texts(base_records, k) == sl
    )
    masked = tuple(
        k for k, r in base_records.items()
        if COMMON.literal_texts(base_records, k) == sl
        and COMMON.CORE.mask_call_operands(r) == COMMON.CORE.mask_call_operands(source)
    )
    assembled = (NEIGHBOR["17:1029:0"], TRANSLATIONS["17:1029:1"])
    neighbors = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"] if path.is_file()
        for row in COMMON.read_jsonl(path)
    }
    if (
        neighbors.get("17:1029:0") is not None
        and neighbors["17:1029:0"].get("translation") != NEIGHBOR["17:1029:0"]
    ):
        raise RuntimeError("segment 1441 neighbor drifted")
    if (
        len(sl) != 2 or raw or literal or masked
        or assembled != ("성문 제압 전에 적 부대 1개 격파", " 실패")
    ):
        raise RuntimeError("segment 1441 boundary assembly drifted")
    donor = next(
        row for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
        if row["coordinate"] == "9:2842:0"
    )
    refs = (("9:2842:0", donor["translation"], donor["runtime_review"]),)
    return (
        tuple(base) + ((
            1029, COMMON.sha256_bytes(source.data), sl, cl,
            tuple(x.hex().upper() for x in COMMON.gap_bytes(source)),
            raw, literal, masked, refs, "semantic_context_only",
        ),),
        tuple(assembly) + ((
            1029,
            ("optional_previous_segment_manual_companion", "segment_manual_multilingual"),
            assembled, None, COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current), "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ),),
    )


def install_globals():
    _ORIGINAL_INSTALL_GLOBALS()
    COMMON.BASE.BLOCK_ID = 17
    COMMON.BASE.EXACT_BASE_DONOR = {}


def install_b071_globals():
    _ORIGINAL_B071_INSTALL_GLOBALS()
    COMMON.BASE.BASE.BASE.PARENT.PARENT.base_and_assembly_evidence = boundary_evidence
    COMMON.CORE.base_and_assembly_evidence = boundary_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
