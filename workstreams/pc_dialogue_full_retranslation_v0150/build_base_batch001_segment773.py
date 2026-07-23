#!/usr/bin/env python3
"""Build Base authoring segment 773 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S773.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s773", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:24:0": "[역직]",
    "14:24:1": (
        "\n정이대장군이 다이묘인 세력, 즉 쇼군가만 실행할 수 있는 명령입니다.\n"
        "다른 세력에 막부 역직을 내려 자세력에 대한 외교 자세를 개선할 수 있습니다.\n"
        "\n"
        "다만 역직을 얻은 세력은 위신이 높아지므로\n"
        "함부로 역직을 내리지 말고 상대를 잘 살펴 외교합시다.\n"
        "\n"
    ),
    "14:24:2": "◇쇼군가의 이점",
    "14:24:3": (
        "\n역직을 내려 외교 자세를 개선하고 유리하게 외교를 펼칠 수 있습니다.\n"
        "쇼군가로 플레이한다면 높은 위신과 역직을 활용해\n"
        "적극적으로 외교합시다."
    ),
    "14:25:0": "[상벌]",
    "14:25:1": (
        "\n가신에게 가보나 관직을 내리면 충성과 능력을 높일 수 있습니다.\n"
        "몰수하거나 박탈할 수도 있지만 충성이 크게 떨어집니다.\n"
        "가보와 관직은 얻을 수 있는 수량이 한정되어 있으므로\n"
        "되도록 유력하면서 충성이 낮은 무장에게 주는 것이 좋습니다.\n"
        "\n"
    ),
    "14:25:2": "◇가보 수여",
    "14:25:3": (
        "\n무장에게 가보를 주면 충성과 능력이 오릅니다.\n"
        "가보의 종류에 따라 오르는 능력도 달라집니다.\n"
        "등급이 높은 가보일수록 충성과 능력의 상승 폭이 커집니다.\n"
        '※가보는 "거래"로 구입할 수 있습니다\n'
        "\n"
    ),
    "14:25:4": "◇관직 수여",
    "14:25:5": (
        "\n가신에게 관직을 내리면 충성이 오릅니다.\n"
        "가신에게 내릴 수 있는 관직은 세력이 보유한 관직 중\n"
        "다이묘의 관직보다 관위가 낮은 것뿐입니다.\n"
        '※관직은 "조정"에서 얻을 수 있습니다'
    ),
    "14:26:0": "[결연]",
    "14:26:1": (
        "\n다이묘나 가신의 혼인을 주선합니다.\n"
        "남성 다이묘는 정실과 측실을 둘 수 있습니다.\n"
        "결연한 가신은 충성이 오를 뿐 아니라 일문 무장도 늘어납니다.\n"
        "\n"
    ),
    "14:26:2": "◇일문 무장이란",
    "14:26:3": (
        "\n일문 무장이란 다이묘의 혈족이나 배우자의 혈족인 무장을 말합니다.\n"
        "다이묘의 양부와 배우자의 양부도 일문에 포함됩니다.\n"
        '무장 정보의 "인물" 탭에서 확인할 수 있습니다.\n'
        "\n"
        "일문 무장이 없는 상태에서 다이묘가 사망하면 게임 오버가 되므로\n"
        "후계자로 알맞은 무장이 있다면 미리 결연해 두는 것이 좋습니다."
    ),
    "14:27:0": "[은거]",
    "14:27:1": "\n다이묘가 은거하고 일문 무장이 그 뒤를 이어 다이묘가 됩니다.\n\n",
    "14:27:2": "◇포인트",
    "14:27:3": (
        '\n\u3000·발동 조건이 "다이묘"인 특성을 지닌 경우\n'
        "  다이묘가 되면 그 특성을 발휘할 수 있다\n"
        "·다이묘가 자주 병에 걸려 능력 저하가 잦다면\n"
        "  은거시키는 편이 나을 수도 있다"
    ),
    "14:28:0": "[해고]",
    "14:28:1": (
        "\n가신을 세력에서 추방합니다.\n"
        "어지간한 일이 아니라면 가신을 추방할 이점은 없습니다.\n"
        "\n"
        "다만 충성이 낮은 무장은 조략에 넘어가기 쉬우므로\n"
        "무장 수가 부족하지 않다면 추방해 화근을 미리 없애는 방법도 있습니다.\n"
        "※소지한 가보나 관위는 몰수합니다"
    ),
}

BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)
EXPECTED_ARITY = {24: 4, 25: 6, 26: 4, 27: 4, 28: 2}


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {24: 37, 25: 38, 26: 39, 27: 40, 28: 42}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 773 record has no configured PK mapping: {base_record_id}") from exc


def layout_signature(text: str) -> tuple[object, ...]:
    return (
        text.count("\n"),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(ENGINE.protected_signature(text)["non_layout_controls"]),
        ENGINE.protected_signature(text)["leading_whitespace"],
        ENGINE.protected_signature(text)["trailing_whitespace"],
    )


def assert_available_duplicate_decision(coordinate: str, translation: str) -> None:
    decision_dir = OUTPUT.parent
    if not decision_dir.is_dir():
        return
    for decision_path in decision_dir.glob("base_msggame_B001_S*.private.v1.jsonl"):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate and row.get("translation") != translation:
                raise RuntimeError(f"duplicate translation differs from {coordinate}")


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
    expected_divergences = {"JP": {24, 27, 28}, "SC": set(), "TC": set()}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(24, 29)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(14, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(14, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != expected_divergences[language]:
            raise RuntimeError(
                f"segment 773 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected_arity in EXPECTED_ARITY.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 773 literal arity drifted: 14:{record_id}")
    for coordinate, translation in TRANSLATIONS.items():
        _, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(14, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/ESC layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} retains CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "역직",
        "관직",
        "관위",
        "결연",
        "정실",
        "측실",
        "일문 무장",
        "은거",
        "해고",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 773 required terminology drifted")
    if any(term in joined for term in ("취차", "연조", "혼약", "호족")):
        raise RuntimeError("segment 773 retains a forbidden legacy term")
    if len(ENGINE.parse_record_literals(pk_source_records[(14, 37)])) != 6:
        raise RuntimeError("segment 773 PK-only 14:24 expansion contract drifted")
    if any(term in joined for term in ("관령", "간토 관령")):
        raise RuntimeError("segment 773 imported PK-only role explanations")
    if TRANSLATIONS["14:27:2"] != "◇포인트":
        raise RuntimeError("14:27:2 repeated heading drifted")
    assert_available_duplicate_decision("14:19:2", TRANSLATIONS["14:27:2"])
    if len(TRANSLATIONS) != 20 or set(TRANSLATIONS) != {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITY.items()
        for literal_id in range(arity)
    }:
        raise RuntimeError("segment 773 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S773",
                "decision_count": len(rows),
                "retranslated": len(rows),
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
