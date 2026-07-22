#!/usr/bin/env python3
"""Build Base authoring segment 441 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S441.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s441", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2160:0": "이런 성은 작은 바위나 다름없다\n단숨에 몰아쳐라",
    "7:2161:0": "작은 성이라 해도\n결코 소홀히 하지 않겠다!",
    "7:2162:0": "보잘것없는 성이군\n단숨에 때려 부숴 주마",
    "7:2163:0": "이 정도의 작은 성은\n함락하는 것쯤은 일도 아니다",
    "7:2164:0": "이런 작은 성은 단숨에\n짓눌러 버려라!",
    "7:2165:0": "작은 성에 시간을 들이면\n웃음거리가 됩니다",
    "7:2166:0": "이런 작은 성에 틀어박히다니\n우리를 얕보았구나!",
    "7:2167:0": "조그마한 성이로군\n단숨에 짓밟아 주마",
    "7:2168:0": "작은 성 따위\n병력으로 짓눌러 버리면 된다",
    "7:2169:0": "불면 날아갈 듯한 작은 성\n자, 단숨에 몰아쳐라",
    "7:2170:0": "이런 작은 성쯤은\n금세 함락해 보이겠습니다",
    "7:2171:0": "이 정도의 작은 성은\n단숨에 짓눌러 버려라!",
    "7:2172:0": "이런 작은 성에\n시간을 들일 수는 없습니다",
    "7:2173:0": "이런 작은 성은\n단숨에 함락시켜라!",
    "7:2174:0": "기다릴 필요는 없다\n강공으로 빼앗아라!",
    "7:2175:0": "포위에는 시간이 걸린다\n힘으로 밀어붙여 굴복시키는 게다",
    "7:2176:0": "상황을 고려하면\n힘으로 밀어붙여야 하오!",
    "7:2177:0": "이 성은 포위보다\n힘으로 밀어붙이는 편이 효과적이겠군",
    "7:2178:0": "포위는 필요 없다\n정면에서 공격하라",
    "7:2179:0": "비축분은 충분하다…… 그렇다면\n강공으로 끝장을 내라",
}

STATIC_COORDINATES = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S441", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
