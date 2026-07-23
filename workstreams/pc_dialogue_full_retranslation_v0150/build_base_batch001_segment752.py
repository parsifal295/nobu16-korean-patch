#!/usr/bin/env python3
"""Build Base authoring segment 752 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S752.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s752", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:162:0": "은(는)",
    "13:162:1": "이(가) 머무는 성,\n곧 다이묘의 성이며, 본거지라고 합니다\n다른 성은 가신이 성주로서 다스립니다",
    "13:163:0": "성은 성주가 다스리는 것이 기본입니다\n본거지는",
    "13:163:1": "이(가) 성주이기도 하므로\n직접 명령하여 발전시켜야 합니다",
    "13:164:0": "성은 성주가 다스리는 것이 기본입니다\n본거지는",
    "13:164:1": "이(가) 성주이기도 하므로\n직접 명령하여 발전시켜야 합니다",
    "13:165:0": "그렇군, 본거지는 직접 발전시키고\n다른 성은 성주에게 맡기는 것인가…\n하지만 모두 맡겨 두어도 괜찮은가?",
    "13:166:0": "자세한 설명은 다음 기회에 드리겠습니다만\n성주가 지시를 청해 올 때도 있으니\n그때는 직접 명령해 주십시오",
    "13:167:0": "다음으로 이 그림을 봐 주십시오\n성은 주변 토지인 '군'을\n지배 아래에 두고 있습니다",
    "13:168:0": "예를 들어 우리 본거지는\n이처럼 여러 군으로 이루어져 있고…",
    "13:169:0": "군에서 거둔 금전 수입은 다이묘에게 보내고,\n병량 수입은 성에 비축하여\n부대가 출진할 때 사용합니다",
    "13:170:0": "성과 군을 가신에게 맡기면\n영지는 더욱 발전하고 수입도 늘어나\n성은 한층 강해질 것입니다",
    "13:171:0": "이(가) 머무는 본거지 외의\n성과 군은 가신에게 내주어 맡김으로써\n더욱 강해지는 것이로군",
    "13:172:0": "그렇습니다. 영지를 가신에게 내리는 제도를\n지행이라 합니다\n우선 지행의 중요성을 헤아려 주십시오",
    "13:173:0": "같은 가신이라 해도\n여러 신분이 있었을 터인데…\n어디 보자… 무엇이었더라",
    "13:174:0": "낮은 순서부터\n조두, 아시가루 대장, 사무라이 대장, 부장, 가로, 숙로\n이렇게 여섯 신분이 있습니다",
    "13:175:0": "출세하려면 훈공이 필요합니다\n아무런 성과도 내지 못한 자를\n출세시킬 수는 없기 때문입니다",
    "13:176:0": "합전에서 활약하거나 군을 다스려\n훈공을 인정받으면 출세의 길이\n열린다는 말이군",
    "13:177:0": "그렇군, 군을 영지로 내리려면\n아시가루 대장 이상의 신분이 필요한 것이군",
    "13:178:0": "우선 본거지에 속한 군의 대관으로\n훈공을 세우고 신분을 올린 뒤\n지행지를 맡기는 것이 좋겠습니다",
    "13:179:0": "가신의 신분이 올라가면\n성주나 군단장으로 임명하는 것도\n가능해집니다",
    "13:180:0": "눈여겨본 무장에게는 적극적으로\n일을 맡겨 훈공을 세우게 해야겠군!\n가신끼리 경쟁시키는 것도 좋겠어…",
    "13:181:0": "(가신들로서는 한시도 마음을 놓지 못하니\n　견딜 노릇이 아니겠지만…)",
}

RUNTIME_RECORD_IDS = {162, 163, 164, 171}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_CURRENT_GAPS: dict[int, tuple[bytes, ...]] = {
    162: (b"\x02\x64\x32", b"\x01\x43\x1d\x00\x00\x00", b"\x05\x05\x05"),
    163: (b"", b"\x01\x43\x1d\x00\x00\x00", b"\x05\x05\x05"),
    164: (b"", b"\x01\x43\x1d\x00\x00\x00", b"\x05\x05\x05"),
    171: (b"\x01\x43\x01\x00\x00\x00", b"\x05\x05\x05"),
}
B091_EXACT_REUSE: dict[int, int] = {
    173: 82,
    174: 83,
    175: 84,
    176: 85,
    178: 87,
    179: 88,
    180: 89,
    181: 90,
}
B091_EXACT_TRANSLATIONS = {
    "13:173:0": "같은 가신이라 해도\n여러 신분이 있었을 터인데…\n어디 보자… 무엇이었더라",
    "13:174:0": "낮은 순서부터\n조두, 아시가루 대장, 사무라이 대장, 부장, 가로, 숙로\n이렇게 여섯 신분이 있습니다",
    "13:175:0": "출세하려면 훈공이 필요합니다\n아무런 성과도 내지 못한 자를\n출세시킬 수는 없기 때문입니다",
    "13:176:0": "합전에서 활약하거나 군을 다스려\n훈공을 인정받으면 출세의 길이\n열린다는 말이군",
    "13:178:0": "우선 본거지에 속한 군의 대관으로\n훈공을 세우고 신분을 올린 뒤\n지행지를 맡기는 것이 좋겠습니다",
    "13:179:0": "가신의 신분이 올라가면\n성주나 군단장으로 임명하는 것도\n가능해집니다",
    "13:180:0": "눈여겨본 무장에게는 적극적으로\n일을 맡겨 훈공을 세우게 해야겠군!\n가신끼리 경쟁시키는 것도 좋겠어…",
    "13:181:0": "(가신들로서는 한시도 마음을 놓지 못하니\n　견딜 노릇이 아니겠지만…)",
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def record_gaps(record: Any) -> tuple[bytes, ...]:
    gaps: list[bytes] = []
    cursor = 0
    for literal in ENGINE.parse_record_literals(record):
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def assert_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_CURRENT_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine runtime skeleton drift: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current runtime skeleton drift: 13:{record_id}")
    if source_records[(13, 163)].data != source_records[(13, 164)].data:
        raise RuntimeError("13:163/164 pristine duplicate drift")
    if current_records[(13, 163)].data != current_records[(13, 164)].data:
        raise RuntimeError("13:163/164 current duplicate drift")
    if TRANSLATIONS["13:163:0"] != TRANSLATIONS["13:164:0"]:
        raise RuntimeError("13:163/164 literal 0 translations must remain exact")
    if TRANSLATIONS["13:163:1"] != TRANSLATIONS["13:164:1"]:
        raise RuntimeError("13:163/164 literal 1 translations must remain exact")
    for target_id, prior_id in B091_EXACT_REUSE.items():
        if source_records[(13, target_id)].data != source_records[(13, prior_id)].data:
            raise RuntimeError(f"B091 exact source reuse drift: 13:{target_id} != 13:{prior_id}")
    for coordinate, expected in B091_EXACT_TRANSLATIONS.items():
        if TRANSLATIONS[coordinate] != expected:
            raise RuntimeError(f"B091 exact translation reuse drift: {coordinate}")
    u3000_counts = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if u3000_counts != {"13:181:0": 1}:
        raise RuntimeError(f"segment 752 U+3000 scope drift: {u3000_counts}")
    for translation in TRANSLATIONS.values():
        if "\r" in translation or BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 752 retains CR or banned fullwidth punctuation")


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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_jp_en_sc_tc_context"
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
                "segment": "base_msggame_B001_S752",
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
