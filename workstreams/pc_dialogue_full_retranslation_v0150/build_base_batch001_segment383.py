#!/usr/bin/env python3
"""Build Base authoring segment 383 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S383.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s383", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1247:0": "이(가) 대군으로 침공한다 하옵니다\n각오는 이미 마쳤사오니\n출격을 명해 주시옵소서",
    "7:1248:0": "이(가) 다가오고 있사옵니다\n당해 내지 못할 상대일지도 모르오나\n그래도 한칼만이라도……!",
    "7:1249:0": "이(가) 대군으로 내습한다 하옵니다\n설령 적과 함께 죽는 한이 있더라도\n영민을 지키고 싶사옵니다",
    "7:1250:0": "의 침공입니다\n중과부적이오나…… 호락호락\n적이 제멋대로 하게 두지는 않겠습니다",
    "7:1251:0": "은(는) 강대합니다!\n이대로 잠자코 지켜보기만 하면\n놈들의 먹잇감이 되고 말 것이옵니다",
    "7:1252:0": "의 침공입니다!\n피아의 전력 차이는 막대합니다!\n서둘러 요격하지 않으면……!",
    "7:1253:0": "은(는) 수비가 허술하다\n보낼 병력은 최소한으로 줄여\n낭비를 덜어 보는 게 어떻겠나",
    "7:1254:0": "이라면\n대군을 거느리지 않아도\n쉽게 함락할 수 있을 게다",
    "7:1255:0": "은(는) 노릴 만한 곳\n그리 병력을 많이 들이지 않고도\n함락할 수 있을 것이옵니다",
    "7:1256:0": "이라면 적은 병력으로 충분하다\n다른 다이묘에게 선수를 빼앗기기 전에\n우리가 차지해 둬야겠구먼",
    "7:1257:0": "을(를) 공략할 적기이외다\n내가 보기에는\n최소한의 병력으로 충분할 것이오",
    "7:1258:0": "을(를) 공격하는 데\n대군은 필요 없다고 보았소\n이제 주군의 하명을 기다릴 뿐",
    "7:1259:0": "은(는) 노려볼 만한 곳\n외람되오나 병력은 그리 필요치 않을 듯\n주군의 걱정은 기우로 끝날 것이옵니다",
    "7:1260:0": "을(를) 공격해 보세\n저 정도라면\n적은 병력으로도 문제없을 터",
    "7:1261:0": "은(는) 수비가 허술합니다\n우리가 적은 병력으로 나선다 해도\n맞설 방도는 없을 것입니다",
    "7:1262:0": "은(는) 노려볼 만한 곳\n기회를 놓치기 전에\n우리가 숨통을 끊읍시다",
    "7:1263:0": "은(는) 적은 병력으로도 충분할 듯하옵니다\n저곳을 탐내는 다이묘가 나타나기 전에\n서둘러 함락시키십시다",
    "7:1264:0": "이라면\n내 비책을 써서\n적은 병력을 마음껏 날뛰게 해 주마",
    "7:1265:0": "은(는) 노릴 만한 곳\n병력을 최소한으로 줄여도\n쉽게 함락할 수 있을 것이옵니다",
    "7:1266:0": "이라면\n적은 병력으로도 함락할 수 있으리라\n모두들, 기회를 놓치지 마라!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S383", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
