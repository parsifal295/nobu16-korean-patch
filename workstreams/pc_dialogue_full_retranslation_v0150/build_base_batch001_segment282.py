#!/usr/bin/env python3
"""Build Base authoring segment 282 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S282.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s282", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4296:1": "의 기마대가 지닌 위세를 세상에 떨치리라!",
    "6:4297:0": "비사문천이여\n파사현정을 이루는 우리에게 힘을!",
    "6:4298:0": "백성을 아끼는 마음이야말로 정치의 요체\n",
    "6:4298:1": "의 정치는 백성과 함께한다!",
    "6:4299:0": "의 이름 아래 사사로운 무력 행사를 금한다\n우리의 위세로 평온을 가져오리라!",
    "6:4300:0": "늘 단련을 게을리하지 마라!\n우리 영토를 단 한 치도 잃지 마라",
    "6:4301:0": "아미타불께서 우리를 구원하시리라…\n신심은 두텁게, 결속은 굳건히 하라",
    "6:4302:0": "백만일심의 기치 아래\n신민 모두 마음을 하나로 모아야 한다…\n단결하면 이루지 못할 일이 없다",
    "6:4303:0": "위급 상황에 즉시 대응하려면 「",
    "6:4303:1": "」이(가) 요체다\n상재전장, 결코 방심해서는 안 된다!",
    "6:4304:0": "사쓰마 하야토라면 무엇보다 무도를 익혀야 한다\n무인의 참뜻은 전장에서 보여라!",
    "6:4305:0": "말 위에서 불을 뿜는 용기병이여!\n천하를 향해 날아올라라!",
    "6:4306:0": "육문전은 삼도천을 건너는 뱃삯…\n목숨을 아끼지 않는 각오를 세상에 보이리라!",
    "6:4307:0": "검지를 철저히 시행하라!\n그리하여 만백성이 평온하리라…는 것이지!",
    "6:4308:0": "남만사를 두터이 후원하고 음악으로 세상을 채워라\n천주의 가르침을 널리 전파하라…!",
    "6:4309:0": "동지들은 각자 화승총을 손질하라\n자기 영지는 스스로 지키는 것이야말로 자치촌의 법도다!",
    "6:4310:0": "에 성하 시설",
    "6:4310:1": "을(를) 건설했습니다",
}

STATIC_COORDINATES: set[str] = {
    "6:4297:0",
    "6:4300:0",
    "6:4301:0",
    "6:4302:0",
    "6:4304:0",
    "6:4305:0",
    "6:4306:0",
    "6:4307:0",
    "6:4308:0",
    "6:4309:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S282", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
