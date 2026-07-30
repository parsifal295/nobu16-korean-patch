#!/usr/bin/env python3
"""Build source-redacted PK B138 segment 1419 residual decisions."""

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
    "17:279:2", "17:280:0", "17:281:0", "17:281:1",
    "17:282:0", "17:283:0", "17:284:0", "17:284:1",
    "17:284:2", "17:285:0", "17:285:1", "17:286:0",
    "17:286:1", "17:287:0", "17:287:1", "17:287:2",
    "17:288:0", "17:288:1", "17:288:2", "17:288:3",
    "17:289:0", "17:290:0", "17:291:0", "17:291:1",
    "17:291:2", "17:292:0", "17:292:1", "17:293:0",
    "17:293:1", "17:294:0", "17:295:0", "17:296:0",
    "17:296:1", "17:297:0", "17:297:1", "17:298:0",
    "17:298:1", "17:299:0", "17:300:0", "17:300:1",
    "17:300:2", "17:301:0", "17:301:1", "17:301:2",
    "17:302:0", "17:302:1", "17:302:2", "17:303:0",
    "17:303:1", "17:304:0", "17:304:1", "17:304:2",
    "17:305:0", "17:305:1", "17:305:2", "17:306:0",
    "17:306:1", "17:306:2", "17:307:0", "17:307:1",
    "17:308:0", "17:309:0", "17:309:1", "17:310:0",
    "17:310:1", "17:311:0", "17:312:0",
)
TRANSLATIONS = {
    "17:279:2": "… 네게 승리를 안겨 주지 못했구나…",
    "17:280:0": "주군… 지켜 드리지 못했나…",
    "17:281:0": "남은 것은",
    "17:281:1": "뿐이다!\n전군 전진! 반드시 쓰러뜨려라!",
    "17:282:0": "여기까지인가…\n미안하다, Color.Blue 지부 Color.Default. 네게 승리를 안겨 주지 못했구나…",
    "17:283:0": "주군… 지켜 드리지 못했나…",
    "17:284:0": "때가 됐군… 우리는",
    "17:284:1": "의 편에 선다!\n노릴 것은",
    "17:284:2": "의 목이다! 진군을 시작하라!",
    "17:285:0": "가 배신했나!\n우리도 이 기회를 틈타",
    "17:285:1": "를 쓰러뜨리자!",
    "17:286:0": "이제는",
    "17:286:1": "뿐이다!\n전군 진격! 쓰러뜨려라!",
    "17:287:0": "공…　",
    "17:287:1": "태합",
    "17:287:2": "전하…\n면목이 없습니다…",
    "17:288:0": "간신",
    "17:288:1": "은 제거됐고\n주군",
    "17:288:2": "히데요리",
    "17:288:3": "공을 해칠 자도 사라졌다!",
    "17:289:0": "승전 함성을 올려라!\n이제 우리 천하는 평안하리라!",
    "17:290:0": "(내 천하가 말이지…)",
    "17:291:0": "이 싸움은 패전이다, 우리 시마즈는 철수한다!\n",
    "17:291:1": "이세 가도",
    "17:291:2": "으로 진군하라!",
    "17:292:0": "요시히로",
    "17:292:1": "님을 무사히 모셔야 한다\n정신 바짝 차려라!",
    "17:293:0": "도요히사",
    "17:293:1": "…그대 덕분에 여기까지 왔다…\n시마즈는 내게 맡겨라…",
    "17:294:0": "패배인가! 내가 지는 것인가!\n때를 기다리고 또 기다린 끝이 이것인가!",
    "17:295:0": "의 부대가 바로 앞이다!\n전군 전진! 반드시 쓰러뜨려라!",
    "17:296:0": "목표 2개를 달성하라 (",
    "17:296:1": "/2)",
    "17:297:0": "목표 2개를 달성하라",
    "17:297:1": " 성공",
    "17:298:0": "목표 2개를 달성하라",
    "17:298:1": " 실패",
    "17:299:0": "목표 2개를 달성하라",
    "17:300:0": "요충지 총",
    "17:300:1": "4곳을 제압하라 (",
    "17:300:2": "/4)",
    "17:301:0": "요충지 ",
    "17:301:1": "4곳을 제압하라",
    "17:301:2": " 성공",
    "17:302:0": "요충지 ",
    "17:302:1": "4곳을 제압하라",
    "17:302:2": " 실패",
    "17:303:0": "요충지 ",
    "17:303:1": "4곳을 제압하라",
    "17:304:0": "적군 총",
    "17:304:1": "4개 부대를 격파하라 (",
    "17:304:2": "/4)",
    "17:305:0": "적군 ",
    "17:305:1": "4개 부대를 격파하라",
    "17:305:2": " 성공",
    "17:306:0": "적군 ",
    "17:306:1": "4개 부대를 격파하라",
    "17:306:2": " 실패",
    "17:307:0": "적군 ",
    "17:307:1": "4개 부대를 격파하라",
    "17:308:0": "부대를 격파하라",
    "17:309:0": "부대를 격파하라",
    "17:309:1": " 성공",
    "17:310:0": "부대를 격파하라",
    "17:310:1": " 실패",
    "17:311:0": "부대를 격파하라",
    "17:312:0": "부대를 격파하라",
}
TARGET_RECORD_IDS = tuple(range(279, 313))
EXPECTED_ARITY = {
    279: 3, 280: 1, 281: 2, 282: 1, 283: 1, 284: 3,
    285: 2, 286: 2, 287: 3, 288: 4, 289: 1, 290: 1,
    291: 3, 292: 2, 293: 2, 294: 1, 295: 1, 296: 2,
    297: 2, 298: 2, 299: 1, 300: 3, 301: 3, 302: 3,
    303: 2, 304: 3, 305: 3, 306: 3, 307: 2, 308: 1,
    309: 2, 310: 2, 311: 1, 312: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "17:279:0", "17:279:1", "17:312:1",
)
PREFILL_COMPANION_DONOR = {
    "17:279:0": "neighbor:S1418",
    "17:279:1": "neighbor:S1418",
    "17:312:1": "neighbor:S1420",
}
SPLIT_TRANSLATIONS = {
    "17:279:0": "여기까지인가…\n미안하다",
    "17:279:1": ", 지부",
    "17:312:1": " 성공",
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
    record_id: ("9:400:0", "9:401:0", "9:444:0", "8:465:0")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    280: ((), ("024835",)),
    281: ((), ("024833",)),
    283: ((), ("024835",)),
    284: ((), ("024835", "024935")),
    285: ((), ("024834", "024935")),
    286: ((), ("024835",)),
    287: ((), ("024735",)),
    288: ((), ("024833",)),
    295: ((), ("024834",)),
    296: ((), ("0232",)),
    300: ((), ("0232",)),
    304: ((), ("0232",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1419, queue_start=67, queue_stop=134,
    slice_first="17:279:2", slice_last="17:312:0",
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
    boundary_record_keys=tuple((17, i) for i in range(249, 347)),
    speaker_style=tuple(
        (i, "historical_event_or_objective_text")
        for i in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Jibu", "지부"),
        ("Taikō", "태합"),
        ("Hideyori", "히데요리"),
        ("Ise route", "이세 가도"),
        ("key point", "요충지"),
        ("enemy unit", "적군 부대"),
        ("project long ellipsis", "…"),
    ),
    basis=(
        "all sixty-seven visible B138 middle-slice coordinates are manually "
        "reviewed against pristine PK JP and available PK EN SC TC context; "
        "completed Base battle, key-point and defeat rows provide semantic "
        "register context only; the left Jibu defeat line and right unit-"
        "defeat success objective are completed with reviewed optional-"
        "neighbor fragments; malformed dynamic-token spacing, literal "
        "Japanese punctuation, Ise route terminology and objective counter "
        "formatting are corrected while tags, controls, whitespace, complete "
        "arity, pins, reverse overlays, tamper rejection, outside-scope "
        "identity, optional neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=17,
    pins={
        "expected_queue_universe_sha256": "4EDC588F91DEC58F97ACA4C16FF4150DCECBB90ED1372150DD2021A8EC01B24E",
        "expected_queue_slice_sha256": "AAA9014BB8BCB867ED4750CC6163B119B436B4C9CF353B184823080E1F5BD574",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "AAA9014BB8BCB867ED4750CC6163B119B436B4C9CF353B184823080E1F5BD574",
        "expected_source_target_sha256": "6446C4631819A3E51A631BC81971E27671DDA84688E1E982CA505777802021DD",
        "expected_current_target_sha256": "11A9F01916B0A1AAA7D06C26915949E5B6901FEDFC4DC2571C8B8DE8845178AB",
        "expected_context_corpus_sha256": "09CA07A2EEB63A33AAFF03821C355C81D5F91E090F8817DF174B573C93FC4623",
        "expected_gap_contract_sha256": "331C44A89FCC3B4BF8DE27E623BACC46981A56F0543881F639884D95DD1E6C77",
        "expected_boundary_sha256": "8E953825692F6A37F195BFE5CC00E2990CF38BF75FF79B74FC5727AA98C6B3FC",
        "expected_runtime_control_sha256": "9FCCC283E1734908A97F316E8F269C93905ECC03388A3A4143F92DCA12F1A633",
        "expected_base_search_sha256": "A1B0F404BCA1970204D10E76CA92F9F6F88506D6B3E008DD8D8D424098CAF387",
        "expected_complete_assembly_sha256": "333959D9FA21EC4E76FFAD98FDDF95F209D503F809C78C8C25914C0D4D4D3ABC",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "CF7A52CC239D609DC72E67E496774CA4025BC63F13C64EEFA63BF823D98D3EEF",
        "expected_terminology_policy_sha256": "55788E5F3DC5A1CB351599789914375FB6FFF56C92D75D7554BBD52247EBC130",
        "expected_translation_policy_sha256": "24BBE52C7300EBB71CB05787744EE47CC8E51B4105EA22CA3098CBDBFC193D32",
        "expected_candidate_sha256": "6692D35B706D910B81E696BADCFC4B9D8A837670CF125E332DDD23AB5D854A39",
        "expected_combined_slice_candidate_sha256": "6692D35B706D910B81E696BADCFC4B9D8A837670CF125E332DDD23AB5D854A39",
        "expected_combined_changed_literal_count": 17,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B138_S1419",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B138_S1419.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B138_S1418.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B138", "queue_row_count": 98,
    "queue_visible_count": 200, "queue_first": "17:249:0",
    "queue_last": "17:346:1",
})
RECIPROCAL_NEIGHBORS = (
    COMMON.DECISIONS_ROOT / "pk_msggame_B138_S1418.private.v1.jsonl",
    COMMON.DECISIONS_ROOT / "pk_msggame_B138_S1420.private.v1.jsonl",
)


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
        for path in RECIPROCAL_NEIGHBORS if path.is_file()
        for row in _ORIGINAL_READ_JSONL(path)
    }
    for coordinate, expected in SPLIT_TRANSLATIONS.items():
        row = neighbors.get(coordinate)
        if row is not None and (
            row.get("translation") != expected
            or row.get("semantic_review") != "approved"
        ):
            raise RuntimeError(
                f"segment 1419 split neighbor drifted: {coordinate}"
            )
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
