#!/usr/bin/env python3
"""Build Base authoring segment 747 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S747.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s747", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:93:0": '불초 "',
    "13:93:1": '"은(는) "',
    "13:93:2": '"이라는\n특성을 지니고 있으니\n믿고 맡겨 주십시오!',
    "13:94:0": '가신 중에서는 "',
    "13:94:1": '"이(가)\n',
    "13:94:2": "이라는\n특성을 지니고 있어 믿음직한 인재입니다",
    "13:95:0": '병사를 지휘하는 능력이 뛰어난 가신이라면\n우선 "',
    "13:95:1": '"의 이름이 떠오릅니다\n출진할 때 참고해 주십시오…',
    "13:96:0": '전투에서 가장 믿음직한 가신이라면\n우선 "',
    "13:96:1": '"님이시겠군요\n우리 가문에서 가장 뛰어난 전투의 달인입니다',
    "13:97:0": "우리 가문에서 으뜸가는 지략가라면\n",
    "13:97:1": "님 말고는 없을 것입니다\n조략과 외교에서 재능을 발휘할 것입니다",
    "13:98:0": '영지의 발전을 생각하신다면\n정무에 능한 "',
    "13:98:1": '"님을\n내정의 중심으로 삼으시면 좋겠습니다',
    "13:99:0": '님이 지닌 "',
    "13:99:1": '"의 자질은\n우리 가문에서도 손꼽힐 만큼 뛰어나니\n주군의 패업을 뒷받침할 것입니다',
    "13:100:0": "외람된 말씀이오나 이",
    "13:100:1": "\n병사를 지휘하는 기량만큼은\n우리 가문에서 저를 능가할 자가 없을 것입니다…",
    "13:101:0": '또한 전장에서의 무용이라면\n이 "',
    "13:101:1": '"야말로 우리 가문에서 으뜸이라고\n자부하고 있습니다…',
    "13:102:0": '또한 이 "',
    "13:102:1": '"은(는)\n조략과 외교에 자신이 있으니\n그 방면에서 재능을 발휘하고 싶습니다…',
    "13:103:0": '영지의 발전을 생각하신다면\n정무에 능한 이 "',
    "13:103:1": '"에게\n내정을 맡겨 주시기를 바랍니다…',
    "13:104:0": '외람되오나 "',
    "13:104:1": '"에 관한 한\n우리 가문에서 이 "',
    "13:104:2": '"에\n견줄 자는 없을 것입니다…',
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)
EXPECTED_GAPS = {
    93: (b"", b"\x01\x43\x01\x00\x00\x00", b"\x02\x3c", b"\x05\x05\x05"),
    94: (b"", b"\x01\x43\x1d\x00\x00\x00", b"\x02\x3c", b"\x05\x05\x05"),
    95: (b"", b"\x02\x48\x33", b"\x05\x05\x05"),
    96: (b"", b"\x02\x48\x33", b"\x05\x05\x05"),
    97: (b"", b"\x02\x48\x33", b"\x05\x05\x05"),
    98: (b"", b"\x02\x48\x33", b"\x05\x05\x05"),
    99: (b"\x02\x48\x33", b"\x02\x3c", b"\x05\x05\x05"),
    100: (b"", b"\x02\x46\x35", b"\x05\x05\x05"),
    101: (b"", b"\x02\x46\x35", b"\x05\x05\x05"),
    102: (b"", b"\x02\x46\x35", b"\x05\x05\x05"),
    103: (b"", b"\x02\x46\x35", b"\x05\x05\x05"),
    104: (b"", b"\x02\x3c", b"\x02\x46\x35", b"\x05\x05\x05"),
}


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def assert_runtime_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")
    if len(TRANSLATIONS) != 27:
        raise RuntimeError("segment 747 must contain exactly 27 visible decisions")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_runtime_scope(prepared)
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
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
                "segment": "base_msggame_B001_S747",
                "decision_count": len(rows),
                "retranslated": 0,
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
