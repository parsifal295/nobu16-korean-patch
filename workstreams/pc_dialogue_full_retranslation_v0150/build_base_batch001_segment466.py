#!/usr/bin/env python3
"""Build Base authoring segment 466 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S466.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s466", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2560:0": "퇴로를 장악한 내 활약에\n적도 간담이 서늘했을 터\n훌륭한 전과를 거두었으니 경사로다, 경사로다",
    "7:2561:0": "적의 퇴로를 끊은 것이\n승리를 불러온 결정타였군요\n전공 제일도 당연하겠지요",
    "7:2562:0": "전공 제일이라니 쑥스럽군\n그저 이번 싸움의 급소를 간파해\n적의 퇴로를 끊었을 뿐이다",
    "7:2563:0": "싸움을 좌우했으리라\n적의 퇴로를 끊어 주었다\n이 승리는 내 활약 덕분이다!",
    "7:2564:0": "달아날 곳을 잃은 적 따위\n갓난아이 손목을 비트는 것과 같지\n군공도 바라는 대로구나",
    "7:2565:0": "이제 알았을 것이다\n적의 퇴로를 막으면 그걸로 끝이지!\n오랜 세월의 경험이 힘을 발휘했도다",
    "7:2566:0": "생각 이상으로 전과를 올렸습니다\n퇴로를 끊은 것이 주효했군요\n다행입니다……",
    "7:2567:0": "적군은 괴멸했다\n퇴로를 끊으면 이 정도는 당연하지\n다음에도—",
    "7:2567:1": "에게 맡겨 주게",
    "7:2568:0": "퇴로를 끊는 전법이 잘 통했습니다\n지혜와 담력만 있다면\n",
    "7:2568:1": "라도 이 정도는 해낼 수 있습니다",
    "7:2569:0": "적의 퇴로를 끊은 내 군략이\n싸움의 흐름을 결정했군\n전공 제일도 당연한 일이지",
    "7:2570:0": "요지를 장악하는 자가 싸움을 장악한다\n이번 싸움에서는—",
    "7:2570:1": "의 활약이 승리를\n가져왔다 해도 과언이 아니오",
    "7:2571:0": "이번 싸움에서는—",
    "7:2571:1": "이(가) 전공 제일이다!\n누구보다 먼저 요지를 장악한 덕에\n모두 적과 수월히 싸웠을 게다!",
    "7:2572:0": "싸움에서는 요지 제압도 중요하지\n아군을 계속 뒷받침한 내 활약이\n이번 승리로 이어졌을 터",
    "7:2573:0": "전장을 파악해야 늘 승리하는 법\n요지만 장악하면\n어떤 적도 두려워할 것 없느니라",
    "7:2574:0": "전공 제일이었는가\n요지를 장악해 적의 기세를 꺾은 것이\n이번 승리의 결정적 이유였군",
    "7:2575:0": "호오…… 전공 제일인가\n요지를 장악한 활약이\n이번 승기를 불러온 덕분이로구나",
}

PENDING_COORDINATES = {
    "7:2567:0", "7:2567:1", "7:2568:0", "7:2568:1",
    "7:2570:0", "7:2570:1", "7:2571:0", "7:2571:1",
}
STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - PENDING_COORDINATES


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
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S466", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
