#!/usr/bin/env python3
"""Build Base authoring segment 781 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S781.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s781", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:62:0": "◇부대 능력",
    "14:62:1": (
        "\n\u3000·기동 ... 이동 속도\n"
        " ·공격 ... 높을수록 적의 병력을 줄이기 쉽다\n"
        "       주로 무장의 무용이 영향을 준다\n"
        " ·방어 ... 높을수록 병력과 체력이 줄어들기 어렵다\n"
        "       주로 무장의 통솔이 영향을 준다\n"
        "\n"
    ),
    "14:62:2": "◇전법",
    "14:62:3": (
        "\n\u3000·부대를 이끄는 무장이 하나씩 보유한다\n"
        " ·무장이 자발적으로 발동하지만 발동을 명령할 수도 있다\n"
        " ·능력 상승, 적 병력 감소, 혼란 부여 등의 효과가 있다"
    ),
    "14:63:0": "◇사기",
    "14:63:1": (
        "\n사기는 합전의 승패에 큰 영향을 줍니다.\n"
        "적의 사기를 0으로 만들면 합전에서 승리할 수 있으므로\n"
        "적의 사기를 낮추는 데 유의합시다.\n"
        "\n"
        '"퇴각로"와 "요충지"를 제압하면 적의 사기가 내려갑니다.\n'
        "※적에게 제압당하면 아군의 사기가 내려갑니다\n"
        "\n"
        "사기 상태는 게이지로 확인할 수 있습니다.\n"
        "※게이지가 모두 파란색이 되면 승리"
    ),
    "14:64:0": "[합전: 기본 규칙]",
    "14:64:1": (
        "\n적군과 아군의 부대가 한 전장에 모여 승패를 가리는 것이 합전입니다.\n"
        "무장들은 승리와 공명을 위해 스스로 판단하여 부대를 움직이고 싸웁니다.\n"
        "다만 전황이 달라지면 판단을 요청해 올 때도 있습니다.\n"
        "기회와 위기에 어떻게 대응하느냐가 합전의 승패를 좌우합니다."
    ),
    "14:65:0": "◇승리 조건",
    "14:65:1": (
        "\n다음 중 하나를 달성한 진영이 승리합니다.\n"
        ' ①적의 "총사기"를 0으로 만든다\n'
        " ②적 부대를 모두 격파한다\n"
        ' ③적의 "퇴각로"를 모두 파괴한다\n'
        " ④적 다이묘를 쓰러뜨린다"
    ),
    "14:66:0": "◇부대",
    "14:66:1": (
        "\n부대는 적 부대나 퇴각로, 요충지를 공격합니다.\n"
        " ·동시에 8개 부대까지 출진할 수 있다\n"
        "  남은 부대는 출진 중인 부대가 괴멸하거나 퇴각하면 출진한다\n"
        " ·전장에 표시된 선 위를 이동하며\n"
        "  적 부대와 접촉하면 공격한다\n"
        " ·평소에는 스스로 판단해 이동·공격하지만\n"
        "  플레이어가 지시할 수도 있다\n"
        "\n"
        "※지시할 때 Shift+좌클릭으로 중계점을 설정할 수 있습니다"
    ),
    "14:67:0": "◇부대",
    "14:67:1": (
        "\n부대는 적 부대나 퇴각로, 요충지를 공격합니다.\n"
        " ·동시에 8개 부대까지 출진할 수 있다\n"
        "  남은 부대는 출진 중인 부대가 괴멸하거나 퇴각하면 출진한다\n"
        " ·전장에 표시된 선 위를 이동하며\n"
        "  적 부대와 접촉하면 공격한다\n"
        " ·평소에는 스스로 판단해 이동·공격하지만\n"
        "  플레이어가 지시할 수도 있다\n"
        "\n"
        "※지시할 때 ㌘+㍑로 중계점을 설정할 수 있습니다"
    ),
    "14:68:0": "◇퇴각로",
    "14:68:1": (
        "\n각 진영에서 부대가 퇴각하는 출입구가 퇴각로입니다.\n"
        "모두 파괴되면 패배합니다.\n"
        " ·예비 부대의 출진 지점이 된다\n"
        ' ·부대의 공격으로 내구력을 0으로 만들면 "파괴"된다\n'
        " ·파괴되면 모든 부대가 혼란에 빠지고 능력이 낮아지며, 진영의 총사기가 내려간다"
    ),
    "14:69:0": "◇요충지",
    "14:69:1": (
        "\n전장에 흩어진 중요 지점이 요충지입니다.\n"
        "많이 제압할수록 전투가 유리해집니다.\n"
        ' ·내구를 0으로 만들면 "제압"된다\n'
        " ·제압하면 모든 부대의 능력이 상승하고, 진영의 총사기가 올라간다\n"
        "\n"
        '발동 효과가 있는 "특수 요충지"도 존재합니다.\n'
        "제압하고 잠시 지나면 요충지 위의 버튼으로 특별한 효과를\n"
        "발동할 수 있습니다."
    ),
    "14:70:0": "[특성]",
    "14:70:1": (
        '\n일부 무장은 "특성"을 보유하고 있습니다.\n'
        "특성은 본인뿐 아니라 성이나 부대 등에도 영향을 줍니다.\n"
        "일부 특성은 직명이 조건인 경우도 있습니다.\n"
        "※국인중 무장은 직명 조건과 관계없이 모든 특성을 발동할 수 있습니다\n"
        "\n"
    ),
    "14:70:2": "◇세력 전체에 영향을 주는 예",
    "14:70:3": (
        '\n다이묘가 특성 "의로운 장수"를 보유한 상태에서 아군 세력이 적의 공격을 받으면\n'
        "세력 내 모든 성이 임전 상태가 됩니다.\n"
        "\n"
    ),
    "14:70:4": "◇부대에 영향을 주는 예",
    "14:70:5": (
        '\n특성 "성타기"를 보유한 무장이 부대에 있으면\n'
        "그 부대가 적 성에 주는 내구 피해가 늘어납니다.\n"
        "\n"
        '일부 특성은 다음과 같은 경우 "강화"될 수 있습니다.\n'
        " ·같은 성에 같은 특성을 보유한 무장이 여럿 있다\n"
        " ·대응하는 성 능력이 80, 90을 넘는다"
    ),
}

BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("◇①②③④㌘㍑")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)
EXPECTED_ARITY = {62: 4, 63: 2, 64: 2, 65: 2, 66: 2, 67: 2, 68: 2, 69: 2, 70: 6}


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {62: 87, 63: 88, 64: 89, 65: 90, 66: 91, 67: 92, 68: 93, 69: 94, 70: 95}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 781 record has no configured PK mapping: {base_record_id}") from exc


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
    expected_divergences = {"JP": {70}, "SC": set(), "TC": set()}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(62, 71)
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
                f"segment 781 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected_arity in EXPECTED_ARITY.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 781 literal arity drifted: 14:{record_id}")
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
        "부대",
        "전법",
        "사기",
        "합전",
        "퇴각로",
        "요충지",
        "특성",
        "성타기",
        "의로운 장수",
        "국인중",
        "출진",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 781 required terminology drifted")
    if TRANSLATIONS["14:62:0"] != "◇부대 능력":
        raise RuntimeError("14:62:0 cross-segment exact translation drifted")
    if TRANSLATIONS["14:66:0"] != TRANSLATIONS["14:67:0"]:
        raise RuntimeError("14:66:0 and 14:67:0 exact translation drifted")
    if glyph_skeleton(TRANSLATIONS["14:65:1"]) != list("①②③④"):
        raise RuntimeError("14:65:1 numbered-glyph sequence drifted")
    if "명소" in TRANSLATIONS["14:70:5"]:
        raise RuntimeError("14:70 imported PK-only extra trait-page guidance")
    if 96 in {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITY}:
        raise RuntimeError("segment 781 mapped the PK-only expanded trait page")
    if any(term in joined for term in ("호족", "철수")):
        raise RuntimeError("segment 781 retains a forbidden terminology variant")
    expected_coordinates = {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITY.items()
        for literal_id in range(arity)
    }
    if len(TRANSLATIONS) != 24 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 781 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S781",
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
