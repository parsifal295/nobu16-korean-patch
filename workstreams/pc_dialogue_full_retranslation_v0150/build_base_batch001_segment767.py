#!/usr/bin/env python3
"""Build Base authoring segment 767 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S767.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s767", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:470:0": (
        "여러 방향에서 공격받는 부대가 있는 듯합니다.\n"
        '이 상태를 "협격"이라 하며, 협격당한 부대는 능력이 낮아집니다.\n'
        "\n"
        "전황에 큰 영향을 미칠 수도 있으므로\n"
        "행군 중에는 적 부대를 협격할 수 있도록 진군로를 조정하고\n"
        "아군 부대가 협격당하지 않도록 적의 움직임에 주의합시다."
    ),
    "13:471:0": '"조략"',
    "13:472:0": (
        "다른 세력에 조략을 실행하면 그 힘을 약화할 수 있습니다.\n"
        "적대할 가능성이 있는 상대에게는 미리 조략을 실행해 둡시다.\n"
        "\n"
        "[조략을 명하는 법]\n"
        "①명할 내용을 정한다\n"
        "②조략을 실행할 대상을 정한다\n"
        "③실행할 무장을 정한다"
    ),
    "13:473:0": '"공략 개시"',
    "13:474:0": (
        "병력이 적은 세력이 주변에 있다면 침공하여 영토를 넓힐 기회입니다.\n"
        "내정으로 늘린 병사를 출진시켜 적의 성을 공격합시다.\n"
        "\n"
        "언제 침공할지 판단하는 것은 플레이어의 실력을 발휘할 대목이지만\n"
        "한동안 출진하지 않으면 가신이 출진을 건의해 오므로\n"
        "이를 계기로 출진하는 것도 좋습니다."
    ),
    "13:475:0": (
        "[출진 시기의 예]\n"
        "·병력이 적고 자세력보다 약한 상대가 있다\n"
        "·평소에는 자세력보다 강하지만 다른 곳에 출진하여 방비가 약해졌다\n"
        "·조략이 성공하여 영내에서 잇키가 일어났다"
    ),
    "13:476:0": '"영내 문제"',
    "13:477:0": (
        "영내의 군에서는 무장을 파견하지 않으면 해결하기 어려운 문제가 생기기도 합니다.\n"
        "더 빨리 해결하려면 무장을 파견합시다.\n"
        "\n"
        "[문제의 종류]\n"
        "◇영내 황폐\n"
        "◇국경 분쟁\n"
        "◇상위 취락 건설"
    ),
    "13:478:0": (
        "[영내 황폐]\n"
        "·빨리 해결하지 않으면 잇키가 일어나기도 한다\n"
        "·전투나 조략, 재해의 피해를 입은 군에서 생기기도 한다\n"
        "\n"
        "[국경 분쟁]\n"
        "·무장을 파견하지 않으면 적의 군을 제압하려고 독단으로 출진하기도 한다\n"
        "·독단으로 군을 제압하면 공성전까지 이어질 수도 있다\n"
        '·성주가 특성 "혈기"를 지녔거나 "무용 60 이상, 지략 60 미만"인 성에서 발생한다'
    ),
    "13:479:0": (
        "[상위 취락 건설]\n"
        "·강력한 효과가 있는 상위 취락을 건설할 수 있다\n"
        "·군 개발을 진행하면 발생한다"
    ),
    "13:480:0": '"전봉"',
    "13:481:0": (
        "다이묘 군단 내 무장의 지행지를 한꺼번에 변경할 수 있습니다.\n"
        '정책 "제도 개신" LV2로 해금됩니다.\n'
        "\n"
        "[변경 방법]\n"
        "◇이동 … 두 성 사이에서 무장의 지행지를 서로 바꾼다\n"
        "       ※본거지의 무장은 지행지가 없으므로 선택할 수 없다\n"
        "◇호출 … 군단 내 무장을 불러 지정한 성의 군을 내린다"
    ),
    "13:482:0": '"성하 방침"',
    "13:483:0": (
        '정책 "제도 개신"을 발령하면 "성하 방침"을 설정할 수 있습니다.\n'
        '"성하 방침"을 정하면 성주가 자율적으로 건설합니다.\n'
        "비용이 들지 않으므로 성주의 재량에 맡기는 것도 좋습니다.\n"
        "\n"
        "[성하 방침의 특징]\n"
        "·성주가 자율적으로 건설한다(비용 불필요)\n"
        "·설정한 동안 성마다 노동력 1을 사용한다\n"
        "·건설 속도는 성 능력에 따라 다르다"
    ),
    "13:484:0": (
        '또한 정책을 발령하여 "성하 방침"을 강화할 수 있습니다.\n'
        '각 방침의 "건설 예정"을 참고하여 상황에 맞게 설정합시다.\n'
        "\n"
        "[성하 방침 강화]\n"
        '·정책 "제도 개신" LV2로 증축도 하게 된다\n'
        '·정책 "재량권 위양" LV1로 설정에 노동력을 소비하지 않게 된다'
    ),
    "13:485:0": '"지방 통일"',
    "13:486:0": (
        "특정 지방을 제압하면\n"
        "지방 통일 엔딩을 맞이할 수 있습니다.\n"
        "지방 통일 엔딩 후에도 게임을 계속할 수 있습니다.\n"
        "\n"
        "[지방 통일 엔딩 조건]\n"
        "·시나리오 시작 시 본거지가 있는 지방의 모든 성을 지배하에 둔다"
    ),
    "13:487:0": '"출진 부대 편제"',
    "13:488:0": (
        "출진할 부대와 성에 남길 부대를 바꿀 수 있습니다.\n"
        "\n"
        "㌘를 누르면 목록과 지도를 오갈 수 있습니다."
    ),
    "13:489:0": '"군 탈환"',
    "13:490:0": (
        "성 주변의 군을 적에게 빼앗기면 무장이 스스로 판단하여\n"
        "군을 탈환하러 출진하기도 합니다.\n"
        "\n"
        "기본적으로 명령할 필요는 없지만 주변에 원군으로 보내고 싶을 때는\n"
        "직접 명령하여 목표를 변경합시다."
    ),
    "13:491:0": '"쇠퇴한 세력에서 출분"',
    "13:492:0": (
        "많은 성을 적에게 제압당하면\n"
        "충성이 낮은 무장은 자세력을 저버리고 출분하여 적 세력으로 돌아서려 합니다.\n"
        "\n"
        "제압당한 성이 늘어날수록 많은 무장이 출분하여 인재 부족이 심해지고\n"
        "반대로 제압한 쪽은 무장을 등용하여 세력을 강화할 수 있습니다."
    ),
}

BASE_PK_DIVERGENCES = {
    "JP": set(),
    "SC": {478},
    "TC": {478, 486},
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】")
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 470 <= base_record_id <= 477:
        return base_record_id + 42
    if 478 <= base_record_id <= 479:
        return base_record_id + 43
    if 480 <= base_record_id <= 492:
        return base_record_id + 44
    raise RuntimeError(f"segment 767 record has no configured PK mapping: {base_record_id}")


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


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


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
            for record_id in range(470, 493)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 767 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    for record_id in range(470, 493):
        source_literals = ENGINE.parse_record_literals(source_records[(13, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(13, record_id)])
        if len(source_literals) != 1 or len(current_literals) != 1:
            raise RuntimeError(f"segment 767 record must remain one static literal: 13:{record_id}")

    if source_records[(13, 471)].data != source_records[(13, 262)].data:
        raise RuntimeError("pristine exact reuse drifted: 13:471 != 13:262")
    if current_records[(13, 471)].data != current_records[(13, 262)].data:
        raise RuntimeError("current exact reuse drifted: 13:471 != 13:262")
    if TRANSLATIONS["13:471:0"] != prior_translation("13:262:0"):
        raise RuntimeError("13:471 must exactly reuse the approved 13:262 translation")

    for coordinate, translation in TRANSLATIONS.items():
        record_id = int(coordinate.split(":")[1])
        current_text = ENGINE.parse_record_literals(current_records[(13, record_id)])[0].text
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(f"{coordinate} line-count contract drifted")
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} controller-glyph skeleton drifted")

    if glyph_skeleton(TRANSLATIONS["13:488:0"]) != ["㌘"]:
        raise RuntimeError("13:488 exact controller glyph drifted")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "협격",
        "조략",
        "건의",
        "잇키",
        "영토",
        "영내",
        "군",
        "전봉",
        "지행지",
        "제도 개신",
        "재량권 위양",
        "성하 방침",
        "노동력",
        "지방 통일",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 767 required terminology drifted")
    if (
        "호족" in joined
        or "노력" in joined
        or "책략" in joined
        or "재량권 이양" in joined
    ):
        raise RuntimeError("segment 767 retains a forbidden legacy term")
    if TRANSLATIONS["13:484:0"].count("재량권 위양") != 1:
        raise RuntimeError("13:484 must retain the public policy label 재량권 위양")
    if len(TRANSLATIONS) != 23:
        raise RuntimeError("segment 767 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S767",
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
