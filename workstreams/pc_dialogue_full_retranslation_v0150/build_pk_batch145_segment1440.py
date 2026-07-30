#!/usr/bin/env python3
"""Build source-redacted PK B145 segment 1440 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_READ_JSONL = COMMON.BASE.read_jsonl
_ORIGINAL_BASE_EVIDENCE = COMMON.BASE.base_and_assembly_evidence

TARGET_COORDINATES = (
    "17:993:0", "17:994:0", "17:995:0", "17:996:0",
    "17:997:0", "17:998:0", "17:999:0", "17:1000:0",
    "17:1001:0", "17:1002:0", "17:1003:0",
    "17:1004:0", "17:1004:1",
    "17:1005:0", "17:1005:1",
    "17:1006:0", "17:1006:1", "17:1006:2",
    "17:1007:0", "17:1007:1", "17:1007:2",
    "17:1008:0", "17:1009:0", "17:1009:1",
    "17:1010:0", "17:1010:1", "17:1011:0",
    "17:1012:0", "17:1012:1", "17:1013:0", "17:1013:1",
    "17:1014:0", "17:1014:1",
    "17:1015:0", "17:1015:1", "17:1015:2",
    "17:1016:0", "17:1016:1", "17:1016:2",
    "17:1017:0", "17:1018:0", "17:1018:1",
    "17:1019:0", "17:1019:1",
    "17:1020:0", "17:1020:1", "17:1020:2",
    "17:1021:0", "17:1021:1", "17:1021:2", "17:1021:3",
    "17:1022:0", "17:1022:1", "17:1022:2", "17:1022:3",
    "17:1023:0", "17:1024:0", "17:1024:1", "17:1024:2",
    "17:1025:0", "17:1025:1", "17:1025:2",
    "17:1026:0", "17:1027:0",
    "17:1028:0", "17:1028:1", "17:1029:0",
)
TRANSLATIONS = {
    "17:993:0": "……이 싸움도 여기까지인가\n이대로라면 협공을 당한다",
    "17:994:0": "여기서는 물러나도록 하지……\n다음에야말로 결판을 내겠다",
    "17:995:0": "설마 내게 일격을 먹이다니……\n운 좋게 군배로 막았지만, 다음은……!",
    "17:996:0": "드디어 도착했다!\n전황은 어떠냐!",
    "17:997:0": "놈!\n절대로 적을 이 전장에서 놓치지 마라!",
    "17:998:0": "오오, 드디어 돌아왔나!\n전사자들의 원수를 갚아라! 모두, 분발하라!",
    "17:999:0": "적이 모두 집결했군……\n이 싸움은 여기까지다",
    "17:1000:0": "여기서는 물러나도록 하지……\n다음에야말로 결판을 내겠다",
    "17:1001:0": "나를 쓰러뜨리다니, 과연 군신이군……\n하지만 이 전장에서 달아날 수 있겠나?",
    "17:1002:0": "퇴각하게 될 줄이야……\n이번에도 완전히 이기진 못했지만, 다음에는 반드시……",
    "17:1003:0": "이번 싸움은 나의 큰 실책이다……\n비사문천마저 나를 버리겠구나……",
    "17:1004:0": "퇴로를 빼앗기다니……\n과연",
    "17:1004:1": "의 정예군이로군",
    "17:1005:0": "퇴로",
    "17:1005:1": "을 사수하라",
    "17:1006:0": "퇴로",
    "17:1006:1": "을 사수하라",
    "17:1006:2": " 성공",
    "17:1007:0": "퇴로",
    "17:1007:1": "을 사수하라",
    "17:1007:2": " 실패",
    "17:1008:0": "부대를 격파하라",
    "17:1009:0": "부대를 격파하라",
    "17:1009:1": " 성공",
    "17:1010:0": "부대를 격파하라",
    "17:1010:1": " 실패",
    "17:1011:0": "부대를 격파하라",
    "17:1012:0": "부대를 격파하라",
    "17:1012:1": " 성공",
    "17:1013:0": "부대를 격파하라",
    "17:1013:1": " 실패",
    "17:1014:0": "부대를",
    "17:1014:1": "부대와 교전시켜라",
    "17:1015:0": "부대를",
    "17:1015:1": "부대와 교전시켜라",
    "17:1015:2": " 성공",
    "17:1016:0": "부대를",
    "17:1016:1": "부대와 교전시켜라",
    "17:1016:2": " 실패",
    "17:1017:0": "부대를 궁지로 몰아라",
    "17:1018:0": "부대를 궁지로 몰아라",
    "17:1018:1": " 성공",
    "17:1019:0": "부대를 궁지로 몰아라",
    "17:1019:1": " 실패",
    "17:1020:0": "부대를",
    "17:1020:1": "퇴로",
    "17:1020:2": "까지 이동시켜라",
    "17:1021:0": "부대를",
    "17:1021:1": "퇴로",
    "17:1021:2": "까지 이동시켜라",
    "17:1021:3": " 성공",
    "17:1022:0": "부대를",
    "17:1022:1": "퇴로",
    "17:1022:2": "까지 이동시켜라",
    "17:1022:3": " 실패",
    "17:1023:0": (
        "농성을 시작한 지도 벌써 몇 달……\n"
        "아직 형님에게서 소식은 없지만\n"
        "믿고 성을 끝까지 지킬 뿐이다!"
    ),
    "17:1024:0": "이 병력으로 질 리가 없다\n오늘이야말로 ",
    "17:1024:1": "가와고에성",
    "17:1024:2": "을 함락하자",
    "17:1025:0": "제1진, 전진하라!\n",
    "17:1025:1": "호조",
    "17:1025:2": "에게 힘의 차이를 보여 줘라",
    "17:1026:0": "형님은 반드시 오신다……!\n하지만 지금은 어떻게든 버텨야 해!",
    "17:1027:0": "성문 제압 전에 적 부대 1개 격파",
    "17:1028:0": "성문 제압 전에 적 부대 1개 격파",
    "17:1028:1": " 성공",
    "17:1029:0": "성문 제압 전에 적 부대 1개 격파",
}
TARGET_RECORD_IDS = tuple(range(993, 1030))
EXPECTED_ARITY = {
    993: 1, 994: 1, 995: 1, 996: 1, 997: 1, 998: 1, 999: 1,
    1000: 1, 1001: 1, 1002: 1, 1003: 1, 1004: 2,
    1005: 2, 1006: 3, 1007: 3, 1008: 1, 1009: 2, 1010: 2,
    1011: 1, 1012: 2, 1013: 2, 1014: 2, 1015: 3, 1016: 3,
    1017: 1, 1018: 2, 1019: 2, 1020: 3, 1021: 4, 1022: 4,
    1023: 1, 1024: 3, 1025: 3, 1026: 1, 1027: 1, 1028: 2,
    1029: 2,
}
PREFILL_COMPANION_COORDINATES = ("17:1029:1",)
PREFILL_COMPANION_DONOR = {"17:1029:1": "neighbor:S1441"}
SPLIT_TRANSLATIONS = {"17:1029:1": " 실패"}
SYNTHETIC_ROWS = tuple({
    "coordinate": coordinate,
    "translation": translation,
    "semantic_review": "approved",
    "runtime_review": "pending",
    "base_exact_reuse_prefill": {
        "base_coordinate": PREFILL_COMPANION_DONOR[coordinate],
        "runtime_promotion_authorized": False,
    },
} for coordinate, translation in SPLIT_TRANSLATIONS.items())
SEMANTIC_BASE_CONTEXT = {
    record_id: ("9:1006:0",)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    997: ((), ("024835",)),
    1004: ((), ("024834",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1440, queue_start=67, queue_stop=134,
    slice_first="17:993:0", slice_last="17:1029:0",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple((17, record_id) for record_id in range(961, 1069)),
    speaker_style=tuple(
        (record_id, "historical_battle_dialogue_or_objective")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Bishamonten", "비사문천"),
        ("war fan", "군배"),
        ("God of War", "군신"),
        ("Kawagoe Castle", "가와고에성"),
        ("Hōjō", "호조"),
        ("disengagement point", "퇴로"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "all sixty-seven visible B145 middle-slice coordinates are manually "
        "reviewed against pristine PK JP and complete PK EN SC TC context; "
        "completed Base rows provide semantic terminology context only; "
        "the split gate-defense failure objective in record 1029 is "
        "completed with the reciprocally reviewed segment-1441 suffix; "
        "the Kawanakajima aftermath and Kawagoe defense preserve established "
        "Bishamonten, war-fan, Hōjō, castle and retreat terminology; "
        "historical command registers, dynamic names, controls, protected "
        "whitespace, line breaks, complete arity, pins, reverse overlays, "
        "tamper rejection, outside-scope identity, optional neighbors and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256": "70E0037D99B43444619DC9E531C28BA2DC4FCE9B6772EE886C653132791548E0",
        "expected_queue_slice_sha256": "D6B2E2CA0A96B6D0424FEEF7F9CA334C5BE9D581B77C2EFA3A32160F4769F348",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "D6B2E2CA0A96B6D0424FEEF7F9CA334C5BE9D581B77C2EFA3A32160F4769F348",
        "expected_source_target_sha256": "158F3136E921DAA21347C00F7C229A471BEB414C922E424E9F4CAC3BE41226AE",
        "expected_current_target_sha256": "BF4A0BA4D10F1FC602F589FCE966A052E2152C415019BD380B7CD52FA41DD06C",
        "expected_context_corpus_sha256": "40DF8E6F091D56470657530F2949F7E3679106D788AEE1924C3F34FB5E13E55C",
        "expected_gap_contract_sha256": "02017957553083CE2C7A7918061B9A8F07DE4C3784F517262537F8550F297BA1",
        "expected_boundary_sha256": "8D0B5D27802FFA5D756DD42962A8F5A8B9D13C3C6BBB6E20C62F490BB5FB511F",
        "expected_runtime_control_sha256": "54187032529C2AF90B873084F72BBC76685B2C940DEAE0CF9637392ED9F50F26",
        "expected_base_search_sha256": "57A19E94F11B82BC82B5BCEBE0DFF2BD31C3BDA5002CF084A56710EFEFC12D35",
        "expected_complete_assembly_sha256": "43162C4B80D46CE9136DB4C1F35E3BDAF7C05F7E7FAEAA7B2CCD6EC556104806",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "3ED42BA0085CED05B6590F8DB80A12E581161A12588386497AAC328AA09CD15E",
        "expected_terminology_policy_sha256": "34A73F1BE3985386A2D127567577D9510C979547BDE927455609772DEC71CD85",
        "expected_translation_policy_sha256": "BF0B335AB90EEB4DD8F39A485623D3B23DC2978430ACE0E49DDBA03EC97A73DE",
        "expected_candidate_sha256": "E8F2D3135229AA247AB755F17997A46E0BEF8C756D2E2382956C56B44E126CDB",
        "expected_combined_slice_candidate_sha256": "E8F2D3135229AA247AB755F17997A46E0BEF8C756D2E2382956C56B44E126CDB",
        "expected_combined_changed_literal_count": 12,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B145_S1440",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B145_S1440.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B145_S1439.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B145_S1441.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B145", "queue_row_count": 108,
    "queue_visible_count": 198, "queue_first": "17:961:0",
    "queue_last": "17:1068:1",
})


def read_jsonl_with_splits(path: Path) -> tuple[dict[str, Any], ...]:
    rows = tuple(_ORIGINAL_READ_JSONL(path))
    if path.resolve(strict=False) == COMMON.PREFILL.resolve(strict=False):
        return rows + SYNTHETIC_ROWS
    return rows


def base_evidence_with_splits(
    prepared: Any,
    records: dict[str, Any],
) -> Any:
    neighbors = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"] if path.is_file()
        for row in _ORIGINAL_READ_JSONL(path)
    }
    for coordinate, expected in SPLIT_TRANSLATIONS.items():
        row = neighbors.get(coordinate)
        if row is not None and (
            row.get("translation") != expected
            or row.get("semantic_review") != "approved"
        ):
            raise RuntimeError(
                f"segment 1440 split neighbor drifted: {coordinate}"
            )
    return _ORIGINAL_BASE_EVIDENCE(prepared, records)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "read_jsonl", read_jsonl_with_splits)
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_evidence_with_splits
    COMMON.CORE.base_and_assembly_evidence = base_evidence_with_splits


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
