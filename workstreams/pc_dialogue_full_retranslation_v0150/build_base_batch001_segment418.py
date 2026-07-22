#!/usr/bin/env python3
"""Build Base authoring segment 418 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S418.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s418", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1813:0": "돌아가라!　",
    "7:1813:1": "의\n위기는 사라졌다",
    "7:1814:0": "은(는) 이제 됐다\n위기가 사라졌으니 경사로구나",
    "7:1815:0": "은(는) 이제 안전하다\n더는 지킬 필요도 없으리라",
    "7:1816:0": "은(는) 걱정할 것 없소\n바위처럼 굳건하니 말이오",
    "7:1817:0": "은(는) 반석과도 같다\n경계를 해제한다",
    "7:1818:0": "은(는) 근심할 것 없다\n자리를 떠나도 문제없겠지",
    "7:1819:0": "은(는) 이제 안전하다!\n철수한다!",
    "7:1820:0": "은(는) 방어할 필요 없다\n이제 아무 문제도 없다",
    "7:1821:0": "은(는) 괜찮다\n",
    "7:1821:1": "의 차례도 여기까지로군",
    "7:1822:0": "의 주변에는\n적의 모습이 보이지 않는군",
    "7:1823:0": "은(는) 안전하다\n내가 나설 필요도 없느니라",
    "7:1824:0": "의 경계 해제\n방어 임무도 종료로군요",
    "7:1825:0": "은(는) 문제없다\n지금은 병사를 거둘 때다",
    "7:1826:0": "의 안전은\n이제 확실해졌어요",
    "7:1827:0": "의 방어 완료\n이제 돌아간다",
    "7:1828:0": "의 수비는\n이제 충분한 듯하구나",
    "7:1829:0": "의 방어는\n이쯤에서 마칩시다",
    "7:1830:0": "의 방어 완료\n이제 귀환한다",
}

STATIC_COORDINATES: set[str] = set()


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S418", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
