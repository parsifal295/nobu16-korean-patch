#!/usr/bin/env python3
"""Build Base authoring segment 123 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S123.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s123", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:2256:0": "님, 용케도 오셨군요",
    "6:2257:0": "님은 목숨이 아깝지 않은 모양이군",
    "6:2258:0": "님, 이야기 정도는 들어 드리지요",
    "6:2259:0": "님과 나눌 이야기가 있겠습니까?",
    "6:2260:0": "요구 내용을 일단 모두 취하합니다\n진행하시겠습니까?",
    "6:2261:0": "오! 사이좋게 지내자는 거냐?",
    "6:2262:0": "그래서 우리와 친목을 다지는 데\n얼마만한 가치가 있다고 보는가?",
    "6:2263:0": "호오, 마음만으로도 기쁜 법이지",
    "6:2264:0": "무언가를 주시겠다는 겁니까?\n이거 참 송구스럽군요",
    "6:2265:0": "번거로운 미사여구는 필요 없소\n무엇으로 우리의 환심을 사시려는가?",
    "6:2266:0": "호오, 기특한 일이로군",
    "6:2267:0": "친목을 다지고 싶다고? 바라던 바요\n하지만 그 말의 무게를 무엇으로 재겠소?",
    "6:2268:0": "흠… 그러니까 말이야\n뭔가 선물을 주겠다는 거지?",
    "6:2269:0": "혹시 무언가를 주시는 겁니까?",
    "6:2270:0": "이거 고맙군\n감사를 표해야겠어",
    "6:2271:0": "어머, 마음 써 주시니 감사드려요",
    "6:2272:0": "이토록 배려해 주시다니… 감격했습니다",
    "6:2273:0": "별거 아니긴 한데…\n뭐, 성의랄까… 말하게 하지 말라고!",
    "6:2274:0": "상관없다… 하지만 우리 가문에도 긍지가 있다\n그대 가문의 개로 보이지 않을 만큼의 대가는 받아야겠다",
    "6:2275:0": "그렇군… 우리 가문에는 간단한 일이지\n그래, 사례는 얼마나 내놓겠나?",
    "6:2276:0": "흔쾌히 받아들이지요\n그에 걸맞은 사례를 주신다면 말입니다",
    "6:2277:0": "쉬운 일이오\n하지만 가신들 앞에서 공짜로 해 줄 수는 없지",
    "6:2278:0": "가벼운 일이라도 그에 맞는 대가는 필요하다…\n그래야 두 가문이 함께 발전할 수 있지",
    "6:2279:0": "좋습니다. 이제 그대 가문도 보여 주십시오\n우리가 베풀 만한 가치가 있는 후한 벗임을",
    "6:2280:0": "그 정도는 가벼운 일이나…\n나머지는 답례로 무엇을 내놓느냐에 달렸지",
    "6:2281:0": "그렇군요, 그것을 바라십니까?\n그럼 성의를 조금 받아 볼까요",
    "6:2282:0": "이 정도는 일도 아니지\n…하지만 공짜로는 해 줄 수 없다",
    "6:2283:0": "그야 쉬운 일입니다\n그래서,",
    "6:2283:1": "은(는) 무엇을 주시겠습니까?",
    "6:2284:0": "받아들일 수는 있습니다만\n대가를 받지 않고서는…",
    "6:2285:0": "우선",
    "6:2285:1": "이(가) 성의를 보여라\n이야기는 그다음이다",
    "6:2286:0": "이만한 일을 부탁하는 것이니\n대가로 우리를 얕보지는 않겠지",
    "6:2287:0": "참으로 큰 소망이로군\n물론 값이 비쌀 텐데 괜찮겠나?",
    "6:2288:0": "크게 나오시는군요\n그에 걸맞은 것은 준비하셨습니까?",
    "6:2289:0": "훗… 크게 나오는군\n단도직입적으로 말해 대가에 달렸어",
    "6:2290:0": "제법이군… 당연히 그만한 대가가 필요하다만\n물론 준비해 두었겠지…?",
    "6:2291:0": "그래… 요구에 응하고 싶은 마음은 굴뚝같지만\n먼저 그대 가문의 성의를 보고 싶소",
    "6:2292:0": "흠… 조금 까다로운 이야기로군\n대가에 따라 응하지 못할 것도 없네만",
    "6:2293:0": "그것을 바라신다면…\n값은 톡톡히 받겠습니다",
    "6:2294:0": "못 들어줄 부탁은 아니나…\n그에 걸맞은 대가는 받아야겠소",
    "6:2295:0": "제법 어려운 요구를 하시는군요\n물론 시세는 알고 계시지요?",
    "6:2296:0": "까다로운 요구로군…\n대가는 넉넉히 받겠소",
    "6:2297:0": "터무니없는 소릴 하는군…\n대가에 달렸어",
    "6:2298:0": "이만한 일을 우리 가문에 바라는 것이니\n그대 가문도 상당한 출혈을 각오해야 한다",
    "6:2299:0": "그것을 바란다면\n그에 걸맞은 대가를 받도록 하지",
}

DYNAMIC_COORDINATES = {
    "6:2256:0",
    "6:2257:0",
    "6:2258:0",
    "6:2259:0",
    "6:2283:0",
    "6:2283:1",
    "6:2285:0",
    "6:2285:1",
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
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_COORDINATES
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
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S123",
                "decision_count": len(rows),
                "retranslated": len(rows) - len(DYNAMIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_COORDINATES),
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
