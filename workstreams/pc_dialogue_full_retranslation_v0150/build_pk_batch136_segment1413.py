#!/usr/bin/env python3
"""Build source-redacted PK B136 segment 1413 residual decisions."""

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
    "17:99:1", "17:100:0", "17:101:0", "17:101:1",
    "17:102:0", "17:102:1", "17:102:2", "17:103:0",
    "17:104:0", "17:104:1", "17:104:2", "17:104:3",
    "17:105:0", "17:106:0", "17:107:0",
    "17:108:0", "17:108:1", "17:108:2",
    "17:109:0", "17:109:1", "17:109:2", "17:109:3", "17:109:4",
    "17:110:0", "17:111:0", "17:111:1", "17:111:2",
    "17:112:0", "17:113:0", "17:113:1",
    "17:114:0", "17:114:1",
    "17:115:0", "17:115:1", "17:115:2", "17:115:3", "17:115:4",
    "17:116:0", "17:116:1", "17:116:2", "17:117:0",
    "17:118:0", "17:118:1", "17:118:2", "17:118:3", "17:118:4", "17:118:5",
    "17:119:0", "17:119:1", "17:119:2",
    "17:120:0", "17:120:1", "17:120:2",
    "17:121:0", "17:121:1", "17:121:2",
    "17:122:0", "17:123:0", "17:123:1",
    "17:124:0", "17:124:1", "17:125:0",
    "17:126:0", "17:126:1", "17:127:0", "17:127:1", "17:128:0",
)
TRANSLATIONS = {
    "17:99:1": "다!\n병사 한 명도 이곳을 지나게 두지 않겠다!",
    "17:100:0": "큭……!　측면에서도 공격받다니……\n아무래도 오래 버티지는 못하겠군",
    "17:101:0": "다케다군",
    "17:101:1": ", 이토록 강할 줄이야……\n어쩔 수 없다, 물러나라!",
    "17:102:0": "도쿠가와",
    "17:102:1": "의 방어가 무너졌다!\n전군 전진!　",
    "17:102:2": "을(를) 노려라!",
    "17:103:0": "좋은 기회다!\n우리도 밀고 올라가자!",
    "17:104:0": "저",
    "17:104:1": "조차",
    "17:104:2": "다케다",
    "17:104:3": "의 상대가 못 되는가……?\n어찌 이리 강한가……　이럴 수는……",
    "17:105:0": "주군!　이미 아군의 열세는 분명합니다\n저희가 막을 테니 퇴각을 준비하십시오",
    "17:106:0": "그렇군……\n모두, 미안하다……",
    "17:107:0": "은(는) 무사히 달아났는가……",
    "17:108:0": "면목이 없습니다\n수많은 ",
    "17:108:1": "도쿠가와",
    "17:108:2": " 가신이 대신 희생되어……",
    "17:109:0": "됐다, ",
    "17:109:1": "도쿠가와",
    "17:109:2": "군을 격파했다\n이제 ",
    "17:109:3": "미카와 무사들",
    "17:109:4": "의 충의를 칭찬할 뿐이다",
    "17:110:0": "이대로 교토까지 밀고 올라가자!\n모두 승리의 함성을 올려라!",
    "17:111:0": "저곳이",
    "17:111:1": "본진이다!\n전진하라!",
    "17:111:2": "을(를) 놓치지 마라!",
    "17:112:0": "을(를) 협공하라",
    "17:113:0": "을(를) 협공하라",
    "17:113:1": " 성공",
    "17:114:0": "을(를) 협공하라",
    "17:114:1": " 실패",
    "17:115:0": "우리 ",
    "17:115:1": "다케다",
    "17:115:2": "의 상경이\n",
    "17:115:3": "도쿠가와 ",
    "17:115:4": "따위에게 방해받다니……",
    "17:116:0": "은(는) 무서운 속도로 군을 교토로 돌렸습니다\n그 충격으로",
    "17:116:1": "하시바",
    "17:116:2": "군을 돕기로 한 자도 많아\n우리 병력은 크게 열세입니다",
    "17:117:0": "주군의 원군은 역시 오지 않는가……",
    "17:118:0": "쓰쓰이",
    "17:118:1": "군은 ",
    "17:118:2": "야마자키",
    "17:118:3": " 앞에서 진군을 멈췄습니다\n",
    "17:118:4": "아케치",
    "17:118:5": "의 열세가 분명하다고 본 것이겠지요",
    "17:119:0": "하지만, ",
    "17:119:1": "쓰쓰이",
    "17:119:2": "의 원군이 없다면\n이 열세를 뒤집기 어렵다……",
    "17:120:0": "……이렇게 된 이상 어쩔 수 없다!\n기책에 ",
    "17:120:1": "아케치 가문",
    "17:120:2": "의 앞날을 걸겠다!",
    "17:121:0": "!　우선",
    "17:121:1": "덴노잔",
    "17:121:2": "을 탈취하라!\n산에서 본진을 급습하는 척해 적을 위축시켜라",
    "17:122:0": "알겠습니다!\n하지만 정면이 허술해지지 않겠습니까……?",
    "17:123:0": "적은 병력으로 본대를 막기란 어렵지만\n이곳은",
    "17:123:1": "의 분전에 걸겠다!",
    "17:124:0": "이제 각오를 굳힐 수밖에……!\n결단하지 않고서는",
    "17:124:1": "의 야망을 이을 수 없다",
    "17:125:0": "을(를) 격파하라",
    "17:126:0": "을(를) 격파하라",
    "17:126:1": " 성공",
    "17:127:0": "을(를) 격파하라",
    "17:127:1": " 실패",
    "17:128:0": "덴노잔",
}
TARGET_RECORD_IDS = tuple(range(99, 129))
EXPECTED_ARITY = {
    99: 2, 100: 1, 101: 2, 102: 3, 103: 1, 104: 4,
    105: 1, 106: 1, 107: 1, 108: 3, 109: 5, 110: 1,
    111: 3, 112: 1, 113: 2, 114: 2, 115: 5, 116: 3,
    117: 1, 118: 6, 119: 3, 120: 3, 121: 3, 122: 1,
    123: 2, 124: 2, 125: 1, 126: 2, 127: 2, 128: 2,
}
PREFILL_COMPANION_COORDINATES = ("17:99:0", "17:128:1")
PREFILL_COMPANION_DONOR = {
    "17:99:0": "neighbor:S1412",
    "17:128:1": "neighbor:S1414",
}
SPLIT_TRANSLATIONS = {
    "17:99:0": "내가 바로",
    "17:128:1": "을 탈취하라",
}
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
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    record_id: ("9:3792:0", "9:3792:2")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    99: ((), ("024833",)), 100: ((), ()), 101: ((), ()),
    102: ((), ("024835",)), 103: ((), ()),
    104: ((), ("024835",)), 105: ((), ()), 106: ((), ()),
    107: ((), ("024835",)), 108: ((), ()), 109: ((), ()),
    110: ((), ()), 111: ((), ("024834", "024835")),
    112: ((), ()), 113: ((), ()), 114: ((), ()), 115: ((), ()),
    116: ((), ("024835",)), 117: ((), ("024835",)),
    118: ((), ()), 119: ((), ()), 120: ((), ()),
    121: ((), ("024835",)), 122: ((), ()),
    123: ((), ("024834", "024935")), 124: ((), ("024833",)),
    125: ((), ()), 126: ((), ()), 127: ((), ()), 128: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1413, queue_start=67, queue_stop=134,
    slice_first="17:99:1", slice_last="17:128:0",
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
    boundary_record_keys=tuple((17, i) for i in range(58, 154)),
    speaker_style=tuple((i, "historical_event_dialogue") for i in TARGET_RECORD_IDS),
    terminology_policy=(
        ("Tennōzan", "덴노잔"), ("Kyoto", "교토"),
        ("Kyushu tandai", "규슈 단다이"), ("loyalty", "충의"),
        ("pincer attack", "협공"), ("dynamic particles", "은(는), 을(를)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "all sixty-seven visible B136 middle-slice coordinates are manually "
        "reviewed PK-specific event dialogue with pristine JP authoritative; "
        "completed Base event rows provide semantic register context only; "
        "left split record 99 and right split record 128 are completed with "
        "reviewed optional-neighbor fragments, including the coordinated "
        "Tennōzan capture command; historical names, titles, dynamic "
        "particles, whitespace, line breaks, punctuation, complete arity, "
        "pins, reverse overlays, tamper rejection, outside-scope identity, "
        "optional neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=26,
    pins={
        "expected_queue_universe_sha256": "9875C5BDFC630EE0ACB5EB425F8ADE458E850FCAF249DD388A37E7336B631D1B",
        "expected_queue_slice_sha256": "93BE1967FF034E2E6E47116FEEC90792656AF0ED8128F59112C6308D5F0F8016",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "93BE1967FF034E2E6E47116FEEC90792656AF0ED8128F59112C6308D5F0F8016",
        "expected_source_target_sha256": "D54FE97F538EE7AEB4C9DAAED601E8DEE2D655DA8089D25FAD65E67DEAB907B5",
        "expected_current_target_sha256": "67EAAAF84AA924B7ACD1471B04C51467410C6E82B56655055C3D79FFFE1A5334",
        "expected_context_corpus_sha256": "02EB336E27DC8BD87228E49E57CB46F10056DE13C4F4FFCC4BDFE71D3A645836",
        "expected_gap_contract_sha256": "82F60FF8F686AD47486BCEBE70482921656335C46CBCBC16BFBA14127764ECCD",
        "expected_boundary_sha256": "BC33F6442EDEBC6EBEC92C3DB94BDFADAA71753942624AB034E0E70638311609",
        "expected_runtime_control_sha256": "5C79745368EAEF27DDB77E3AA2C883504C1CC68055AA266275FE5760E6C1877F",
        "expected_base_search_sha256": "04FA5CD7FCD546747B9E2FD3ED1D2B506A540F3E4845272A9B9A4C6BA8D2FB32",
        "expected_complete_assembly_sha256": "C013E5A33CA83364C028E05F4041794D0DE0EF72A2B1224673538788CFF6CE08",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "F482C532A06B180A178B07EA0A2B4E617318D5AC661D96B064C434C05B3D077D",
        "expected_terminology_policy_sha256": "6D13423ED9E03899AEA6E9B5E8EBA00C0527E2B2E7856BD34E046613D47380AC",
        "expected_translation_policy_sha256": "B7BB048C3FD6EBC753E245D607618DDC61D95FF58850B34D451AF36C7C1BAADA",
        "expected_candidate_sha256": "1D84CBCF4D85042638B67C7D707E17F864E942638E9172A9CF61E1231C3F4236",
        "expected_combined_slice_candidate_sha256": "1D84CBCF4D85042638B67C7D707E17F864E942638E9172A9CF61E1231C3F4236",
        "expected_combined_changed_literal_count": 26,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B136_S1413",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B136_S1413.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B136_S1412.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B136_S1414.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B136", "queue_row_count": 96,
    "queue_visible_count": 198, "queue_first": "17:58:0",
    "queue_last": "17:153:0",
})


def read_jsonl_with_splits(path: Path) -> tuple[dict[str, Any], ...]:
    rows = tuple(_ORIGINAL_READ_JSONL(path))
    if path.resolve(strict=False) == COMMON.PREFILL.resolve(strict=False):
        return rows + SYNTHETIC_ROWS
    return rows


def base_evidence_with_splits(prepared: Any, records: dict[str, Any]) -> Any:
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
            raise RuntimeError(f"segment 1413 split neighbor drifted: {coordinate}")
    return _ORIGINAL_BASE_EVIDENCE(prepared, records)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


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
