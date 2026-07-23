#!/usr/bin/env python3
"""Build Base authoring segment 761 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S761.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s761", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:342:0": '"조작 설명"',
    "13:343:0": (
        "㍑      … 선택\n"
        "㌍      … 결정\n"
        "㌦      … 명령 메뉴 열기(메인 화면)\n"
        "㍗      … 취소(각종 메뉴나 창이 열려 있을 때)\n"
        "㍍㎝㌣ … 주변 메뉴로 커서 이동\n"
        "㌍      … 시간 진행/정지(메인 화면)\n"
        "          ※각종 메뉴가 열린 동안에는 시간이 정지"
    ),
    "13:344:0": (
        "【힌트】\n"
        "게임의 기본 흐름은 화면 왼쪽의 목록에서 고쇼가 설명합니다.\n"
        "무엇을 해야 할지 모르겠다면 이야기를 들어 봅시다.\n"
        '곤란할 때는 화면 오른쪽 위의 "도움말"을 확인해 봅시다.\n'
        "각 메뉴는 ㍍㎝㌣(으)로 이동할 수 있습니다."
    ),
    "13:345:0": '"군단"',
    "13:346:0": (
        "가신을 군단장으로 임명해 여러 성을 맡깁니다.\n"
        "통치 범위 밖의 성에는 다이묘의 지시가 닿지 않고 금전 수입도 크게 줄어드니\n"
        "군단에 맡기는 것이 좋습니다.\n"
        "\n"
        "【군단이란】\n"
        "·군단장이 지휘하므로 직접 명령할 수 없다\n"
        "·군단 방침으로 활동 내용을 정할 수 있다\n"
        "·매달 다이묘 군단에 상납금으로 금전을 보낸다"
    ),
    "13:347:0": (
        "【통치 범위란】\n"
        "·다이묘나 군단장의 본거지에서 일정 거리 이상 떨어진 성은 통치 범위 밖이 된다\n"
        "·성이 통치 범위 밖이면 그 성에서 얻는 금전 수입이 크게 줄어든다"
    ),
    "13:348:0": (
        "【군단 방침】\n"
        "군단 방침을 설정하면 군단장은 그 방침에 따라 군단을 운영합니다.\n"
        '군단장에게 성을 공격할 시점을 맡기려면 "위임 공략"이나 "성 공략"을,\n'
        '다른 군단을 지원하게 하려면 "군단 지원"을 지시합시다.\n'
        "\n"
        "【다른 군단 지원】\n"
        "·다른 군단의 성에 병력이나 군량을 수송하겠다고 건의한다\n"
        '·"군단 지원"으로 지정한 군단이 출진했을 때 닿는 범위라면 원호한다'
    ),
    "13:349:0": '"외교"',
    "13:350:0": (
        "싸움만이 천하통일로 가는 길은 아닙니다.\n"
        "다른 세력과 동맹하면 적을 줄이고 아군을 늘릴 수 있습니다.\n"
        "상대로부터 충분한 신용을 얻어야 하므로 평소부터 외교에 힘씁시다.\n"
        "\n"
        "【외교 진행 방법】\n"
        '·"친선"으로 상대의 신용을 높인다\n'
        "  ※외교 자세가 좋은 상대일수록 신용이 오르기 쉽다\n"
        '·신용을 소비해 동맹이나 원군 등의 "교섭"을 진행한다'
    ),
    "13:351:0": (
        "외교 상대를 고르기 어렵다면 싸우는 동안 방해받지 않도록\n"
        "주변의 적대 세력(공격하려는 상대 제외)과 동맹하는 것을 권합니다.\n"
        "\n"
        "【외교의 이점】\n"
        "◇동맹 … 서로 전투가 발생하지 않는다\n"
        "◇원군 … 다른 세력과 싸울 때 동맹 세력에 원군을 요청할 수 있다\n"
        "◇신종 … 강대한 다른 세력의 휘하에 들어가 출진 명령을 따르는 대신\n"
        "          다른 세력의 침공으로부터 보호받을 수 있다"
    ),
    "13:352:0": (
        "막부(다이묘가 정이대장군인 세력)와 외교하여 역직을 얻을 수 있습니다.\n"
        "역직을 얻어 위신이 높아지면 여러 이점이 생깁니다.\n"
        "※막부 세력과는 거리에 상관없이 외교할 수 있습니다\n"
        "\n"
        "【위신을 높이는 이점】\n"
        "·정책을 발령할 수 있다\n"
        "·상대보다 위신이 높으면 침공한 적병이 위축되어 유리하게 싸울 수 있다\n"
        "·자신보다 위신이 낮은 세력과의 외교가 유리해진다"
    ),
    "13:353:0": '"지행"-영주의 내정 활동-',
    "13:354:0": (
        "영주가 영지 개발을 시작해 수입과 병력을 늘리려 합니다.\n"
        "군의 발전은 성의 발전, 나아가 다이묘 가문 전체의 강화로 이어집니다.\n"
        "가신에게 적극적으로 영지를 내려 능력을 발휘하게 합시다.\n"
        "\n"
        "【영주의 주요 활동】\n"
        "◇장악 … 군의 농촌 등 취락을 완전히 복속시켜 수입을 늘린다\n"
        "◇건설 … 개발 용지에 새 취락을 지어 그 효과를 얻는다"
    ),
    "13:356:0": '"군 개발"-개발 완료와 대관 임명-',
    "13:357:0": (
        "군 개발이 완료되었습니다.\n"
        "금전과 노동력에 여유가 있다면 개발을 계속해 본거지를 발전시킵시다.\n"
        "※군의 모든 취락을 장악하거나 모든 개발 용지에 건설하면 석고가 추가로 상승합니다\n"
        "\n"
        "【대관 임명】\n"
        "본거지의 군에 대관을 임명하면 명령 없이도 자율적으로 개발합니다.\n"
        "신분은 필요하지 않으므로 한가한 무장은 적극적으로 대관에 임명합시다."
    ),
    "13:358:0": '"성하 시설"-완성-',
    "13:359:0": (
        "성하 시설이 완성되어 그 효과를 얻을 수 있게 되었습니다.\n"
        "지행이나 군 개발과 더불어 성하 시설 건설은 성을 강화하는 중요한 축입니다.\n"
        "금전과 노동력을 사용해 적극적으로 건설합시다.\n"
        "\n"
        "【건설과 증축】\n"
        "◇건설 … 빈 구획에 새로운 성하 시설을 짓는다\n"
        "◇증축 … 완성된 시설을 강화하여 더 높은 효과를 얻는다\n"
        "          ※증축하려면 성하가 어느 정도 발전해야 한다"
    ),
    "13:360:0": (
        '또한 "성하 방침"을 정하면 성주가 자율적으로 건설합니다.\n'
        "비용이 들지 않으므로 성주의 재량에 맡기는 것도 좋습니다.\n"
        "\n"
        "【성하 방침】\n"
        '·정책 "제도 개신" LV1로 해금\n'
        "·성주가 자율적으로 건설(비용 불필요)\n"
        "·설정한 성마다 노동력 1을 사용\n"
        '·정책 "제도 개신" LV2로 증축도 진행'
    ),
    "13:361:0": '"조정"-관직과 위신-',
    "13:362:0": (
        "조정에 금전을 헌상하면 관직을 얻고 위신을 높일 수 있습니다.\n"
        "\n"
        "【조정】\n"
        "·매달 금전을 헌상해 신용을 100으로 만들면 관직을 얻는다\n"
        "·현재보다 한 등급 높은 관직을 얻어 세력의 위신이 높아진다"
    ),
    "13:363:0": (
        "관직을 얻어 위신이 높아지면 여러 이점이 생깁니다.\n"
        "\n"
        "【위신을 높이는 이점】\n"
        "·정책을 발령할 수 있다\n"
        "·상대보다 위신이 높으면 침공한 적병이 위축되어 유리하게 싸울 수 있다\n"
        "·자신보다 위신이 낮은 세력과의 외교가 유리해진다"
    ),
    "13:364:0": '"다른 세력의 친선 제안"',
    "13:365:0": (
        "다른 세력도 전국시대의 난세를 살아남기 위해 외교를 펼칩니다.\n"
        "친선을 승낙하면\n"
        "훗날 요구에 응해야 하지만 그 대가로 금전을 받을 수 있습니다.\n"
        "\n"
        "【친선 승낙 후】\n"
        "·친선을 승낙한 뒤 기간 중에는 매달 금전 수입을 얻는다\n"
        "·기간이 끝나면 필요할 때 약속한 내용을 대가로 요구받는다\n"
        "·약속을 거부하면 상대의 신용과 주변 세력의 외교 자세가 악화된다"
    ),
}

VISIBLE_RECORD_IDS = set(range(342, 366)).difference({355})
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 342 <= base_record_id <= 344:
        return base_record_id + 24
    if 345 <= base_record_id <= 346:
        return base_record_id + 29
    if base_record_id == 347:
        return base_record_id + 30
    if base_record_id == 348:
        return base_record_id + 31
    if 349 <= base_record_id <= 365:
        return base_record_id + 32
    raise RuntimeError(f"segment 761 record has no configured PK mapping: {base_record_id}")


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


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
    expected_divergences = {"JP": {365}, "SC": set(), "TC": set()}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(342, 366)
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
        if divergences != expected_divergences[language]:
            raise RuntimeError(
                f"segment 761 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for blank_record_id in (355,):
        source_literal = ENGINE.parse_record_literals(source_records[(13, blank_record_id)])[0]
        current_literal = ENGINE.parse_record_literals(current_records[(13, blank_record_id)])[0]
        if source_literal.text or current_literal.text:
            raise RuntimeError(f"13:{blank_record_id} blank contract drifted")
    for left, right in ((342, 339), (345, 238), (349, 242)):
        if source_records[(13, left)].data != source_records[(13, right)].data:
            raise RuntimeError(f"pristine Base raw duplicate 13:{left}=13:{right} drifted")
        if current_records[(13, left)].data != current_records[(13, right)].data:
            raise RuntimeError(f"current Base raw duplicate 13:{left}=13:{right} drifted")
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
    if TRANSLATIONS["13:342:0"] != '"조작 설명"':
        raise RuntimeError("13:342 must remain synchronized with raw duplicate 13:339")
    if TRANSLATIONS["13:345:0"] != '"군단"' or TRANSLATIONS["13:349:0"] != '"외교"':
        raise RuntimeError("segment 761 prior exact title translation drifted")
    assert_available_duplicate_decision("13:339:0", TRANSLATIONS["13:342:0"])
    assert_available_duplicate_decision("13:238:0", TRANSLATIONS["13:345:0"])
    assert_available_duplicate_decision("13:242:0", TRANSLATIONS["13:349:0"])
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "고쇼",
        "역직",
        "관직",
        "막부",
        "정이대장군",
        "조정",
        "지행",
        "노동력",
        "제도 개신",
        "본거지",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 761 required terminology drifted")
    if "제도개신" in joined or "노력" in joined or "시동" in joined:
        raise RuntimeError("segment 761 retains a forbidden legacy term")
    if len(TRANSLATIONS) != 23 or {int(key.split(":")[1]) for key in TRANSLATIONS} != VISIBLE_RECORD_IDS:
        raise RuntimeError("segment 761 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S761",
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
