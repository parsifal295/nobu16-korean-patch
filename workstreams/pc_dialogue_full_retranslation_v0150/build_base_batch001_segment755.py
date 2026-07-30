#!/usr/bin/env python3
"""Build Base authoring segment 755 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S755.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s755", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:221:0": "다음에 공격할 성을 공략 목표로\n설정할 수 있습니다. 공격하기 전에\n준비하면 부대를 강화할 수 있습니다",
    "13:222:0": '"출진"',
    "13:223:0": "목표를 향해 부대를 출진시킵니다.\n적의 성을 공략하거나 적 부대를 요격할 수 있습니다.\n※이 건의는 보기만 해도 완료됩니다",
    "13:224:0": " > 군사 > 출진",
    "13:225:0": "병력이 필요해질 때에 대비해,\n부대 출진에 관한 설명을\n조금만 드리겠습니다",
    "13:226:0": '"행군"',
    "13:227:0": "부대의 목표를 지정했다면,\n시간을 진행합시다. 각 부대는\n스스로 판단해 목표를 향해 진군합니다.",
    "13:228:0": "왼쪽 위의 시간 진행 버튼(또는",
    "13:228:1": ")",
    "13:229:0": "부대의 목적지를 지정했다면,\n다음은 시간을 진행해 봅시다",
    "13:230:0": '"성주 임명"',
    "13:231:0": "성주를 임명하면\n무장은 다양한 임무를\n수행할 수 있게 됩니다.",
    "13:232:0": " > 임명 > 지행",
    "13:233:0": '가신을 성주로 임명하면\n성의 발전을 기대할 수 있사옵니다\n"지행"에서 임명할 수 있소이다',
    "13:234:0": '"정책"',
    "13:235:0": "매달 일정액의 금전을 소비해 정책을 발령하면,\n세력 전체에 다양한 효과를 얻을 수 있습니다.",
    "13:236:0": " > 평정 > 정책",
    "13:237:0": '금전 수입이 충분하다면\n정책 발령을 검토해 주십시오\n"평정"에서 발령할 수 있사옵니다',
    "13:238:0": '"군단"',
    "13:239:0": "신분이 높은 가신을 군단장으로 임명합니다.\n성과 무장을 맡겨 운용하게 합니다.\n방침을 지시해 전략적으로 연계할 수 있습니다.",
    "13:240:0": " > 평정 > 군단",
    "13:241:0": '군단을 신설해 성의 통치를\n가신에게 맡겨 봅시다\n"평정"에서 진행해 주시오',
}

RUNTIME_RECORD_IDS = {224, 228, 232, 236, 240}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_GAPS = {
    224: (b"\x02\x3c", b"\x05\x05\x05"),
    228: (b"", b"\x02\x3c", b"\x05\x05\x05"),
    232: (b"\x02\x3c", b"\x05\x05\x05"),
    236: (b"\x02\x3c", b"\x05\x05\x05"),
    240: (b"\x02\x3c", b"\x05\x05\x05"),
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
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


def mapped_pk_record_id(base_record_id: int) -> int:
    if 221 <= base_record_id <= 228:
        return base_record_id + 1
    if 229 <= base_record_id <= 269:
        return base_record_id + 2
    raise RuntimeError(f"segment 755 record has no configured PK mapping: {base_record_id}")


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
    jp_divergences = {
        record_id
        for record_id in range(221, 242)
        if [literal.text for literal in ENGINE.parse_record_literals(source_records[(13, record_id)])]
        != [
            literal.text
            for literal in ENGINE.parse_record_literals(
                pk_source_records[(13, mapped_pk_record_id(record_id))]
            )
        ]
    }
    if jp_divergences != {239}:
        raise RuntimeError(f"segment 755 mapped PK JP offsets drifted: {sorted(jp_divergences)}")
    for language in ("SC", "TC"):
        context_divergences = {
            record_id
            for record_id in range(221, 242)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    base_context_records[language][(13, record_id)]
                )
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    pk_context_records[language][(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if context_divergences != {228}:
            raise RuntimeError(
                f"segment 755 mapped PK {language} offsets drifted: {sorted(context_divergences)}"
            )
    for record_id, expected in EXPECTED_GAPS.items():
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drifted: 13:{record_id}")
    for record_id in (224, 232, 236, 240):
        literal = ENGINE.parse_record_literals(current_records[(13, record_id)])[0]
        if ENGINE.protected_signature(literal.text)["leading_whitespace"] != " ":
            raise RuntimeError(f"13:{record_id}:0 must preserve one leading ASCII space")
    if source_records[(13, 216)].data != source_records[(13, 232)].data:
        raise RuntimeError("pristine Base raw duplicate 13:216=13:232 drifted")
    if current_records[(13, 216)].data != current_records[(13, 232)].data:
        raise RuntimeError("current Base raw duplicate 13:216=13:232 drifted")
    duplicate_ids = (228, 272, 276, 280)
    if len({source_records[(13, record_id)].data for record_id in duplicate_ids}) != 1:
        raise RuntimeError("pristine Base raw duplicate 13:228=272=276=280 drifted")
    if len({current_records[(13, record_id)].data for record_id in duplicate_ids}) != 1:
        raise RuntimeError("current Base raw duplicate 13:228=272=276=280 drifted")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 755 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 755 retains banned fullwidth punctuation")
    if "건의" not in TRANSLATIONS["13:223:0"]:
        raise RuntimeError("13:223 must preserve 具申=건의")
    if TRANSLATIONS["13:232:0"] != " > 임명 > 지행":
        raise RuntimeError("13:232 must remain synchronized with raw duplicate 13:216")
    if len(TRANSLATIONS) != 22 or len(DYNAMIC_RUNTIME_COORDINATES) != 6:
        raise RuntimeError("segment 755 decision/classification count drifted")

    decision_dir = OUTPUT.parent
    if decision_dir.is_dir():
        for decision_path in decision_dir.glob("base_msggame_B001_S*.private.v1.jsonl"):
            if decision_path == OUTPUT:
                continue
            for line in decision_path.read_text(encoding="utf-8").splitlines():
                if not line:
                    continue
                row = json.loads(line)
                if row.get("coordinate") == "13:216:0" and row.get("translation") != TRANSLATIONS["13:232:0"]:
                    raise RuntimeError("13:232 translation differs from the available B result at 13:216")


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
                "segment": "base_msggame_B001_S755",
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
