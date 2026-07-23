#!/usr/bin/env python3
"""Build Base authoring segment 783 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S783.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s783", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:74:0": "[기타 조작]",
    "14:74:1": (
        "\n\u3000"
        "·Z 키 ... 카메라를 북쪽으로 향함\n"
        "·Shift+마우스 휠 위아래 ... 카메라를 천천히 확대/축소\n"
        "·Home 키 ... 본거지로 이동\n"
        "·C 키 ... 기능 메뉴 열기\n"
        "·I 키 ... 정보 목록 열기\n"
        "·1~7 키 ... 뷰 전환"
    ),
    "14:75:0": "[국인중]",
    "14:75:1": (
        "\n"
        "국인중은 각지에 흩어진 소규모 세력으로, 무력으로는 지배할 수 없습니다.\n"
        "다만 주변 세력에 대한 종속도가 있으며\n"
        "종속도가 가장 높은 세력은 원군을 요청할 수 있습니다.\n"
        "자세력에 대한 종속도가 원군 요청 기준에 이른 국인중은 아이콘이 녹색으로 표시됩니다.\n"
        "\n"
        '또한 종속도가 충분히 높은 국인중은 "편입"을 통해\n'
        "자세력의 일부로 삼을 수도 있습니다.\n"
        "\n"
    ),
    "14:75:2": "◇국인중에 대한 대응",
    "14:75:3": (
        "\n\u3000"
        "·인근 영주가 국인중을 회유해 종속도를 높이기도 한다\n"
        "·영내 제책으로 국인중을 회유하도록 명할 수 있다\n"
        "·영내 제책으로 종속도가 충분히 높은 국인중을 편입하도록 명할 수 있다\n"
        "\n"
        "※원군으로 출진한 국인중 부대가 괴멸하면 종속도가 크게 낮아집니다"
    ),
    "14:76:0": "[기본 조작]",
    "14:76:1": (
        "\n\u3000"
        "㍑ ... 선택\n"
        "㍗ ... 취소\n"
        "㌦ ... 명령 메뉴 열기(메인 화면)\n"
        "㌍ ... 시간 진행/정지(메인 화면)\n"
        "      ※시간 진행 버튼을 누른 것과 동일\n"
        "      결정(각종 명령 실행)\n"
        "㌍ 길게 누르기㎝㌣ ... 진행 속도 변경\n"
        "\n"
        "㍍㎝㌣ ... 주변 메뉴로 커서 이동\n"
        "\n"
        "㌫ ... 카메라 회전\n"
        "㍉㎝㌫ ... 카메라 확대/축소\n"
        "\n"
        "㍉㎝㍑㎝㌣ ... 여러 부대 선택"
    ),
    "14:77:0": "[기타 조작]",
    "14:77:1": (
        "\n\u3000"
        "㌘ ... 보고 화면 열기\n"
        "㌢ ... 본거지로 이동\n"
        "㌧ ... 카메라를 북쪽으로 향함\n"
        "㍉㎝㌔㎝㌫ ... 카메라를 천천히 확대/축소\n"
        "㌶ ... 기능 메뉴 열기\n"
        "㌃ ... 뷰 전환"
    ),
    "14:78:0": "[기본 조작]",
    "14:78:1": (
        "\n\u3000"
        "㍑ ... 선택\n"
        "㍗ ... 취소\n"
        "㌦ ... 명령 메뉴 열기(메인 화면)\n"
        "㌍ ... 시간 진행/정지(메인 화면)\n"
        "      ※시간 진행 버튼을 누른 것과 동일\n"
        "      결정(각종 명령 실행)\n"
        "㌍ 길게 누르기㎝㌣ ... 진행 속도 변경\n"
        "\n"
        "㍍㎝㌣ ... 주변 메뉴로 커서 이동\n"
        "\n"
        "㌫ ... 카메라 회전\n"
        "㍉㎝㌫ ... 카메라 확대/축소\n"
        "\n"
        "㍉㎝㍑㎝㌣ ... 여러 부대 선택"
    ),
    "14:79:0": "[기타 조작]",
    "14:79:1": (
        "\n\u3000"
        "㌘ ... 보고 화면 열기\n"
        "㌢ ... 본거지로 이동\n"
        "㌧ ... 카메라를 북쪽으로 향함\n"
        "㍉㎝㌔㎝㌫ ... 카메라를 천천히 확대/축소\n"
        "㌶ ... 기능 메뉴 열기\n"
        "㌃ ... 뷰 전환"
    ),
    "14:80:0": "[이벤트 목록]",
    "14:80:1": (
        "\n"
        "게임 중 일정 조건을 충족하면 역사적 사건이 이벤트로 발생합니다.\n"
        '이벤트에는 역사적 사실에 근거한 것과 "노부나가의 야망·신생"의 오리지널 이벤트가 있으며\n'
        "자세력과 다른 세력의 상황에 영향을 주기도 합니다.\n"
        "자세력이 관련되면 대화 이벤트가 재생됩니다.\n"
        '자세력과 관련이 없다면 일부 이벤트는 건의 "풍문"으로 확인할 수 있습니다.\n'
        "\n"
    ),
    "14:80:2": '◇"이벤트 목록"에서 할 수 있는 일',
    "14:80:3": (
        "\n\u3000"
        "·각 이벤트의 발생을 유효/무효로 설정\n"
        "·각 이벤트의 발생 조건과 영향을 확인\n"
        "\n"
    ),
    "14:80:4": "◇보충",
    "14:80:5": (
        "\n\u3000"
        "자세력이 멸망하는 이벤트는 초기 상태에서 무효로 설정됩니다."
    ),
}

EXPECTED_ARITIES = {74: 2, 75: 4, 76: 2, 77: 2, 78: 2, 79: 2, 80: 6}
BASE_PK_DIVERGENCES = {
    "JP": {76, 77, 78, 79, 80},
    "SC": {76, 77, 78, 79},
    "TC": {74, 76, 77, 78, 79},
}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
CONTROLLER_GLYPHS = set("㌃㌔㌘㌢㌧㌫㌶㌍㌣㌦㍉㍍㍑㍗㎝")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {74: 101, 75: 103, 76: 104, 77: 105, 78: 107, 79: 108, 80: 111}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 783 record has no configured PK mapping: {base_record_id}") from exc


def expected_gaps(arity: int) -> tuple[bytes, ...]:
    return tuple(
        part
        for _ in range(arity // 2)
        for part in (b"\x1b\x43\x49", b"\x1b\x43\x5a")
    ) + (b"\x05\x05\x05",)


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


def assert_available_duplicate_decision(coordinate: str, translation: str) -> None:
    if not OUTPUT.parent.is_dir():
        return
    for decision_path in OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl"):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate and row.get("translation") != translation:
                raise RuntimeError(f"duplicate translation differs from {coordinate}")


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


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

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(74, 81)
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
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 783 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 783 literal arity drifted: 14:{record_id}")
        if record_gaps(source_records[(14, record_id)]) != expected_gaps(expected_arity):
            raise RuntimeError(f"segment 783 pristine literal/opcode boundary drifted: 14:{record_id}")
        if record_gaps(current_records[(14, record_id)]) != expected_gaps(expected_arity):
            raise RuntimeError(f"segment 783 current literal/opcode boundary drifted: 14:{record_id}")
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(f"segment 783 unexpectedly contains a blank literal: 14:{record_id}")

    if TRANSLATIONS["14:75:0"] != prior_translation("14:12:0"):
        raise RuntimeError("14:75:0 must exactly reuse the approved [국인중] translation")
    source_75 = ENGINE.parse_record_literals(source_records[(14, 75)])[0].text
    current_75 = ENGINE.parse_record_literals(current_records[(14, 75)])[0].text
    source_12 = ENGINE.parse_record_literals(source_records[(14, 12)])[0].text
    current_12 = ENGINE.parse_record_literals(current_records[(14, 12)])[0].text
    if source_75 != source_12 or current_75 != current_12:
        raise RuntimeError("14:75:0 exact [국인중] source/current reuse drifted")

    for record_id in (74, 77, 79):
        source_title = ENGINE.parse_record_literals(source_records[(14, record_id)])[0].text
        current_title = ENGINE.parse_record_literals(current_records[(14, record_id)])[0].text
        if source_title != ENGINE.parse_record_literals(source_records[(14, 74)])[0].text:
            raise RuntimeError(f"14:{record_id}:0 pristine 기타 조작 title drifted")
        if current_title != ENGINE.parse_record_literals(current_records[(14, 74)])[0].text:
            raise RuntimeError(f"14:{record_id}:0 current 기타 조작 title drifted")
    if len({TRANSLATIONS[f"14:{record_id}:0"] for record_id in (74, 77, 79)}) != 1:
        raise RuntimeError("14:74:0, 14:77:0, and 14:79:0 must translate exactly alike")

    for literal_id in (0, 1):
        if (
            ENGINE.parse_record_literals(source_records[(14, 76)])[literal_id].text
            != ENGINE.parse_record_literals(source_records[(14, 78)])[literal_id].text
        ):
            raise RuntimeError(f"14:76:{literal_id} pristine exact reuse drifted")
        if (
            ENGINE.parse_record_literals(current_records[(14, 76)])[literal_id].text
            != ENGINE.parse_record_literals(current_records[(14, 78)])[literal_id].text
        ):
            raise RuntimeError(f"14:76:{literal_id} current exact reuse drifted")
        if TRANSLATIONS[f"14:76:{literal_id}"] != TRANSLATIONS[f"14:78:{literal_id}"]:
            raise RuntimeError(f"14:76:{literal_id} and 14:78:{literal_id} must translate exactly alike")

    source_80 = ENGINE.parse_record_literals(source_records[(14, 80)])[4].text
    current_80 = ENGINE.parse_record_literals(current_records[(14, 80)])[4].text
    source_47 = ENGINE.parse_record_literals(source_records[(14, 47)])[4].text
    current_47 = ENGINE.parse_record_literals(current_records[(14, 47)])[4].text
    if source_80 != source_47 or current_80 != current_47:
        raise RuntimeError("14:80:4 exact ◇補足 source/current reuse drifted")
    if TRANSLATIONS["14:80:4"] != "◇보충":
        raise RuntimeError("14:80:4 must preserve the canonical ◇보충 translation")
    assert_available_duplicate_decision("14:47:4", TRANSLATIONS["14:80:4"])

    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/token layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} controller-glyph skeleton drifted")

    expected_u3000 = {
        "14:74:1",
        "14:75:3",
        "14:76:1",
        "14:77:1",
        "14:78:1",
        "14:79:1",
        "14:80:3",
        "14:80:5",
    }
    actual_u3000 = {
        coordinate for coordinate, translation in TRANSLATIONS.items() if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError("segment 783 protected U+3000 coordinates drifted")
    if any(TRANSLATIONS[coordinate].count("\u3000") != 1 for coordinate in expected_u3000):
        raise RuntimeError("segment 783 protected U+3000 count drifted")

    control_text = "\n".join(
        TRANSLATIONS[f"14:{record_id}:1"] for record_id in range(74, 80)
    )
    if "㍊" in control_text or any(term in control_text for term in ("중계점", "경유점", "성 선택")):
        raise RuntimeError("segment 783 imported PK-only controller operations")
    event_text = "\n".join(TRANSLATIONS[f"14:80:{literal_id}"] for literal_id in range(6))
    if any(term in event_text for term in ("이벤트 합전", "승패에 따라", "전투 재현")):
        raise RuntimeError("14:80 imported the PK-only 14:112 event-battle explanation")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "본거지",
        "국인중",
        "편입",
        "이벤트 목록",
        "건의",
        "풍문",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 783 required terminology drifted")
    if any(term in joined for term in ("본거로", "호족", "노력")):
        raise RuntimeError("segment 783 retains a forbidden legacy term")
    if len(TRANSLATIONS) != 20:
        raise RuntimeError("segment 783 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S783",
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
