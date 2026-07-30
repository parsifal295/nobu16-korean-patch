#!/usr/bin/env python3
"""Build source-redacted PK B137 segment 1416 residual decisions."""

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
    "17:181:2", "17:182:0", "17:182:1", "17:182:2",
    "17:183:0", "17:184:0", "17:185:0", "17:186:0",
    "17:186:1", "17:187:0", "17:187:1", "17:187:2",
    "17:188:0", "17:188:1", "17:188:2", "17:189:0",
    "17:189:1", "17:190:0", "17:191:0", "17:192:0",
    "17:192:1", "17:192:2", "17:193:0", "17:193:1",
    "17:194:0", "17:195:0", "17:196:0", "17:196:1",
    "17:196:2", "17:197:0", "17:197:1", "17:197:2",
    "17:197:3", "17:198:0", "17:198:1", "17:198:2",
    "17:198:3", "17:199:0", "17:199:1", "17:200:0",
    "17:201:0", "17:202:0", "17:203:0", "17:204:0",
    "17:204:1", "17:204:2", "17:205:0", "17:205:1",
    "17:206:0", "17:207:0", "17:208:0", "17:209:0",
    "17:209:1", "17:209:2", "17:209:3", "17:210:0",
    "17:210:1", "17:211:0", "17:211:1", "17:211:2",
    "17:212:0", "17:213:0", "17:214:0", "17:215:0",
    "17:216:0", "17:216:1", "17:216:2",
)
TRANSLATIONS = {
    "17:181:2": " 실패",
    "17:182:0": "무사히 ",
    "17:182:1": "덴노잔",
    "17:182:2": "을 제압했군!\n이대로 나머지 요충지도 빼앗자!",
    "17:183:0": "오, 여기서는\n적의 움직임이 잘 보이는군…",
    "17:184:0": "음? 오른쪽 저 숲속 깊은 곳…\n혹시 길이 나 있는 것 아닌가?",
    "17:185:0": "기습할 절호의 기회다!\n서둘러 주군께 전령을 보내라!",
    "17:186:0": "숲가의 요충지",
    "17:186:1": "를 차지하라",
    "17:187:0": "숲가의 요충지",
    "17:187:1": "를 차지하라",
    "17:187:2": " 성공",
    "17:188:0": "숲가의 요충지",
    "17:188:1": "를 차지하라",
    "17:188:2": " 실패",
    "17:189:0": "덴노잔",
    "17:189:1": "을 먼저 빼앗기다니…\n서둘러 탈환하라!",
    "17:190:0": "기회다! 공격하라!",
    "17:191:0": "측면에서 적이!?\n대체 어디에서…",
    "17:192:0": "좋아!　",
    "17:192:1": "의 작전대로다!\n이제",
    "17:192:2": "만 쓰러뜨리면 된다!",
    "17:193:0": "선봉의 양옆을 빼앗겼다고!?\n이 용병술은 바로",
    "17:193:1": "인가…!",
    "17:194:0": "좌우에서 포위당했다…!?\n물러나라! 이대로면 독 안에 든 쥐다!",
    "17:195:0": "전군, 물러서라! 주군을 지켜라!",
    "17:196:0": "아군 진지의 ",
    "17:196:1": "요충지",
    "17:196:2": "를 지켜라",
    "17:197:0": "아군 진지의 ",
    "17:197:1": "요충지",
    "17:197:2": "를 지켜라",
    "17:197:3": " 성공",
    "17:198:0": "아군 진지의 ",
    "17:198:1": "요충지",
    "17:198:2": "를 지켜라!",
    "17:198:3": " 실패",
    "17:199:0": "의 본대가 저곳이다!\n전군 전진!",
    "17:199:1": "의 목을 베어라!",
    "17:200:0": "요충지를 빼앗기다니…\n이래서는 내 계책이…",
    "17:201:0": "의 진지가 코앞이다!\n전군, 계속 돌격!",
    "17:202:0": "계책이 없어도 병사는 충분하다!\n무슨 수를 써서라도 적의 공세를 막아라!",
    "17:203:0": "천하가 내 손에서 빠져나간다…\n때는 지금이 아니었던가…",
    "17:204:0": "역적",
    "17:204:1": "은 패했다!\n",
    "17:204:2": "님의 유지는 우리가 잇겠다!",
    "17:205:0": "! 어찌하여",
    "17:205:1": "님을 죽였느냐!\n그토록 큰 은혜를 입고도…!",
    "17:206:0": "가 만든 천하는 내가 바라던 천하가 아니다…\n그저 그뿐이다!",
    "17:207:0": "인가… 강적이지만…\n주군의 새로운 천하를 위해 이곳은 양보할 수 없다",
    "17:208:0": "주군의 뜻을 꺾기는 안타깝지만…\n우리의 야망도 이곳에서 끝낼 수는 없다",
    "17:209:0": "숲가의 요충지",
    "17:209:1": "를 차지했나!\n이어서",
    "17:209:2": "덴노잔",
    "17:209:3": "도 빼앗아라!",
    "17:210:0": "선봉의 양옆을 빼앗겼다고!?\n이 용병술은 바로",
    "17:210:1": "인가…!",
    "17:211:0": "내 그릇으로는 천하에 닿지 못하는가…\n",
    "17:211:1": ", ",
    "17:211:2": ", 미안하다…",
    "17:212:0": "요충지 제압",
    "17:213:0": "요충지 사수",
    "17:214:0": "무장 격파",
    "17:215:0": "전투 전법",
    "17:216:0": "예상대로, ",
    "17:216:1": "이시다",
    "17:216:2": " 일파를\n",
}
TARGET_RECORD_IDS = tuple(range(181, 217))
EXPECTED_ARITY = {
    181: 3, 182: 3, 183: 1, 184: 1, 185: 1, 186: 2,
    187: 3, 188: 3, 189: 2, 190: 1, 191: 1, 192: 3,
    193: 2, 194: 1, 195: 1, 196: 3, 197: 4, 198: 4,
    199: 2, 200: 1, 201: 1, 202: 1, 203: 1, 204: 3,
    205: 2, 206: 1, 207: 1, 208: 1, 209: 4, 210: 2,
    211: 3, 212: 1, 213: 1, 214: 1, 215: 1, 216: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "17:181:0", "17:181:1", "17:216:3", "17:216:4",
)
PREFILL_COMPANION_DONOR = {
    "17:181:0": "neighbor:S1414",
    "17:181:1": "neighbor:S1414",
    "17:216:3": "neighbor:S1417",
    "17:216:4": "neighbor:S1417",
}
SPLIT_TRANSLATIONS = {
    "17:181:0": "덴노잔",
    "17:181:1": "을 탈취하라",
    "17:216:3": "세키가하라",
    "17:216:4": "로 끌어내는 데 성공했다\n이제 일격에 놈들을 섬멸할 뿐이다",
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
    192: ((), ("024835", "024935")),
    193: ((), ("024833",)),
    199: ((), ("024835", "024833")),
    201: ((), ("024835",)),
    204: ((), ("024833", "024935")),
    205: ((), ("024835", "024935")),
    206: ((), ("024835",)),
    207: ((), ("024833",)),
    208: ((), ("024834",)),
    210: ((), ("024833",)),
    211: ((), ("024835", "024935")),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1416, queue_start=67, queue_stop=134,
    slice_first="17:181:2", slice_last="17:216:2",
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
    boundary_record_keys=tuple((17, i) for i in range(154, 249)),
    speaker_style=tuple(
        (i, "historical_event_dialogue") for i in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Tennōzan", "덴노잔"),
        ("Sekigahara", "세키가하라"),
        ("Ishida", "이시다"),
        ("key point", "요충지"),
        ("lord", "주군"),
        ("traitor", "역적"),
        ("project long ellipsis", "…"),
    ),
    basis=(
        "all sixty-seven visible B137 middle-slice coordinates are manually "
        "reviewed against pristine PK JP and complete PK EN SC TC context; "
        "completed Base battle, key-point and defeat rows provide semantic "
        "register context only; the left Tennōzan objective result and right "
        "Ishida-Sekigahara plan are completed with reviewed optional-neighbor "
        "fragments; awkward dynamic-name punctuation is corrected while "
        "historical names, titles, particles, whitespace, line breaks, "
        "punctuation, complete arity, pins, reverse overlays, tamper rejection, "
        "outside-scope identity, optional neighbors and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=3,
    pins={
        "expected_queue_universe_sha256": "AA6B64E39166A50CF7D456140DFC053DCB88E80C33120BAFFADE06C49C921E0D",
        "expected_queue_slice_sha256": "658820C92F1A130FAA65970FDFBE288B30F05FFC6ECB433EE023C101CCF2DC64",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "658820C92F1A130FAA65970FDFBE288B30F05FFC6ECB433EE023C101CCF2DC64",
        "expected_source_target_sha256": "CDD88512993EAC8657DB46E657FD17C9ADEBD5374CA2B5D40DCFE11F5E849FE5",
        "expected_current_target_sha256": "CEB9FB7DCE7D9664DA7AD3F7B2C6E6732FA5DCDBBF0835BAD4111642F323012C",
        "expected_context_corpus_sha256": "B542EDCA0F2044E694BE2A20C0C8015569380470245117D24C4B915CE072C772",
        "expected_gap_contract_sha256": "A7D44D79DE484C7E3BDBF7556CDC256B9431B39B85B7A5CE5219780B81FDCE0B",
        "expected_boundary_sha256": "0387829D0FC6D48E3AD2791610A9B3C0D3D36FC25BD4F2989CE6C1C3BEA5D985",
        "expected_runtime_control_sha256": "BC846ED1F11162452237745E6AFA7DB47E81BA965683DA6D8835E320E4644F10",
        "expected_base_search_sha256": "5B23057C8826ADCD80B84E0835DCF136C82B3615AEB898A63226DEE1632E8E09",
        "expected_complete_assembly_sha256": "7CDE787BFD8885E8560AFE5CEF9DBBA0F2D72E68185219A79E41F6095ADB68F4",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "E47CB28AACCADF12B3B958349EE9DA628D16E822B5B757A4DC3A980CA491FD47",
        "expected_terminology_policy_sha256": "CA931638E2A0A9BFC1A6322AC37119B261521F32D8F007DF06D22A5875F1C9FB",
        "expected_translation_policy_sha256": "1EFAE7FF921DC6A32CE4488811DB1590462D499A7DA69E08C9FCF2B6742B87DA",
        "expected_candidate_sha256": "A5C1A67C1043FDCBFE06C661255B0301F7754DB0A69EFC5381BAD7C9CFCCDD44",
        "expected_combined_slice_candidate_sha256": "A5C1A67C1043FDCBFE06C661255B0301F7754DB0A69EFC5381BAD7C9CFCCDD44",
        "expected_combined_changed_literal_count": 3,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B137_S1416",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B137_S1416.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B137_S1415.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B137_S1417.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B137", "queue_row_count": 95,
    "queue_visible_count": 199, "queue_first": "17:154:0",
    "queue_last": "17:248:2",
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
                f"segment 1416 split neighbor drifted: {coordinate}"
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
