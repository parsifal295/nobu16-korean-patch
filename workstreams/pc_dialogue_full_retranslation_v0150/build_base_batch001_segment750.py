#!/usr/bin/env python3
"""Build Base authoring segment 750 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S750.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s750", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:125:0": '다만 이 "',
    "13:125:1": '"은(는) 지략에도 자신이\n',
    "13:125:2": "조략이나 외교 등의\n분야에서 재능을 발휘하고 싶습니다…",
    "13:126:0": '영토의 발전을 생각하신다면\n정무에 능한 이 "',
    "13:126:1": '"의 재능이\n반드시 도움이 될 날이 오',
    "13:127:0": "게다가 특성도 남들만큼은 갖추고 있으니\n부디 재능을 발휘할 자리를\n마련해 주십시오",
    "13:128:0": "부끄러운 말씀이오나 특성은 없으니\n지닌 능력을 살릴 자리를 마련해 주신다면\n더없이 감사하겠습니다…",
    "13:129:0": "그렇다고 해도 현재 우리 가문을 섬기는 이는\n",
    "13:129:1": "밖에 없사옵니다. 하루빨리\n재야 무장을 등용하여 진용을 갖춰야겠습니다…",
    "13:130:0": "그 밖에도 든든한 가신은\n아직 많이 있사옵니다\n인재를 적재적소에 활용하는 것이 중요합니다",
    "13:131:0": "좋다!\u3000이를 바탕으로\n군을, 그리고 나라를 강하게 만들자!\n모두 함께 나아가자!",
    "13:132:0": "말할 것도 없다!\u3000우리의 명운은\n",
    "13:132:1": "와(과) 함께하옵니다\n무엇이든 명해 주십시오!",
    "13:134:0": "용맹한 말이로다!\u3000훌륭한 가신들의 진언도\n적극적으로 받아들이겠다!\n뜻을 하나로 모아 천하통일을 향해 매진하겠다!",
    "13:135:0": "예!\n",
    "13:135:1": "의 야망을 반드시 이루어 내겠습니다!",
    "13:136:0": "모두 수고했다!\n지금부터 평정을 시작한다!\n고개를 들라!",
    "13:137:0": "들으라!\n우리 가문은 이제부터 천하통일에 나선다!\n각자 마음껏 계책을 내놓아라!",
    "13:138:0": "분부대로 하겠습니다!",
    "13:139:0": "천하를 노리려면 영토를 넓히고\n모든 다이묘에게 우리의 힘을 인정받아야 합니다",
    "13:140:0": "지금부터 평정을 시작한다!",
    "13:141:0": "우리 가문은 아직 강대한 세력이라 할 수 없으나\n나의 야망은 이 땅에 머무르지 않는다!\n이제부터 '",
    "13:141:1": "'은(는) 천하를 노린다!",
}

RUNTIME_RECORD_IDS = {125, 126, 129, 132, 135, 141}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_RUNTIME_GAPS = {
    125: (b"", b"\x02\x46\x35", b"\x01\x43\x5e\x00\x00\x00", b"\x05\x05\x05"),
    126: (b"", b"\x02\x46\x35", b"\x01\x43\x1e\x04\x00\x00\x05\x05\x05"),
    129: (b"", b"\x01\x43\x01\x00\x00\x00", b"\x05\x05\x05"),
    132: (b"", b"\x02\x50\x32", b"\x05\x05\x05"),
    135: (b"", b"\x02\x50\x32", b"\x05\x05\x05"),
    141: (b"", b"\x01\x43\x01\x00\x00\x00", b"\x05\x05\x05"),
}
EXPECTED_MERGED_LITERAL_COUNTS = {
    127: (2, 1),
    128: (2, 1),
    136: (2, 1),
}
B091_EXACT_REUSE = {
    "13:136:0": "모두 수고했다!\n지금부터 평정을 시작한다!\n고개를 들라!",
    "13:137:0": "들으라!\n우리 가문은 이제부터 천하통일에 나선다!\n각자 마음껏 계책을 내놓아라!",
    "13:138:0": "분부대로 하겠습니다!",
    "13:140:0": "지금부터 평정을 시작한다!",
    "13:141:0": "우리 가문은 아직 강대한 세력이라 할 수 없으나\n나의 야망은 이 땅에 머무르지 않는다!\n이제부터 '",
    "13:141:1": "'은(는) 천하를 노린다!",
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def assert_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_RUNTIME_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine runtime skeleton drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current runtime skeleton drifted: 13:{record_id}")
    for record_id, expected in EXPECTED_MERGED_LITERAL_COUNTS.items():
        actual = (
            len(ENGINE.parse_record_literals(source_records[(13, record_id)])),
            len(ENGINE.parse_record_literals(current_records[(13, record_id)])),
        )
        if actual != expected:
            raise RuntimeError(f"merged-literal authority drifted at 13:{record_id}: {actual}")
        if record_gaps(current_records[(13, record_id)]) != (b"", b"\x05\x05\x05"):
            raise RuntimeError(f"merged current record retains an unexpected opcode: 13:{record_id}")
    source_blank = ENGINE.parse_record_literals(source_records[(13, 133)])
    current_blank = ENGINE.parse_record_literals(current_records[(13, 133)])
    if [literal.text for literal in source_blank] != [""] or [literal.text for literal in current_blank] != [""]:
        raise RuntimeError("13:133 must remain a single blank, undecided literal")
    if set(TRANSLATIONS) & {"13:133:0"}:
        raise RuntimeError("blank 13:133 must not receive a decision")
    if any(TRANSLATIONS[coordinate] != translation for coordinate, translation in B091_EXACT_REUSE.items()):
        raise RuntimeError("B091 exact-reuse translation drifted")
    if len(TRANSLATIONS) != 23 or len(DYNAMIC_RUNTIME_COORDINATES) != 13:
        raise RuntimeError("segment 750 visible/static-runtime counts drifted")
    u3000_counts = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if u3000_counts != {"13:131:0": 1, "13:132:0": 1, "13:134:0": 1}:
        raise RuntimeError(f"segment 750 U+3000 scope drifted: {u3000_counts}")
    for translation in TRANSLATIONS.values():
        if "\r" in translation:
            raise RuntimeError("segment 750 must not add CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 750 retains banned fullwidth punctuation")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_same_coordinate_pk_jp_en_sc_tc_context_where_available"
                ),
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S750",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": 0,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
