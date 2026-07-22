#!/usr/bin/env python3
"""Build Base batch 001 segment 02 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S02.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s02", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:95:0": (
        "성인식을 마쳤으니 저도\n"
        "어엿한 어른이 되었습니다.\n"
        "아내로서 주군을 받들고 싶사옵니다"
    ),
    "2:96:0": (
        "저도 이제 어엿한 어른이 되었으니, 앞으로는\n"
        "주군께 더욱 힘이 될 수 있도록\n"
        "무가의 아내로서 부끄럽지 않게 처신하겠습니다"
    ),
    "2:97:0": (
        "성인식을 마쳐 저도 어엿한 어른이 되었습니다.\n"
        "무가에 시집온 몸으로서 훌륭히 소임을 다하고자\n"
        "앞으로도 정진하겠나이다"
    ),
    "2:98:0": (
        "마침내 한 사람 몫을 하게 되었으니, 앞으로는\n"
        "주군을 훌륭히 보필하고 가문의 번영에\n"
        "조금이나마 보탬이 되고자 하옵니다"
    ),
    "2:99:0": "드디어 성인식도 마쳤으니\n이제부터는",
    "2:99:1": "의 패업에 힘을 보태고자\n갈고닦은 문무를 마음껏 펼치겠사옵니다",
    "2:100:0": (
        "저도 홀로 설 때를 맞았지만, 앞으로도\n"
        "당당히 한 사람 몫을 해내도록 끊임없이 힘써\n"
    ),
    "2:100:1": "께 온 힘을 다하고 싶사옵니다",
    "2:101:0": "성인식을 마치고, 저도",
    "2:101:1": "님을\n모실 날이 마침내\n찾아와 참으로 기쁘옵니다",
    "2:102:0": (
        "님, 저도 성인식을 마쳐\n"
        "이제 어엿한 어른으로 대접받게 되었사오니\n"
        "마음껏 써 주시옵소서"
    ),
    "2:103:0": "님, 찾아뵈었습니다.\n성인식도 마쳤으니 이제부터는",
    "2:103:1": "님께\n도움이 되도록 힘쓰겠습니다",
    "2:104:0": "성인식을 마쳤으니, 무가의 딸로서\n",
    "2:104:1": "님을 보필할 수 있는 이날을\n저 또한 오래도록 기다려 왔습니다",
    "2:105:0": "원복을 마치고\n한 사람 몫을 하게 된 무장 수:",
    "2:105:1": "명",
    "2:106:0": "원복을 마치고\n휘하에 들어오는 무장 수:",
    "2:106:1": "명",
    "2:107:0": "의 적대 목표가 갱신되었습니다",
    "2:108:0": "의 금전 공출량이 수입 부족으로 감소했습니다",
    "2:109:0": "의 병량 공출량이 수입 부족으로 감소했습니다",
    "2:110:0": "의 군마 공출량이 수입 부족으로 감소했습니다",
    "2:111:0": "의 철포 공출량이 수입 부족으로 감소했습니다",
    "2:112:0": "세력이 멸망했습니다\n게임을 종료합니다",
    "2:113:0": "측과 맺은 혼인 동맹을\n파기하게 됩니다. 계속하시겠습니까?",
    "2:114:0": "등과 맺은 혼인 동맹을\n파기하게 됩니다. 계속하시겠습니까?",
    "2:115:0": "와 혈연관계가 없어\n출가하게 될 공주가 있습니다. 계속하시겠습니까?",
    "2:116:0": "뒷일은 내게 맡겨\n이",
    "2:116:1": "이 크게 키워 줄 테니까!",
}


DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - {
    "2:95:0",
    "2:96:0",
    "2:97:0",
    "2:98:0",
    "2:112:0",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
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
                "scope_classification": (
                    "runtime_fragment_pending"
                    if coordinate in DYNAMIC_RUNTIME_COORDINATES
                    else "retranslated"
                ),
                "layout_review": "unchanged_from_current",
                "runtime_review": (
                    "pending" if coordinate in DYNAMIC_RUNTIME_COORDINATES else "not_required"
                ),
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context",
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
                "segment": "base_msggame_B001_S02",
                "decision_count": len(rows),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
