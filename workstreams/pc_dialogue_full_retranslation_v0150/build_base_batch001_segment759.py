#!/usr/bin/env python3
"""Build Base authoring segment 759 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S759.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s759", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:301:0": '"성하 시설"-건설-',
    "13:302:0": "㊤금전",
    "13:302:1": "과",
    "13:302:2": "㈹노동력",
    "13:302:3": '을 소비하여 다이묘 군단의 성에 시설 건설을 명령할 수 있습니다.\n성하 시설 건설은 군 개발보다 비용이 많이 들지만, 그만큼 효과도 강력합니다.\n빈 구획에 건설하여 성을 더욱 발전시켜 봅시다.\n\n※무엇을 지을지 고민된다면 금전 수입을 높이는 "상인 마을"을 추천합니다\n※튜토리얼에서는 처음에 한해 비용과 노동력이 들지 않으며, 기간도 단축됩니다',
    "13:303:0": '"지행"-가신 선택-',
    "13:304:0": '지행지를 내릴 무장을 선택합시다.\n선택한 무장은 영주로서 영지(군)를 발전시킵니다.\n\n【무장 선택의 요점】\n◇능력 … 성주보다 높은 능력을 지니고 있다\n◇상성 … 성주와의 상성이 "◎"이다\n\n※한번 영주로 삼으면 정책 "제도 개신" LV2를 발령할 때까지 변경할 수 없습니다',
    "13:305:0": "성주를 중심으로 영주가 보좌하는 형태로 성 능력이 정해집니다.\n앞 페이지의 【무장 선택의 요점】을 충족하는 영주가 있으면 성 능력이 높아집니다.\n\n【성 능력이란】\n·성에도 무장처럼 통솔, 무용, 지략, 정무 능력이 있다\n·내정이나 행군 등 성 단위로 행하는 행동에 사용된다\n·성 능력이 높으면 부대가 강해지고, 수입과 명령 실행 효과도 커진다\n",
    "13:307:0": "'공략 목표 설정'",
    "13:308:0": '미리 "공략 목표"를 설정하면 적의 성을 유리하게 공격할 수 있습니다.\n\n【공략 목표를 설정하면】\n·군을 맡은 무장들이 군비를 시작한다\n·군비가 완료되면 일정 시간 임전 상태(',
    "13:308:1": "╋",
    "13:308:2": ")가 되어\n  출진할 때 부대가 강화된다\n·적 영지와 인접한 지략 60 이상의 영주가 조략을 건다",
    "13:309:0": "【설정 시 주의】\n·공략 목표를 설정하면 가신은 내정을 중단하고\n  군비와 조략에 관한 행동만 수행한다\n·임전 상태는 출진 후 귀환하거나 일정 시간이 지나면 해제된다\n·성대와 군다이는 군비를 할 수 없다",
    "13:310:0": '"목표로 출진"',
    "13:311:0": "목표를 향해 부대를 출진시켜 봅시다.\n※병력이나 성 능력이 아군보다 낮은 상대를 선택하는 것이 좋습니다\n\n【출진할 때 정할 것】\n·공략할 목표\n·출진시킬 부대",
    "13:312:0": "목표를 선택해 부대를 출진시켜 봅시다.\n※이기기 어려운 상대에게 무리하게 출진하지 맙시다.\n\n【출진 순서】\n①목표를 선택하면 추천 부대 편제가 제안된다\n  ※㌘㎝㍑으로 중계점을 설정할 수 있다\n②부대 편제 내용이나 목표도 변경할 수 있다",
    "13:313:0": '부대는 성마다 편제되며, 이끄는 무장에 따라 강함이 달라집니다.\n전투에서 중요한 것은 "능력", "특성", "병력"입니다.\n\n【부대를 강화하려면】\n·우수한 무장에게 영지를 내려 성 능력과 특성 레벨을 높인다\n·영지를 발전시켜 병력을 늘린다\n·성하 시설과 정책으로 병력과 능력을 높인다\n  등',
    "13:314:0": "【이길 만한 상대가 없다면】\n·내정에 전념하여 힘을 기른다\n·주변 세력과 외교하여 원군을 요청한다\n·조략으로 적의 전력을 약화한다\n\n【출진 시 주의】\n출진 중에는 다른 세력에게 공격받을 위험이 있습니다.\n부대를 남겨 두는 등 방어에도 신경 쓰는 것이 좋습니다.",
    "13:315:0": '"행군 개시"',
    "13:316:0": "시간을 진행하면 부대는 휴대 군량을 소비하며 목표를 향해 행군합니다.\n휴대 군량은 날마다 소비됩니다.\n\n【휴대 군량이 바닥나면】\n·병력이 감소하다가 0이 되면 부대가 괴멸한다\n·부대가 괴멸할 때 부대를 이끄는 무장이 사망할 수도 있다\n\n휴대 군량에 주의하며 행군시킵시다.",
    "13:318:0": "【행군 요령】\n·다이묘 이외의 부대는 부대장의 판단으로 행동하지만 지시할 수도 있다\n·적 부대나 성을 협격하면 큰 피해를 줄 수 있다\n 적에게 협격당하지 않는 것도 중요하다\n·특성과 군마, 철포의 LV를 높이면 부대가 강해진다\n·Shift + 드래그로 여럿을 선택해 동시에 명령할 수 있다\n·목표 변경 시 Shift + 왼쪽 클릭으로 중계점을 설정할 수 있다",
    "13:319:0": "【행군 요령】\n·다이묘 이외의 부대는 부대장의 판단으로 행동하지만 지시할 수도 있다\n·적 부대나 성을 협격하면 큰 피해를 줄 수 있다\n 적에게 협격당하지 않는 것도 중요하다\n·특성과 군마, 철포의 LV를 높이면 부대가 강해진다\n·㍉㎝㍑㎝㌣으로 여럿을 선택해 동시에 명령할 수 있다\n·목표 변경 시 ㌘㎝㍑으로 중계점을 설정할 수 있다",
}

EXPECTED_GAPS = {
    302: (
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x1b\x43\x52",
        b"\x1b\x43\x5a",
        b"\x05\x05\x05",
    ),
    308: (b"", b"\x1b\x43\x50", b"\x1b\x43\x5a", b"\x05\x05\x05"),
}
BLANK_RECORD_IDS = {306, 317}
BASE_PK_DIVERGENCES = {
    "JP": {312, 316, 318, 319},
    "SC": {316},
    "TC": {316},
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_offset_plus_22_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def prior_translation(coordinate: str) -> str:
    for decision_path in sorted(OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl")):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    raise RuntimeError(f"prior exact translation is absent: {coordinate}")


def assert_scope(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(301, 320)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, record_id + 22)]
                )
            ]
        }
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 759 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drifted: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")

    for record_id in BLANK_RECORD_IDS:
        if [literal.text for literal in ENGINE.parse_record_literals(source_records[(13, record_id)])] != [""]:
            raise RuntimeError(f"pristine blank classification drifted: 13:{record_id}")
        if [literal.text for literal in ENGINE.parse_record_literals(current_records[(13, record_id)])] != [""]:
            raise RuntimeError(f"current blank classification drifted: 13:{record_id}")
        if any(coordinate.startswith(f"13:{record_id}:") for coordinate in TRANSLATIONS):
            raise RuntimeError(f"blank record must not receive a decision: 13:{record_id}")

    if TRANSLATIONS["13:307:0"] != prior_translation("13:218:0"):
        raise RuntimeError("13:307 must exactly reuse the approved 13:218 translation")
    if source_records[(13, 307)].data != source_records[(13, 218)].data:
        raise RuntimeError("pristine exact reuse drifted: 13:307 != 13:218")
    if current_records[(13, 307)].data != current_records[(13, 218)].data:
        raise RuntimeError("current exact reuse drifted: 13:307 != 13:218")

    if not TRANSLATIONS["13:305:0"].endswith("\n"):
        raise RuntimeError("13:305 must preserve its trailing LF")
    if "휴대 군량" not in TRANSLATIONS["13:316:0"]:
        raise RuntimeError("13:316 must translate 腰兵糧 as 휴대 군량")
    if "중계점" not in TRANSLATIONS["13:312:0"]:
        raise RuntimeError("13:312 must translate 中継点 as 중계점")
    for coordinate in ("13:318:0", "13:319:0"):
        if "중계점" not in TRANSLATIONS[coordinate]:
            raise RuntimeError(f"{coordinate} must translate 中継点 as 중계점")
        if "협격" not in TRANSLATIONS[coordinate] or "협공" in TRANSLATIONS[coordinate]:
            raise RuntimeError(f"{coordinate} must use the established combat term 협격")
    if "㍉㎝㍑㎝㌣" not in TRANSLATIONS["13:319:0"] or "㌘㎝㍑" not in TRANSLATIONS["13:319:0"]:
        raise RuntimeError("13:319 must preserve its embedded input glyph text")

    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 759 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 759 retains banned fullwidth punctuation")
    if len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 759 decision count drifted")


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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": BASIS,
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
                "segment": "base_msggame_B001_S759",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS),
                "dynamic_runtime_review_pending": 0,
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
