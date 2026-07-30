#!/usr/bin/env python3
"""Build Base authoring segment 774 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S774.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s774", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:29:0": "[군단]",
    "14:29:1": (
        "\n무장에게 성과 가신을 맡겨 군사와 내정을 일임합니다.\n"
        "\n"
        '"신설"로 새로운 군단을 만듭니다.\n'
        '이미 만든 군단은 "편제"에서 설정할 수 있습니다.\n'
        '필요 없는 군단은 "해산"할 수 있습니다.\n'
        "\n"
    ),
    "14:29:2": "◇군단 설정",
    "14:29:3": (
        "\n\u3000·성 편제  ... 군단에 맡길 성을 변경한다\n"
        "·무장 편제 ... 군단 소속 가신을 변경한다\n"
        "·군단 방침 ... 활동 내용의 방침을 변경한다\n"
        "\n"
    ),
    "14:29:4": "◇군단장 조건",
    "14:29:5": '\n\u3000·가문 내 역직이 "가로" 이상\n·성주로 임명된 무장',
    "14:30:0": "◇군단 방침",
    "14:30:1": (
        "\n\u3000·위임 공략 ... 군단장의 판단에 따라 다른 세력을 공격한다\n"
        "·성 공략  ... 지정한 성을 공략한다\n"
        "·군단 지원 ... 지정한 아군 군단에 맞춰 출진하거나 물자를 수송한다\n"
        "·절취 허가 ... 군단이 얻은 영지를 군단 소속으로 삼을지 정한다\n"
        "\n"
    ),
    "14:30:2": "◇상납금",
    "14:30:3": (
        "\n군단에서 다이묘 군단에 매달 자동으로 바치는 금전입니다.\n"
        "군단의 금전 수입에 따라 늘거나 줄어듭니다.\n"
        "\n"
    ),
    "14:30:4": "◇군단 상황 확인",
    "14:30:5": (
        '\n군단 내부의 상황과 문제는 "보고" 화면에서 확인할 수 있습니다.\n'
        "정기적으로 확인하여 문제가 생기지 않았는지 살펴봅시다."
    ),
    "14:31:0": "◇군단 지원",
    "14:31:1": (
        "\n군단 지원으로 지정한 군단에 물자와 군사 지원을 제공합니다.\n"
        "병력이나 병량의 수송을 건의하고, 지원 대상 군단이 출진하면 원군을 보내기도 합니다.\n"
        "\n"
        "다만 원군은 도달할 수 있는 범위에만 보낼 수 있으므로\n"
        "되도록 인접한 군단을 지원하게 하는 것이 좋습니다.\n"
        "\n"
    ),
    "14:31:2": "[휘하 군단의 내정]",
    "14:31:3": "\n휘하 군단의 내정은 군단장에게 일임됩니다.\n\n",
    "14:31:4": "◇휘하 군단의 군 개발",
    "14:31:5": "\n농촌과 시장 장악을 우선합니다.\n\n",
    "14:31:6": "◇휘하 군단의 성하 시설",
    "14:31:7": (
        '\n정책 "제도 개신" LV1과 "재량권 위양" LV1을 발령하면\n'
        '"성하 방침"을 정해 건설을 진행합니다.\n'
        "※농촌과 시장 장악을 우선합니다"
    ),
    "14:32:0": "[가신 논공행상]",
    "14:32:1": (
        "\n3개월마다 논공행상이 열려 훈공을 세운 가신이 승진합니다.\n"
        "이 화면에서는 무장의 훈공 내역과 승진한 무장 등을 확인할 수 있습니다.\n"
        "※확인하지 않아도 무장은 승진합니다\n"
        "\n"
    ),
    "14:32:2": "◇훈공 획득 방법",
    "14:32:3": (
        '\n\u3000·"대관"이나 "지행"으로 맡은 영지를 개발한다\n'
        "·실행 무장으로 명령을 실행한다\n"
        '·"건의"를 성공시킨다\n'
        '·"영내 문제"를 해결한다\n'
        "·행군이나 합전에서 세운 공적\n"
        '·"조두"로서 맡는 하급 업무(※정책 "호로슈 결성" 발령 필요)'
    ),
}

BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)
EXPECTED_ARITY = {29: 6, 30: 6, 31: 8, 32: 4}


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {29: 43, 30: 45, 31: 46, 32: 48}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 774 record has no configured PK mapping: {base_record_id}") from exc


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
    expected_divergences = {"JP": {29, 30, 32}, "SC": {29, 30}, "TC": {29, 30}}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(29, 33)
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
                f"segment 774 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected_arity in EXPECTED_ARITY.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 774 literal arity drifted: 14:{record_id}")
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
        "군단",
        "가문 내 역직",
        "군단 방침",
        "절취 허가",
        "상납금",
        "휘하 군단",
        "제도 개신",
        "재량권 위양",
        "논공행상",
        "훈공",
        "조두",
        "호로슈 결성",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 774 required terminology drifted")
    if "예하 군단" in joined or "행하겠습니다" in joined or "가문 내 직위" in joined:
        raise RuntimeError("segment 774 retains inconsistent or speaker-like system wording")
    if any(
        term in TRANSLATIONS["14:29:1"]
        for term in (
            "통치 범위",
            "군단 전략",
            "공성전",
            "군단장 이동",
            "군단장 변경",
            "강력한 건의",
            "지행",
        )
    ):
        raise RuntimeError("14:29 imported PK-only expanded corps guidance")
    if any(
        term in TRANSLATIONS["14:30:1"]
        for term in ("지원 대상 군단 소속", "지원하는 군단의 소속", "지원할 군단의 소속")
    ):
        raise RuntimeError("14:30 imported the PK-only support-affiliation bullet")
    if len(TRANSLATIONS) != 24 or set(TRANSLATIONS) != {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITY.items()
        for literal_id in range(arity)
    }:
        raise RuntimeError("segment 774 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S774",
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
