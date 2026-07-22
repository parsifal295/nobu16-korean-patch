#!/usr/bin/env python3
"""Build Base authoring segment 384 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S384.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s384", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1267:0": "이(가) 허술하다니 뜻밖의 행운\n출병할 병력은 최소한으로 줄이고\n다른 다이묘의 침공에 대비합시다",
    "7:1268:0": "을(를) 공격하는가\n설령 아군이 적은 병력이라 해도\n우리라면 걱정 없겠지만……",
    "7:1269:0": "을(를) 노리는 건 어때?\n저 정도 성이라면\n병력도 그리 많이 필요 없겠지",
    "7:1270:0": "을(를) 노려 볼까?\n나 혼자서도 함락할 수 있을 듯하지만\n지휘는 주군께 맡기겠어",
    "7:1271:0": "이(가) 좋을 듯하옵니다\n병력을 적게 추리더라도\n쉽게 함락할 수 있는 성이옵니다",
    "7:1272:0": "공략한다면 「",
    "7:1272:1": "」이(가) 좋다\n강자와 맞설 때까지\n병력은 아껴 두는 것이 길하리라",
    "7:1273:0": "은(는) 어떻겠사옵니까\n그 정도 성이라면\n소수의 병력으로 충분할 것이옵니다",
    "7:1274:0": "을(를) 공략한다면\n병력을 헛되이 나누지 않고\n성을 얻을 수 있으니 더없이 좋구나",
    "7:1275:0": "은(는) 노려볼 만한 곳\n병력을 최소한으로 줄여도\n쉽게 제압할 수 있을 것입니다",
    "7:1276:0": "은(는) 지금이 공략할 호기이옵니다\n적은 병력으로 제압하면\n남은 병력을 다른 곳에 돌릴 수 있사옵니다",
    "7:1277:0": "이라면\n적은 병력으로도 문제없사오나\n조금 지루할 듯도 하옵니다",
    "7:1278:0": "이라면\n적은 병력으로도 함락할 수 있겠지만\n맞설 만한 맹장이 없다니 아쉽구나",
    "7:1279:0": "은(는) 노려볼 만한 곳인 듯하옵니다\n최소한의 병력과 소생의 계책으로\n쉽게 함락할 수 있을 것이옵니다",
    "7:1280:0": "은(는) 무르다\n살짝 건드리기만 해도\n쉽게 무너져 내릴 게다",
    "7:1281:0": "을(를) 공격합시다\n병력은 많이 필요치 않사옵니다만\n어찌하시겠사옵니까",
    "7:1282:0": "은(는) 지금이 노릴 때로다\n병력을 헛되이 나누지 않고\n성을 얻을 수 있다니 더없이 좋구나",
    "7:1283:0": "은(는) 노려볼 만한 곳이옵니다\n늙은이의 감이기는 하오나\n소수의 병력으로도 함락할 수 있을 듯하옵니다",
    "7:1284:0": "을(를) 공격할까나\n전란이 격심한 세상이니\n병사 하나도 허투루 쓸 수 없느니라",
    "7:1285:0": "을(를) 공격하신다면\n그리 대군을 이끌지 않아도\n승산은 충분히 보이옵니다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S384", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
