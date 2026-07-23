#!/usr/bin/env python3
"""Build Base authoring segment 780 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S780.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s780", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:55:0": "◇공성전",
    "14:55:1": (
        '\n적 성과 접촉하면 "포위"가 시작됩니다.\n'
        '"강공"으로 변경할 수도 있습니다.\n'
        "\n"
        " ·성의 내구를 0으로 만들면 성을 제압한다\n"
        " ·여러 길에서 성을 포위하면 유리해진다\n"
        ' ·"포위"는 시간이 걸리지만 반격을 받지 않는다\n'
        " ·포위 중 피해는 부대 측의 포위와 성 측의 대포위로 결정된다\n"
        ' ·"강공"은 성에 큰 피해를 주지만 반격을 받는다\n'
        " ·강공 중 피해는 부대 측의 공격과 성 측의 방어로 결정된다\n"
        " ·성에 방위 설비가 있으면 포위 중에도 강력한 반격을 받는다\n"
        " ·방위 설비는 성내 병사가 출진 중이어도 발동할 수 있다\n"
        " ·적 부대와 교전 중에는 공성전을 할 수 없다"
    ),
    "14:56:0": "◇부대 능력",
    "14:56:1": (
        "\n각 무장은 자신의 지행지에 있는 병사를 이끌고 각 성에 집결해\n"
        "하나의 부대로 출진합니다.\n"
        "\n"
        "지위가 가장 높은 무장이 부대장을 맡습니다.\n"
        "부대 능력은 성 능력과 같은 방식으로 정해집니다."
    ),
    "14:57:0": "◇부대 능력·상세",
    "14:57:1": (
        "\n\u3000·방어     ... 무장의 통솔에 따라 결정된다\n"
        "           부대가 받는 피해를 줄인다\n"
        " ·공격     ... 무장의 무용에 따라 결정된다\n"
        "           적 부대에 주는 피해와 강공 시\n"
        "           적 성에 주는 피해에 영향을 준다\n"
        " ·포위     ... 무장의 지략에 따라 결정된다\n"
        "           포위 시 적 성에 주는 피해에 영향을 준다\n"
        " ·휴대 군량   ... 출진 후 활동할 수 있는 일수\n"
        "           병량이 떨어지면 병력이 조금씩 감소한다\n"
        " ·기마/철포 LV ... 드물게 LV에 따라 위력이 오르는 공격을 한다\n"
        " ·특성     ... 무장이 지닌 특성의 합계. 같은 특성을 지닌 무장\n"
        "           이 여럿이면 특성 LV가 최대 5까지 오른다"
    ),
    "14:58:0": "◇부대 능력·보충",
    "14:58:1": (
        "\n\u3000·성의 병량이 병력보다 적으면 휴대 군량의 지속 일수가 줄어든다\n"
        " ·임전 상태인 무장이 있으면 부대 능력과 휴대 군량의 지속 일수가 늘어난다\n"
        " ·위신이 높은 세력을 공격하면 위축되어 부대 능력이 낮아진다\n"
        " ·자신의 성이 아닌 다른 성에 입성한 부대는 병사와 무장이 서서히 자기 성으로 돌아간다"
    ),
    "14:59:0": "◇합전",
    "14:59:1": (
        "\n적 부대와 접촉하면 전투가 시작됩니다.\n"
        "이때 다이묘 부대가 전투에 참가 중이거나 근처에 있으면\n"
        '다이묘 부대의 메뉴에서 "합전"을 벌일 수 있습니다.\n'
        "합전에서는 전용 전장에서 아군과 적군이 최대 16개 부대씩 싸웁니다.\n"
        '※합전이 가능하면 다이묘 부대에 "합전 가능"이 표시됩니다\n'
        "\n"
    ),
    "14:59:2": "◇합전을 하면",
    "14:59:3": (
        '\n\u3000·승리하면 참전한 부대 수에 따라 "위풍"이 발생한다\n'
        ' ·"위풍"이 발생하면 주변의 성이나 군, 국인중이 돌아설 수 있다\n'
        '  ※패배하면 적의 "위풍"을 받을 수 있으므로 주의합시다'
    ),
    "14:60:0": "[처우 선택]",
    "14:60:1": (
        "\n포박한 무장의 처우를 결정합니다.\n"
        "\n"
        " ·등용 ... 자세력에 출사하도록 권한다\n"
        " ·처단 ... 처단된 무장은 해당 게임에서\n"
        "       다시는 등장하지 않는다\n"
        " ·해방 ... 아무 조치 없이 풀어 준다. 다시 포박하면 등용에 응하기 쉬워진다\n"
        "\n"
    ),
    "14:60:2": "◇등용에 성공하려면",
    "14:60:3": (
        "\n\u3000·충성이 최대이면 절대로 등용에 응하지 않는다\n"
        " ·충성이 낮을수록 등용에 응하기 쉽다\n"
        " ·주가가 멸망했으면 등용에 응하기 쉽다\n"
        " ·여러 번 포박될수록 등용에 응하기 쉬워진다"
    ),
    "14:61:0": "[군평정]",
    "14:61:1": (
        "\n합전 전에 열리는 군평정에서는\n"
        "아군 부대의 포진과 행동 예정을 확인할 수 있습니다.\n"
        "아군 부대의 포진 위치와 출진 부대를 선택할 수 있습니다.\n"
        "\n"
    ),
    "14:61:2": "◇출진 부대 선발",
    "14:61:3": (
        "\n출진 부대 선발에서는 처음 출진할 8개 부대를 선택합니다.\n"
        "여기서 선택하지 않은 부대도 출진 부대가 괴멸하거나 퇴각하면\n"
        "교대로 출진합니다.\n"
        "\n"
    ),
    "14:61:4": "◇포진 변경",
    "14:61:5": (
        "\n포진 변경에서는 부대의 배치 위치를 바꿉니다.\n"
        "2개 부대를 차례로 선택하면 위치가 서로 바뀝니다.\n"
        "\n"
    ),
    "14:61:6": "◇개전",
    "14:61:7": "\n현재 설정으로 합전을 시작합니다.",
}

BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("◇")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)
EXPECTED_ARITY = {55: 2, 56: 2, 57: 2, 58: 2, 59: 4, 60: 4, 61: 8}


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {55: 78, 56: 80, 57: 81, 58: 82, 59: 83, 60: 85, 61: 86}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 780 record has no configured PK mapping: {base_record_id}") from exc


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
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
    expected_divergences = {"JP": {55}, "SC": {55}, "TC": {55}}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(55, 62)
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
                f"segment 780 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected_arity in EXPECTED_ARITY.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 780 literal arity drifted: 14:{record_id}")
    for coordinate, translation in TRANSLATIONS.items():
        _, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(14, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/token layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} retains CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} protected-glyph skeleton drifted")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "공성전",
        "부대",
        "방어",
        "공격",
        "포위",
        "대포위",
        "휴대 군량",
        "합전",
        "국인중",
        "처우 선택",
        "군평정",
        "출진",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 780 required terminology drifted")
    if TRANSLATIONS["14:55:0"] != "◇공성전":
        raise RuntimeError("14:55 Base 공성전 heading drifted toward mapped PK")
    if TRANSLATIONS["14:56:0"] != "◇부대 능력":
        raise RuntimeError("14:56:0 cross-segment exact translation drifted")
    if any(term in TRANSLATIONS["14:55:1"] for term in ("돌 떨구기", "투포락")):
        raise RuntimeError("14:55 imported PK-specific defensive equipment names")
    if {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITY}.intersection({79, 84}):
        raise RuntimeError("segment 780 mapped a PK-only castle-attack or siege page")
    if any(
        term in joined
        for term in ("군량이 떨어지면", "호족", "자기 세력에 사관", "이쿠사효조")
    ):
        raise RuntimeError("segment 780 retains a forbidden terminology variant")
    expected_coordinates = {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITY.items()
        for literal_id in range(arity)
    }
    if len(TRANSLATIONS) != 24 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 780 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S780",
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
